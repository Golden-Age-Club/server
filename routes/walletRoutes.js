const express = require('express');
const router = express.Router();
const { createDeposit, createWithdrawal } = require('../controllers/walletController');
const { protect } = require('../middleware/authMiddleware');

router.post('/deposit', protect, createDeposit);
router.post('/withdraw', protect, createWithdrawal);

module.exports = router;
