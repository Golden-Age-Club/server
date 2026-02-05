const walletService = require('../services/walletService');
const SystemSetting = require('../models/SystemSetting');

// Default Limits (USDT) - Fallback if not in DB
const DEFAULTS = {
  MIN_DEPOSIT: 0.0001,
  MAX_DEPOSIT: 100000.0,
  MIN_WITHDRAWAL: 0.0001,
  MAX_WITHDRAWAL: 50000.0
};

// Helper to get limit from SystemSetting
const getLimit = async (key, defaultValue, label, description) => {
  try {
    let setting = await SystemSetting.findOne({ key });
    if (!setting) {
      // Lazy init: Create if not exists so Admin sees it
      setting = await SystemSetting.create({
        key,
        value: defaultValue,
        label,
        category: 'payment',
        description,
        is_public: true
      });
    }
    return parseFloat(setting.value);
  } catch (err) {
    console.error(`Error fetching limit ${key}:`, err);
    return defaultValue;
  }
};

// @desc    Create Deposit
// @route   POST /api/wallet/deposit
// @access  Private
const createDeposit = async (req, res) => {
  try {
    const { amount, currency = 'USDT', return_url } = req.body;
    const user = req.user;

    // Get Dynamic Limits
    const minDeposit = await getLimit('payment_min_deposit', DEFAULTS.MIN_DEPOSIT, 'Min Deposit Amount (USDT)', 'Minimum allowed deposit amount');
    const maxDeposit = await getLimit('payment_max_deposit', DEFAULTS.MAX_DEPOSIT, 'Max Deposit Amount (USDT)', 'Maximum allowed deposit amount');

    // Validate amount
    if (amount < minDeposit) {
      return res.status(400).json({ message: `Minimum deposit amount is ${minDeposit} USDT` });
    }
    if (amount > maxDeposit) {
      return res.status(400).json({ message: `Maximum deposit amount is ${maxDeposit} USDT` });
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

    // Check for risk status
    if (user.risk_level === 'high') {
      return res.status(403).json({ message: "Withdrawal restricted due to security alert. Please contact support." });
    }

    // Get Dynamic Limits
    const minWithdrawal = await getLimit('payment_min_withdrawal', DEFAULTS.MIN_WITHDRAWAL, 'Min Withdrawal Amount (USDT)', 'Minimum allowed withdrawal amount');
    const maxWithdrawal = await getLimit('payment_max_withdrawal', DEFAULTS.MAX_WITHDRAWAL, 'Max Withdrawal Amount (USDT)', 'Maximum allowed withdrawal amount');

    // Validate amount
    if (amount < minWithdrawal) {
      return res.status(400).json({ message: `Minimum withdrawal amount is ${minWithdrawal} USDT` });
    }
    if (amount > maxWithdrawal) {
      return res.status(400).json({ message: `Maximum withdrawal amount is ${maxWithdrawal} USDT` });
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

// @desc    Get Balance
// @route   GET /api/wallet/balance
// @access  Private
const getBalance = async (req, res) => {
  try {
    const user = await require('../models/User').findById(req.user._id);
    if (!user) {
      return res.status(404).json({ message: "User not found" });
    }
    res.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate, proxy-revalidate');
    res.json({ balance: user.balance });
  } catch (error) {
    console.error("Get balance error", error);
    res.status(500).json({ message: "Server error" });
  }
};

// @desc    Validate Withdrawal Address
// @route   POST /api/wallet/validate-address
// @access  Private
const validateWithdrawAddress = async (req, res) => {
  try {
    const { address, network, crypto = 'USDT' } = req.body;
    if (!address || !network) return res.status(400).json({ message: "Address and network are required" });

    const result = await walletService.validateWithdrawAddress(address, crypto, network);
    res.json(result);
  } catch (error) {
    console.error("Address validation error", error);
    res.status(500).json({ message: error.message || "Server error" });
  }
};

// @desc    Get Withdrawal Fee
// @route   GET /api/wallet/withdraw-fee
// @access  Private
const getWithdrawFee = async (req, res) => {
  try {
    const { network, crypto = 'USDT' } = req.query;
    if (!network) return res.status(400).json({ message: "Network is required" });

    const result = await walletService.getWithdrawFee(crypto, network);
    res.json(result);
  } catch (error) {
    console.error("Fee lookup error", error);
    res.status(500).json({ message: error.message || "Server error" });
  }
};

module.exports = {
  createDeposit,
  createWithdrawal,
  getBalance,
  validateWithdrawAddress,
  getWithdrawFee
};
