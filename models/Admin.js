const mongoose = require('mongoose');

const adminSchema = new mongoose.Schema({
  email: {
    type: String,
    required: true,
    unique: true,
    trim: true,
    lowercase: true
  },
  password_hash: {
    type: String,
    required: true
  },
  first_name: {
    type: String,
    required: true
  },
  last_name: {
    type: String,
    required: true
  },
  title: {
    type: String,
    default: 'Admin'
  },
  phone: {
    type: String
  },
  location: {
    type: String
  },
  avatar: {
    type: String
  },
  verified: {
    type: Boolean,
    default: false
  },
  bio: {
    type: String
  },
  role: {
    type: String,
    enum: ['super_admin', 'admin', 'moderator'],
    default: 'admin'
  },
  permissions: {
    type: [String],
    default: []
  },
  last_login: {
    type: Date
  }
}, {
  timestamps: { createdAt: 'created_at', updatedAt: 'updated_at' }
});

// Virtual for full name
adminSchema.virtual('name').get(function() {
  return `${this.first_name} ${this.last_name}`;
});

const Admin = mongoose.model('Admin', adminSchema);

module.exports = Admin;
