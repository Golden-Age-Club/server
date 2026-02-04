const express = require('express');
const router = express.Router();
const { getRecentTransactions, getGameHistory } = require('../controllers/transactionController');

router.get('/recent', getRecentTransactions);
router.get('/history', getGameHistory);

module.exports = router;
