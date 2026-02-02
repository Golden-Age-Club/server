const { Transaction } = require('../models/Transaction');
const GameSetting = require('../models/GameSetting');
const pgProviderService = require('../services/pgProviderService');
const User = require('../models/User');

// @desc    Get Bet Records
// @route   GET /api/admin/bets
// @access  Private (Admin)
exports.getBets = async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const search = req.query.search || '';

    const query = {
      type: { $in: ['game_bet', 'game_win', 'game_refund'] }
    };

    if (search) {
      // Search by Order ID, User (username), or Game ID (if stored)
      // Since username is in User model, we might need aggregation or two-step search
      // Let's try to find users first
      const users = await User.find({ username: { $regex: search, $options: 'i' } }).select('_id');
      const userIds = users.map(u => u._id);

      query.$or = [
        { merchant_order_id: { $regex: search, $options: 'i' } },
        { user_id: { $in: userIds } },
        { game_id: { $regex: search, $options: 'i' } } // If game_id is string
      ];
    }

    const total = await Transaction.countDocuments(query);
    const transactions = await Transaction.find(query)
      .populate('user_id', 'username')
      .sort({ created_at: -1 })
      .skip((page - 1) * limit)
      .limit(limit);

    // Fetch all games for name mapping (cached)
    let gameMap = {};
    try {
        const allGames = await pgProviderService._fetchGamesFromProvider();
        allGames.forEach(g => {
            gameMap[g.game_id] = g.name || g.title;
        });
    } catch (e) {
        console.warn("Failed to fetch games for mapping", e);
    }

    // Format for frontend
    const formattedBets = transactions.map(tx => {
      let result = 'pending';
      let winAmount = 0;
      
      // Basic inference
      if (tx.type === 'game_win') {
        result = 'win';
        winAmount = tx.amount;
      } else if (tx.type === 'game_bet') {
        result = 'bet'; // Display as 'bet' type
      }

      return {
        id: tx.merchant_order_id,
        userId: tx.user_id?._id,
        username: tx.user_id?.username || 'Unknown',
        game: gameMap[tx.game_id] || tx.game_id, // Use name if available
        amount: tx.amount,
        balanceAfter: tx.balance_after,
        win: winAmount,
        result: tx.type === 'game_win' ? 'win' : (tx.type === 'game_bet' ? 'bet' : tx.type),
        date: tx.created_at,
        roundId: tx.round_id,
        details: tx.bet_info // Pass raw info
      };
    });

    res.json({
      bets: formattedBets,
      page,
      pages: Math.ceil(total / limit),
      total
    });

  } catch (error) {
    console.error('Error fetching bets:', error);
    res.status(500).json({ message: 'Failed to fetch bets' });
  }
};

// @desc    Get Games Management Data
// @route   GET /api/admin/games
// @access  Private (Admin)
exports.getGames = async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 20;
    const search = req.query.search || '';

    const data = await pgProviderService.getGamesWithStats(page, limit, search);
    res.json(data);
  } catch (error) {
    console.error('Error fetching games management:', error);
    res.status(500).json({ message: 'Failed to fetch games' });
  }
};

// @desc    Toggle Game Status
// @route   POST /api/admin/games/toggle
// @access  Private (Admin)
exports.toggleGame = async (req, res) => {
  try {
    const { gameId, status } = req.body;

    if (!gameId || !status) {
      return res.status(400).json({ message: 'Game ID and status are required' });
    }

    if (!['enabled', 'disabled'].includes(status)) {
        return res.status(400).json({ message: 'Invalid status' });
    }

    await GameSetting.findOneAndUpdate(
      { game_id: gameId },
      { status: status, updated_at: new Date() },
      { upsert: true, new: true }
    );

    res.json({ message: `Game ${gameId} ${status}` });
  } catch (error) {
    console.error('Error toggling game status:', error);
    res.status(500).json({ message: 'Failed to update game status' });
  }
};
