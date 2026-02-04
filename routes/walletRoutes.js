const express = require('express');
const router = express.Router();
const { createDeposit, createWithdrawal, getBalance } = require('../controllers/walletController');
const { protect } = require('../middleware/authMiddleware');

router.get('/balance', protect, getBalance);
router.post('/deposit', protect, createDeposit);
router.post('/withdraw', protect, createWithdrawal);

module.exports = router;
