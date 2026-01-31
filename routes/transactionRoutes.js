const express = require('express');
const router = express.Router();
const { getRecentTransactions } = require('../controllers/transactionController');

router.get('/recent', getRecentTransactions);

module.exports = router;
