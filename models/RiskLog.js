const mongoose = require('mongoose');

const riskLogSchema = new mongoose.Schema({
  user_id: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  username: {
    type: String
  },
  rule_name: {
    type: String,
    required: true
  },
  severity: {
    type: String,
    enum: ['Low', 'Medium', 'High'],
    required: true
  },
  details: {
    type: String
  },
  status: {
    type: String,
    enum: ['active', 'investigating', 'resolved'],
    default: 'active'
  },
  action_taken: {
    type: String,
    enum: ['none', 'freeze', 'restrict', 'warn'],
    default: 'none'
  }
}, {
  timestamps: { createdAt: 'created_at', updatedAt: 'updated_at' }
});

const RiskLog = mongoose.model('RiskLog', riskLogSchema);

module.exports = RiskLog;
