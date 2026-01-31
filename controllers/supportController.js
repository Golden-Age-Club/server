const Ticket = require('../models/Ticket');
const SupportMessage = require('../models/SupportMessage');

// Create a new ticket
exports.createTicket = async (req, res) => {
  try {
    const { content } = req.body;
    const user = req.user;

    if (!content) {
      return res.status(400).json({ message: 'Content is required' });
    }

    // 1. Create Ticket
    const ticket = new Ticket({
      user_id: user._id,
      status: 'open' // Default status
    });
    await ticket.save();

    // 2. Add Initial Message
    const message = new SupportMessage({
      ticket_id: ticket._id,
      sender_id: user._id,
      sender_role: 'user', // Enum: 'user', 'admin'
      content: content
    });
    await message.save();

    // 3. Return Ticket
    res.status(201).json(ticket);
  } catch (error) {
    console.error('Create ticket error:', error);
    res.status(500).json({ message: error.message });
  }
};

// List all tickets for the current user
exports.listTickets = async (req, res) => {
  try {
    const user = req.user;
    const tickets = await Ticket.find({ user_id: user._id }).sort({ created_at: -1 });
    res.json(tickets);
  } catch (error) {
    console.error('List tickets error:', error);
    res.status(500).json({ message: error.message });
  }
};

// Get chat history for a specific ticket
exports.getTicketHistory = async (req, res) => {
  try {
    const { ticket_id } = req.params;
    const user = req.user;

    const ticket = await Ticket.findById(ticket_id);
    if (!ticket) {
      return res.status(404).json({ message: 'Ticket not found' });
    }

    // Access Control: User can only see own tickets
    // Assuming req.user._id is an ObjectId, we compare string representations
    if (ticket.user_id.toString() !== user._id.toString() && !user.is_admin) {
      return res.status(403).json({ message: 'Access denied' });
    }

    const messages = await SupportMessage.find({ ticket_id }).sort({ created_at: 1 });
    res.json(messages);
  } catch (error) {
    console.error('Get ticket history error:', error);
    res.status(500).json({ message: error.message });
  }
};
