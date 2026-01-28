"""
Support API Routes (REST + WebSockets)
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from app.middleware.auth import get_current_user, verify_jwt_token_safe
from app.repositories.ticket import TicketRepository
from app.repositories.support_message import SupportMessageRepository
from app.dependencies import get_ticket_repo, get_message_repo
from app.schemas.support import CreateTicketRequest, TicketResponse, MessageResponse
from app.models.support_message import SenderRole
from app.models.ticket import TicketStatus

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
