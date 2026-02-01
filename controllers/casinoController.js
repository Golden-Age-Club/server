const pgProviderService = require('../services/pgProviderService');
const User = require('../models/User');

// @desc    Update webhook URL
// @route   POST /api/casino/pg/webhook-update
// @access  Public (or Protected)
const updateWebhookUrl = async (req, res) => {
  try {
    let { webhook_url } = req.body;
    
    if (!webhook_url) {
      // Construct default if not provided, similar to Python logic
      if (process.env.WEBHOOK_URL) {
          // Assuming WEBHOOK_URL is like .../api/webhook/ccpayment
          // We might want .../api/webhook/unified or similar
          // For now, let's require it or use a default base
          const baseUrl = process.env.WEBHOOK_URL.split('/api/webhook')[0];
          webhook_url = `${baseUrl}/api/webhook/unified`; 
      } else {
         return res.status(400).json({ message: "webhook_url is required" });
      }
    }

    const data = await pgProviderService.updateWebhookUrl(webhook_url); // You need to implement this in service if not already
    res.json(data);
  } catch (error) {
    console.error("Error updating webhook URL", error);
    res.status(502).json({ message: "Failed to update webhook URL" });
  }
};

// @desc    Get PG Options
// @route   GET /api/casino/pg/options
// @access  Public
const getPgOptions = async (req, res) => {
  try {
    const data = await pgProviderService.getOptions();
    res.json(data);
  } catch (error) {
    console.error("Error fetching PG options", error);
    res.status(502).json({ message: "Failed to fetch PG options" });
  }
};

// @desc    Get PG Games
// @route   GET /api/casino/pg/games
// @access  Public
const getPgGames = async (req, res) => {
  try {
    const page = Math.max(1, parseInt(req.query.page) || 1);
    const limit = Math.max(1, parseInt(req.query.limit) || 10);
    const providerId = req.query.provider_id;
    const search = req.query.search;
    const offset = req.query.offset;

    const data = await pgProviderService.getGames(page, limit, providerId, search, offset)
    res.json(data);
  } catch (error) {
    console.error("Error fetching PG games", error);
    res.status(502).json({ message: "Failed to fetch PG games" });
  }
};

// @desc    Play Game
// @route   POST /api/casino/pg/play
// @access  Private
const playGame = async (req, res) => {
  try {
    const { game_id, exit_url } = req.body;
    const user = req.user; // From auth middleware

    console.log(`[CasinoController] Play game request - User: ${user._id}, Game: ${game_id}`);

    if (!game_id) {
      return res.status(400).json({ message: "game_id is required" });
    }

    // Generate player token (valid for 12 hours)
    // We can use the user's ID or a specific session token
    // Python code: sub=user_id, exp=12h
    // In Node, we can just use the user ID as player_id and a generated token
    
    // For simplicity, let's use a signed JWT or just a random string if we store it
    // But the provider expects us to validate it later via webhook.
    // So we should probably sign something we can verify.
    // Let's use the existing JWT_SECRET_KEY to sign a game token.
    const jwt = require('jsonwebtoken');
    const playerToken = jwt.sign(
      { sub: user._id.toString(), type: 'game_session' }, 
      process.env.JWT_SECRET_KEY, 
      { expiresIn: '12h' }
    );

    // Construct URLs
    // API_HOST/PORT might be internal, use ALLOWED_ORIGINS[0] or explicit PUBLIC_URL
    const publicUrl = process.env.ALLOWED_ORIGINS ? process.env.ALLOWED_ORIGINS.split(',')[0] : 'http://localhost:5173';
    const walletUrl = `${publicUrl}/wallet`; // Frontend wallet page
    const actualExitUrl = exit_url || `${publicUrl}/`;

    const data = await pgProviderService.launchGame(
      game_id,
      user._id.toString(),
      playerToken,
      user.language_code || 'en',
      'USD', // Default currency for now, or user.currency
      actualExitUrl,
      walletUrl
    );

    res.json(data);

  } catch (error) {
    console.error("Error launching game:", error.message);
    if (error.response) {
       console.error("Provider error details:", JSON.stringify(error.response.data, null, 2));
    }
    res.status(502).json({ 
      message: "Failed to launch game",
      details: error.message 
    });
  }
};

module.exports = {
  updateWebhookUrl,
  getPgOptions,
  getPgGames,
  playGame
};
