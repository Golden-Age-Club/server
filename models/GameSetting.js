const mongoose = require('mongoose');

const gameSettingSchema = new mongoose.Schema({
  game_id: {
    type: String,
    required: true,
    unique: true
  },
  status: {
    type: String,
    enum: ['enabled', 'disabled'],
    default: 'enabled'
  },
  updated_at: {
    type: Date,
    default: Date.now
  }
});

const GameSetting = mongoose.model('GameSetting', gameSettingSchema);

module.exports = GameSetting;
