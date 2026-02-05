const express = require('express');
const router = express.Router();
const { createDeposit, createWithdrawal, getBalance, validateWithdrawAddress, getWithdrawFee } = require('../controllers/walletController');
const { protect } = require('../middleware/authMiddleware');

router.get('/balance', protect, getBalance);
router.get('/withdraw-fee', protect, getWithdrawFee);
router.post('/deposit', protect, createDeposit);
router.post('/withdraw', protect, createWithdrawal);
router.post('/validate-address', protect, validateWithdrawAddress);

module.exports = router;
