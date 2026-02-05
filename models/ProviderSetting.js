const mongoose = require('mongoose');

const providerSettingSchema = new mongoose.Schema({
  provider_id: {
    type: String,
    required: true,
    unique: true
  },
  provider_name: {
    type: String
  },
  status: {
    type: String,
    enum: ['enabled', 'disabled'],
    default: 'enabled'
  },
  rtp: {
    type: Number,
    default: 95
  },
  updated_at: {
    type: Date,
    default: Date.now
  }
});

const ProviderSetting = mongoose.model('ProviderSetting', providerSettingSchema);

module.exports = ProviderSetting;
