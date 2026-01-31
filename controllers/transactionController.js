const { Transaction } = require('../models/Transaction');
const User = require('../models/User');

// @desc    Get recent transactions
// @route   GET /api/transactions/recent
// @access  Public
const getRecentTransactions = async (req, res) => {
  try {
    const limit = parseInt(req.query.limit) || 50;
    const safeLimit = Math.min(Math.max(limit, 1), 100);

    const transactions = await Transaction.find({})
      .sort({ created_at: -1 })
      .limit(safeLimit)
      .lean(); // Convert to plain JS objects

    // Enrich with usernames
    // Note: In high traffic, use aggregation or cache. For MVP, this is fine.
    const results = await Promise.all(transactions.map(async (tx) => {
      let username = "Player";
      if (tx.user_id) {
        try {
          const user = await User.findById(tx.user_id).select('username');
          if (user && user.username) {
            username = user.username;
          }
        } catch (err) {
          // Ignore error, keep default
        }
      }

      // Map type for frontend display
      let mappedType = tx.type;
      if (tx.type === 'game_win') mappedType = 'win';
      else if (tx.type === 'game_bet') mappedType = 'bet';
      else if (tx.type === 'game_refund') mappedType = 'refund';

      return {
        transaction_id: tx._id,
        user_id: tx.user_id,
        username: username,
        amount: tx.amount,
        currency: tx.currency || 'USD',
        type: mappedType,
        game_id: tx.game_id || "Unknown Game", // Make sure game_id is in schema if needed
        timestamp: tx.created_at
      };
    }));

    res.json(results);

  } catch (error) {
    console.error("Get recent transactions error", error);
    res.status(500).json({ message: "Server error" });
  }
};

module.exports = {
  getRecentTransactions
};
