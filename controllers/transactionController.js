const { Transaction } = require('../models/Transaction');
const User = require('../models/User');

// @desc    Get recent transactions
// @route   GET /api/transactions/recent
// @access  Public
const getRecentTransactions = async (req, res) => {
  // ... existing logic ...
};

// @desc    Get authenticated user's transactions
// @route   GET /api/transactions/me
// @access  Private
const getMyTransactions = async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 20;
    const skip = (page - 1) * limit;
    const type = req.query.type; // 'deposit', 'withdrawal', 'game_win', 'game_bet'

    const query = { user_id: req.user._id };

    // Filter by type if provided
    if (type) {
      if (type === 'deposit') {
        query.type = 'deposit';
      } else if (type === 'withdrawal') {
        query.type = 'withdrawal';
      } else if (type === 'game') {
        query.type = { $in: ['game_bet', 'game_win', 'game_refund'] };
      }
    }

    const total = await Transaction.countDocuments(query);
    const transactions = await Transaction.find(query)
      .sort({ created_at: -1 })
      .skip(skip)
      .limit(limit)
      .lean();

    res.json({
      transactions,
      pagination: {
        page,
        limit,
        total,
        pages: Math.ceil(total / limit)
      }
    });

  } catch (error) {
    console.error("Get my transactions error", error);
    res.status(500).json({ message: "Server error" });
  }
};

module.exports = {
  getRecentTransactions,
  getMyTransactions
};
