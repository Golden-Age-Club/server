const express = require('express');
const router = express.Router();
const { 
  updateWebhookUrl, 
  getPgOptions, 
  getPgGames, 
  playGame 
} = require('../controllers/casinoController');
const { protect } = require('../middleware/authMiddleware');

router.post('/pg/webhook-update', updateWebhookUrl); // Maybe protect this? Python said "Optionally require auth"
router.get('/pg/options', getPgOptions);
router.get('/pg/games', getPgGames);
router.post('/pg/play', protect, playGame);

module.exports = router;
