const express = require('express');
const router = express.Router();
const { getRecentTransactions, getMyTransactions } = require('../controllers/transactionController');
const { protect } = require('../middleware/authMiddleware');

router.get('/recent', getRecentTransactions);
router.get('/me', protect, getMyTransactions);

module.exports = router;
