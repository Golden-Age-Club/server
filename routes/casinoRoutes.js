const express = require('express');
const router = express.Router();
const { 
  updateWebhookUrl, 
  getPgOptions, 
  getPgGames, 
  playGame,
  getAdminProviders,
  updateProviderStatus
} = require('../controllers/casinoController');
const { protect } = require('../middleware/authMiddleware');

router.post('/pg/webhook-update', updateWebhookUrl); // Maybe protect this? Python said "Optionally require auth"
router.get('/pg/options', getPgOptions);
router.get('/pg/games', getPgGames);
router.post('/pg/play', protect, playGame);

// Admin routes for provider management
router.get('/pg/providers/admin', protect, getAdminProviders);
router.post('/pg/providers/status', protect, updateProviderStatus);

module.exports = router;
