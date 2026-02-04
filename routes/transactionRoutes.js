const express = require('express');
const router = express.Router();
const { getRecentTransactions, getGameHistory , getMyTransactions} = require('../controllers/transactionController');
const { protect } = require('../middleware/authMiddleware');

router.get('/history', getGameHistory);
router.get('/recent', getRecentTransactions);
router.get('/me', protect, getMyTransactions);

module.exports = router;
