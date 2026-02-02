const mongoose = require('mongoose');

const riskRuleSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    unique: true
  },
  description: {
    type: String,
    required: true
  },
  severity: {
    type: String,
    enum: ['Low', 'Medium', 'High'],
    default: 'Medium'
  },
  triggered_count: {
    type: Number,
    default: 0
  },
  last_triggered_at: {
    type: Date
  },
  is_active: {
    type: Boolean,
    default: true
  }
}, {
  timestamps: { createdAt: 'created_at', updatedAt: 'updated_at' }
});

const RiskRule = mongoose.model('RiskRule', riskRuleSchema);

module.exports = RiskRule;
