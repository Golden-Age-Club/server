const mongoose = require('mongoose');

const promotionSchema = new mongoose.Schema({
  title: { type: String, required: true },
  description: { type: String },
  type: { 
    type: String, 
    enum: ['deposit_match', 'free_spins', 'cashback', 'referral', 'manual'], 
    required: true 
  },
  value: { type: Number, required: true }, // e.g., 100 for 100%, 50 for 50 spins
  currency: { type: String, default: 'USD' },
  min_deposit: { type: Number, default: 0 },
  max_bonus: { type: Number }, // Max amount obtainable
  wager_multiplier: { type: Number, default: 30 }, // e.g., 30x
  valid_days: { type: Number, default: 30 }, // How long the bonus lasts
  start_date: { type: Date },
  end_date: { type: Date },
  is_active: { type: Boolean, default: true },
  applicable_games: [{ type: String }], // Game IDs or Categories
  created_at: { type: Date, default: Date.now },
  updated_at: { type: Date, default: Date.now }
});

promotionSchema.pre('save', function(next) {
  this.updated_at = Date.now();
  next();
});

module.exports = mongoose.model('Promotion', promotionSchema);
