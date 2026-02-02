const mongoose = require('mongoose');

const vipTierSchema = new mongoose.Schema({
  level: { 
    type: Number, 
    required: true, 
    unique: true 
  },
  name: { 
    type: String, 
    required: true 
  },
  min_deposit: { 
    type: Number, 
    default: 0 
  },
  min_bets: { 
    type: Number, 
    default: 0 
  },
  benefits: { 
    type: String 
  },
  color: { 
    type: String, 
    default: 'bg-gray-100 text-gray-800' 
  }
}, { 
  timestamps: { createdAt: 'created_at', updatedAt: 'updated_at' } 
});

module.exports = mongoose.model('VipTier', vipTierSchema);
