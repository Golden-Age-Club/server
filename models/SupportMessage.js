const mongoose = require('mongoose');

const SenderRole = {
  USER: 'user',
  ADMIN: 'admin'
};

const supportMessageSchema = new mongoose.Schema({
  ticket_id: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Ticket',
    required: true
  },
  sender_id: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User', // Or Admin if you have separate collection, but usually User for both or generic ID
    required: true
  },
  sender_role: {
    type: String,
    enum: Object.values(SenderRole),
    required: true
  },
  content: {
    type: String,
    required: true,
    minlength: 1,
    maxlength: 4000
  }
}, {
  timestamps: { createdAt: 'created_at', updatedAt: false } // Only createdAt
});

supportMessageSchema.index({ ticket_id: 1, created_at: 1 });

const SupportMessage = mongoose.model('SupportMessage', supportMessageSchema);

module.exports = {
  SupportMessage,
  SenderRole
};
