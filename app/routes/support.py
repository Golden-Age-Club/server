"""
Support API Routes (REST + WebSockets)
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from app.middleware.auth import get_current_user, verify_jwt_token_safe
from app.repositories.ticket import TicketRepository
from app.repositories.support_message import SupportMessageRepository
from app.dependencies import get_ticket_repo, get_message_repo
from app.schemas.support import CreateTicketRequest, TicketResponse, MessageResponse
from app.models.support_message import SenderRole
from app.models.ticket import TicketStatus
from app.services.ws_manager import manager

router = APIRouter(prefix="/api/support", tags=["support"])


# --- REST API ---

@router.post("/tickets", response_model=TicketResponse)
async def create_ticket(
    request: CreateTicketRequest,
    user: dict = Depends(get_current_user),
    ticket_repo: TicketRepository = Depends(get_ticket_repo),
    msg_repo: SupportMessageRepository = Depends(get_message_repo)
):
    """
    User creates a new ticket.
    Must include an initial message.
    """
    # 1. Create Ticket
    user_id = str(user["_id"])
    ticket_id = await ticket_repo.create(user_id)
    
    # 2. Add Initial Message
    await msg_repo.create(
        ticket_id=ticket_id, 
        sender_id=user_id, 
        role=SenderRole.USER.value, 
        content=request.content
    )
    
    # 3. Return Ticket
    return await ticket_repo.get_by_id(ticket_id)





@router.get("/tickets", response_model=List[TicketResponse])
async def list_tickets(
    user: dict = Depends(get_current_user),
    ticket_repo: TicketRepository = Depends(get_ticket_repo)
):
    """List all tickets for the current user"""
    return await ticket_repo.get_user_tickets(str(user["_id"]))


@router.get("/tickets/{ticket_id}/messages", response_model=List[MessageResponse])
async def get_ticket_history(
    ticket_id: str,
    user: dict = Depends(get_current_user),
    ticket_repo: TicketRepository = Depends(get_ticket_repo),
    msg_repo: SupportMessageRepository = Depends(get_message_repo)
):
    """Get chat history for a specific ticket"""
    ticket = await ticket_repo.get_by_id(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    # Access Control: User can only see own; Admin can see all
    # Note: 'is_admin' logic depends on your user model. 
    # For MVP we assume users only access their own.
    if ticket["user_id"] != str(user["_id"]) and not user.get("is_admin"):
         raise HTTPException(status_code=403, detail="Access denied")
         
    return await msg_repo.get_history(ticket_id)


# --- WEBSOCKET CHAT ---

@router.websocket("/ws/{ticket_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    ticket_id: str,
    token: str = Query(...),
    ticket_repo: TicketRepository = Depends(get_ticket_repo),
    msg_repo: SupportMessageRepository = Depends(get_message_repo)
):
    """
    Real-time Chat WebSocket
    """
    # 1. Authenticate (WebSockets don't use HTTP headers, so params used)
    # This is simplified validation
    from app.config import get_settings
    settings = get_settings()
    
    user = None
    is_admin_bypass = False
    
    # Check Admin Bypass Secret
    if token == settings.ADMIN_WS_SECRET:
        is_admin_bypass = True
        user = {"_id": "admin", "username": "Support Agent", "is_staff": True}
    else:
        try:
            user = await verify_jwt_token_safe(token) 
        except:
            pass
        
    if not user:
        await websocket.close(code=1008) # Policy Violation (Auth)
        return

    # 2. Access Control
    ticket = await ticket_repo.get_by_id(ticket_id)
    if not ticket:
        await websocket.close(code=1000)
        return
        
    # Check if user owns ticket or is admin owner
    # Simplification: Assume 'is_superuser' or 'is_staff' flag exists or check ID
    is_admin = user.get("is_staff") or user.get("is_superuser")
    if ticket["user_id"] != str(user["_id"]) and not is_admin:
        await websocket.close(code=1000)
        return

    # 3. Connect
    await manager.connect(ticket_id, websocket)

    try:
        while True:
            # 4. Receive Message
            data = await websocket.receive_json()
            # Expected: {"content": "hello"}
            content = data.get("content", "").strip()
            
            if not content:
                continue

            # 5. Check if Ticket is Resolved (ReadOnly)
            # Fetch latest status
            current_ticket = await ticket_repo.get_by_id(ticket_id)
            if current_ticket["status"] == TicketStatus.RESOLVED:
                # Optionally send error back or just ignore
                continue

            # 6. Save to DB
            sender_id = str(user["_id"])
            role = SenderRole.ADMIN.value if is_admin else SenderRole.USER.value
            
            message_doc = await msg_repo.create(ticket_id, sender_id, role, content)
            
            # Touch ticket updated_at
            await ticket_repo.touch(ticket_id)

            # 7. Broadcast
            response = {
                "_id": str(message_doc["_id"]),
                "sender_id": sender_id,
                "sender_role": role,
                "content": content,
                "created_at": message_doc["created_at"].isoformat()
            }
            await manager.broadcast(ticket_id, response)

    except WebSocketDisconnect:
        manager.disconnect(ticket_id, websocket)
