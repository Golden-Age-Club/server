const walletService = require('../services/walletService');

// Limits (USDT)
const MIN_DEPOSIT_AMOUNT = 10.0;
const MAX_DEPOSIT_AMOUNT = 100000.0;
const MIN_WITHDRAWAL_AMOUNT = 10.0;
const MAX_WITHDRAWAL_AMOUNT = 50000.0;

// @desc    Create Deposit
// @route   POST /api/wallet/deposit
// @access  Private
const createDeposit = async (req, res) => {
  try {
    const { amount, currency = 'USDT', return_url } = req.body;
    const user = req.user;

    // Validate amount
    if (amount < MIN_DEPOSIT_AMOUNT) {
      return res.status(400).json({ message: `Minimum deposit amount is ${MIN_DEPOSIT_AMOUNT} USDT` });
    }
    if (amount > MAX_DEPOSIT_AMOUNT) {
      return res.status(400).json({ message: `Maximum deposit amount is ${MAX_DEPOSIT_AMOUNT} USDT` });
    }

    const transaction = await walletService.createDeposit(
      user._id,
      amount,
      currency,
      return_url
    );

    res.json({
      transaction_id: transaction._id,
      user_id: transaction.user_id,
      type: transaction.type,
      amount: transaction.amount,
      currency: transaction.currency,
      status: transaction.status,
      created_at: transaction.created_at,
      payment_url: transaction.payment_url,
      payment_address: transaction.payment_address,
      merchant_order_id: transaction.merchant_order_id
    });

  } catch (error) {
    console.error("Deposit error", error);
    res.status(500).json({ message: error.message || "Server error" });
  }
};

// @desc    Create Withdrawal
// @route   POST /api/wallet/withdraw
// @access  Private
const createWithdrawal = async (req, res) => {
  try {
    const { amount, wallet_address, currency = 'USDT' } = req.body;
    const user = req.user;

    // Validate amount
    if (amount < MIN_WITHDRAWAL_AMOUNT) {
      return res.status(400).json({ message: `Minimum withdrawal amount is ${MIN_WITHDRAWAL_AMOUNT} USDT` });
    }
    if (amount > MAX_WITHDRAWAL_AMOUNT) {
      return res.status(400).json({ message: `Maximum withdrawal amount is ${MAX_WITHDRAWAL_AMOUNT} USDT` });
    }

    if (!wallet_address) {
      return res.status(400).json({ message: "Wallet address is required" });
    }

    const transaction = await walletService.createWithdrawal(
      user._id,
      amount,
      wallet_address,
      currency
    );

    res.json({
      transaction_id: transaction._id,
      user_id: transaction.user_id,
      type: transaction.type,
      amount: transaction.amount,
      currency: transaction.currency,
      status: transaction.status,
      created_at: transaction.created_at,
      merchant_order_id: transaction.merchant_order_id
    });

  } catch (error) {
    console.error("Withdrawal error", error);
    res.status(400).json({ message: error.message || "Server error" }); // 400 likely for insufficient funds
  }
};

module.exports = {
  createDeposit,
  createWithdrawal
};
