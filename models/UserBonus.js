const mongoose = require('mongoose');

const userBonusSchema = new mongoose.Schema({
  user_id: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
  promotion_id: { type: mongoose.Schema.Types.ObjectId, ref: 'Promotion' },
  promotion_title: { type: String }, // Snapshot of title in case promotion is deleted
  type: { type: String, required: true },
  amount: { type: Number, required: true }, // Current bonus balance
  initial_amount: { type: Number, required: true },
  wager_required: { type: Number, required: true }, // Total wager needed
  wager_remaining: { type: Number, required: true }, // Remaining wager
  status: { 
    type: String, 
    enum: ['active', 'completed', 'expired', 'forfeited', 'cancelled'], 
    default: 'active' 
  },
  expires_at: { type: Date },
  claimed_at: { type: Date, default: Date.now },
  completed_at: { type: Date }
});

module.exports = mongoose.model('UserBonus', userBonusSchema);
