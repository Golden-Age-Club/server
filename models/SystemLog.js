const mongoose = require('mongoose');

const systemLogSchema = new mongoose.Schema({
  admin_id: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Admin',
    required: true
  },
  action: {
    type: String,
    required: true
  },
  target: {
    type: String,
    required: true
  },
  details: {
    type: mongoose.Schema.Types.Mixed
  },
  ip_address: {
    type: String
  },
  user_agent: {
    type: String
  }
}, {
  timestamps: { createdAt: 'created_at', updatedAt: false }
});

const SystemLog = mongoose.model('SystemLog', systemLogSchema);

module.exports = SystemLog;
