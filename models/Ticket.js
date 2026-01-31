const mongoose = require('mongoose');

const TicketStatus = {
  OPEN: 'open',
  RESOLVED: 'resolved'
};

const ticketSchema = new mongoose.Schema({
  user_id: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  status: {
    type: String,
    enum: Object.values(TicketStatus),
    default: TicketStatus.OPEN,
    required: true
  }
}, {
  timestamps: { createdAt: 'created_at', updatedAt: 'updated_at' }
});

ticketSchema.index({ user_id: 1 });
ticketSchema.index({ status: 1 });

const Ticket = mongoose.model('Ticket', ticketSchema);

module.exports = {
  Ticket,
  TicketStatus
};
