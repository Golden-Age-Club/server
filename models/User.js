const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
  telegram_id: {
    type: Number,
    required: false, // Optional as per Python model, but usually unique index if present
    unique: true,
    sparse: true
  },
  email: {
    type: String,
    required: false,
    unique: true,
    sparse: true
  },
  password_hash: {
    type: String,
    required: false
  },
  username: {
    type: String,
    required: false
  },
  first_name: {
    type: String,
    required: false
  },
  last_name: {
    type: String,
    required: false
  },
  photo_url: {
    type: String,
    required: false
  },
  language_code: {
    type: String,
    default: 'en'
  },
  balance: {
    type: Number,
    default: 0.0
  },
  is_active: {
    type: Boolean,
    default: true
  },
  is_premium: {
    type: Boolean,
    default: false
  },
  total_bet: {
    type: Number,
    default: 0.0
  },
  total_won: {
    type: Number,
    default: 0.0
  },
  best_win: {
    type: Number,
    default: 0.0
  }
}, {
  timestamps: { createdAt: 'created_at', updatedAt: 'updated_at' } // Map to snake_case to match Python
});

const User = mongoose.model('User', userSchema);

module.exports = User;
