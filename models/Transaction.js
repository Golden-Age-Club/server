const mongoose = require('mongoose');

const TransactionType = {
  DEPOSIT: 'deposit',
  WITHDRAWAL: 'withdrawal',
  GAME_BET: 'game_bet',
  GAME_WIN: 'game_win',
  GAME_REFUND: 'game_refund',
  ADJUSTMENT: 'adjustment'
};

const TransactionStatus = {
  PENDING: 'pending',
  AWAITING_DEPOSIT: 'awaiting_deposit',
  AWAITING_APPROVAL: 'awaiting_approval',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  FAILED: 'failed',
  EXPIRED: 'expired',
  REFUNDED: 'refunded'
};

const Currency = {
  USDT_TRC20: 'USDT.TRC20',
  USDT_ERC20: 'USDT.ERC20',
  USDT_BEP20: 'USDT.BEP20'
};

const transactionSchema = new mongoose.Schema({
  user_id: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  type: {
    type: String,
    enum: Object.values(TransactionType),
    required: true
  },
  amount: {
    type: Number,
    required: true
  },
  currency: {
    type: String,
    required: true
  },
  status: {
    type: String,
    enum: Object.values(TransactionStatus),
    default: TransactionStatus.PENDING,
    required: true
  },
  merchant_order_id: {
    type: String,
    required: true,
    unique: true
  },
  completed_at: {
    type: Date
  },
  payment_url: {
    type: String
  },
  payment_address: {
    type: String
  },
  wallet_address: {
    type: String
  },
  ccpayment_order_id: {
    type: String
  },
  txid: {
    type: String
  },
  fee: {
    type: Number,
    default: 0
  },
  network: {
    type: String
  },
  error_message: {
    type: String
  },
  game_id: {
    type: String
  },
  round_id: {
    type: String
  },
  bet_info: {
    type: mongoose.Schema.Types.Mixed
  },
  webhook_data: {
    type: mongoose.Schema.Types.Mixed
  },
  balance_after: {
    type: Number
  },
  payment_record_id: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'PaymentRecord'
  }
}, {
  timestamps: { createdAt: 'created_at', updatedAt: 'updated_at' }
});

// Indexes
transactionSchema.index({ user_id: 1 });
transactionSchema.index({ ccpayment_order_id: 1 });
transactionSchema.index({ status: 1 });
transactionSchema.index({ type: 1 });

const Transaction = mongoose.model('Transaction', transactionSchema);

module.exports = {
  Transaction,
  TransactionType,
  TransactionStatus,
  Currency
};
