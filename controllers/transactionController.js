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

    res.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate, proxy-revalidate');
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

// @desc    Get game history (wins/losses)
// @route   GET /api/transactions/history
// @access  Public
const getGameHistory = async (req, res) => {
  try {
    const limit = parseInt(req.query.limit) || 50;
    const safeLimit = Math.min(Math.max(limit, 1), 100);

    // Only fetch 'game_win' transactions
    // In our system, 'game_win' with amount 0 is a loss, amount > 0 is a win
    const transactions = await Transaction.find({ type: 'game_win' })
      .sort({ created_at: -1 })
      .limit(safeLimit)
      .lean();

    const results = await Promise.all(transactions.map(async (tx) => {
      let username = "Player";
      if (tx.user_id) {
        try {
          const user = await User.findById(tx.user_id).select('username');
          if (user && user.username) {
            username = user.username;
          }
        } catch (err) {
          // Ignore error
        }
      }

      const amount = parseFloat(tx.amount);
      const isWin = amount > 0;

      return {
        transaction_id: tx._id,
        user_id: tx.user_id,
        username: username,
        amount: amount,
        currency: tx.currency || 'USD',
        type: isWin ? 'win' : 'lose', // derived type
        game_id: tx.game_id || "Unknown Game",
        timestamp: tx.created_at
      };
    }));

    res.json(results);

  } catch (error) {
    console.error("Get game history error", error);
    res.status(500).json({ message: "Server error" });
  }
};

module.exports = {
  getRecentTransactions,
  getGameHistory,
  getMyTransactions
};
