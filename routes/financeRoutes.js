const express = require('express');
const router = express.Router();
const FinanceController = require('../controllers/financeController');
const { protectAdmin } = require('../middleware/adminMiddleware');

// Balances
router.get('/balances', protectAdmin, FinanceController.getUserBalances);

// Transactions (General, Deposits, Withdrawals via query param ?type=...)
router.get('/transactions', protectAdmin, FinanceController.getTransactions);

// Withdrawals Action
router.put('/withdrawals/:id', protectAdmin, FinanceController.updateWithdrawalStatus);

// Manual Adjustment
router.post('/adjust-balance', protectAdmin, FinanceController.adjustBalance);

module.exports = router;
