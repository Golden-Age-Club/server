const { Transaction, TransactionType } = require('../models/Transaction');
const User = require('../models/User');
const walletService = require('../services/walletService');

class FinanceController {

  /**
   * Get User Balances
   * @route GET /api/admin/finance/balances
   */
  static async getUserBalances(req, res) {
    try {
      const page = parseInt(req.query.page) || 1;
      const limit = parseInt(req.query.limit) || 10;
      const search = req.query.search || '';

      const query = {};
      if (search) {
        query.$or = [
          { username: { $regex: search, $options: 'i' } },
          { email: { $regex: search, $options: 'i' } },
          { first_name: { $regex: search, $options: 'i' } },
          { last_name: { $regex: search, $options: 'i' } }
        ];
      }

      const skip = (page - 1) * limit;

      const users = await User.find(query)
        .select('username first_name last_name email balance is_frozen')
        .sort({ balance: -1 })
        .skip(skip)
        .limit(limit);

      const total = await User.countDocuments(query);

      res.json({
        users: users.map(user => ({
          userId: user._id,
          username: user.username || user.email || 'Unknown',
          available: user.is_frozen ? 0 : user.balance,
          frozen: user.is_frozen ? user.balance : 0, // Simplified logic: if frozen, all balance is frozen
          total: user.balance
        })),
        page,
        pages: Math.ceil(total / limit),
        total
      });
    } catch (error) {
      console.error('Error fetching balances:', error);
      res.status(500).json({ message: 'Server error' });
    }
  }

  /**
   * Get Transactions (General, Deposits, Withdrawals)
   * @route GET /api/admin/finance/transactions
   */
  static async getTransactions(req, res) {
    try {
      const page = parseInt(req.query.page) || 1;
      const limit = parseInt(req.query.limit) || 10;
      const type = req.query.type; // 'deposit', 'withdrawal', etc.
      const search = req.query.search;

      const query = {};
      if (type) {
        query.type = type;
      }

      if (search) {
        // Find users matching search first
        const users = await User.find({
          $or: [
            { username: { $regex: search, $options: 'i' } },
            { email: { $regex: search, $options: 'i' } }
          ]
        }).select('_id');

        const userIds = users.map(u => u._id);

        query.$or = [
          { merchant_order_id: { $regex: search, $options: 'i' } },
          { user_id: { $in: userIds } }
        ];
      }

      const skip = (page - 1) * limit;

      const transactions = await Transaction.find(query)
        .populate('user_id', 'username email first_name last_name')
        .sort({ created_at: -1 })
        .skip(skip)
        .limit(limit);

      const total = await Transaction.countDocuments(query);

      res.json({
        transactions: transactions.map(tx => ({
          id: tx._id,
          orderId: tx.merchant_order_id,
          userId: tx.user_id ? tx.user_id._id : null,
          username: tx.user_id ? (tx.user_id.username || tx.user_id.email) : 'Unknown',
          amount: tx.amount,
          currency: tx.currency,
          type: tx.type,
          status: tx.status,
          date: tx.created_at,
          paymentAddress: tx.payment_address,
          walletAddress: tx.wallet_address,
          txHash: tx.payment_url, // Assuming payment_url might store hash or link
          paymentRecordId: tx.payment_record_id,
          details: tx // Send full object for details view
        })),
        page,
        pages: Math.ceil(total / limit),
        total
      });
    } catch (error) {
      console.error('Error fetching transactions:', error);
      res.status(500).json({ message: 'Server error' });
    }
  }

  /**
   * Update Withdrawal Status
   * @route PUT /api/admin/finance/withdrawals/:id
   */
  static async updateWithdrawalStatus(req, res) {
    try {
      const { id } = req.params;
      const { status, note } = req.body; // 'completed' (approved) or 'failed' (rejected)

      const transaction = await Transaction.findById(id);
      if (!transaction) {
        return res.status(404).json({ message: 'Transaction not found' });
      }

      if (transaction.type !== 'withdrawal') {
        return res.status(400).json({ message: 'Not a withdrawal transaction' });
      }

      if (transaction.status !== 'pending') {
        return res.status(400).json({ message: 'Transaction is not pending' });
      }

      // If admin approved, we set it to processing while we call the provider
      const finalStatus = (status === 'completed') ? 'processing' : status;
      transaction.status = finalStatus;
      if (note) transaction.error_message = note;
      transaction.completed_at = new Date();

      await transaction.save();

      // If approved (now 'processing'), trigger the actual payout via CCPayment
      if (finalStatus === 'processing') {
        try {
          await walletService.processPayout(transaction._id);
        } catch (payoutError) {
          console.error("Failed to execute CCPayment payout:", payoutError);
          // Optional: Revert status to 'pending' or mark as 'error'
          transaction.status = 'failed';
          transaction.error_message = `Payout Failed: ${payoutError.message}`;
          await transaction.save();

          // Refund balance if payout failed
          const user = await User.findById(transaction.user_id);
          if (user) {
            user.balance += transaction.amount;
            await user.save();
          }

          return res.status(502).json({
            message: 'Admin approved but payout provider rejected the request. Funds refunded to user.',
            error: payoutError.message
          });
        }
      }

      // If rejected/refunded, return balance to user
      if (status === 'failed' || status === 'refunded' || status === 'rejected') {
        const user = await User.findById(transaction.user_id);
        if (user) {
          user.balance += transaction.amount; // Add back the amount
          await user.save();

          // Create a refund transaction record? Or just log it? 
          // Ideally create a refund transaction or just rely on the status change.
          // Let's create a refund/adjustment transaction log for clarity if needed, 
          // but updating the withdrawal status to 'refunded' effectively explains why money is back.
          // BUT wait, when withdrawal is requested, balance is usually deducted immediately.
          // If we reject, we must add it back.
        }
      }

      res.json({ message: `Withdrawal ${status}`, transaction });
    } catch (error) {
      console.error('Error updating withdrawal:', error);
      res.status(500).json({ message: 'Server error' });
    }
  }

  /**
   * Manual Balance Adjustment
   * @route POST /api/admin/finance/adjust-balance
   */
  static async adjustBalance(req, res) {
    try {
      const { userId, amount, reason } = req.body;
      const adjustAmount = parseFloat(amount);

      if (isNaN(adjustAmount) || adjustAmount === 0) {
        return res.status(400).json({ message: 'Invalid amount' });
      }

      const user = await User.findById(userId);
      if (!user) {
        return res.status(404).json({ message: 'User not found' });
      }

      // Update Balance
      user.balance += adjustAmount;
      await user.save();

      // Create Transaction Record
      const transaction = await Transaction.create({
        user_id: user._id,
        type: TransactionType.ADJUSTMENT,
        amount: Math.abs(adjustAmount),
        currency: 'USD', // System currency
        status: 'completed',
        merchant_order_id: `ADJ-${Date.now()}-${Math.floor(Math.random() * 1000)}`,
        completed_at: new Date(),
        error_message: reason, // Use error_message field for reason/note for now
        payment_address: 'System Adjustment' // Indicator
      });

      res.json({ message: 'Balance adjusted successfully', newBalance: user.balance });
    } catch (error) {
      console.error('Error adjusting balance:', error);
      res.status(500).json({ message: 'Server error' });
    }
  }
}

module.exports = FinanceController;
