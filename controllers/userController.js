const User = require('../models/User');

// @desc    Get top users sorted by total winnings
// @route   GET /api/users/top-users
// @access  Public
const getTopUsers = async (req, res) => {
  try {
    const limit = parseInt(req.query.limit) || 100;
    
    // Validate limit
    if (limit < 1 || limit > 100) {
      return res.status(400).json({ message: 'Limit must be between 1 and 100' });
    }

    // Find users sorted by total_won descending
    // Note: In a real app, you might want to project only necessary fields
    const users = await User.find({})
      .sort({ total_won: -1 })
      .limit(limit)
      .select('telegram_id username first_name last_name total_won best_win photo_url');

    res.json(users);
  } catch (error) {
    console.error('Get top users error:', error);
    res.status(500).json({ message: 'Server error' });
  }
};

// @desc    Get current user profile
// @route   GET /api/users/me
// @access  Private
const getMe = async (req, res) => {
  try {
    // req.user is set by auth middleware
    const user = await User.findById(req.user._id);
    if (user) {
      res.json(user);
    } else {
      res.status(404).json({ message: 'User not found' });
    }
  } catch (error) {
    console.error('Get me error:', error);
    res.status(500).json({ message: 'Server error' });
  }
};

module.exports = {
  getTopUsers,
  getMe
};
