const { Transaction, TransactionType, TransactionStatus } = require('../models/Transaction');
const User = require('../models/User');
const ccPaymentService = require('./ccPaymentService');

class WalletService {
  /**
   * Create a deposit request
   */
  async createDeposit(userId, amount, currency, returnUrl) {
    // Generate unique merchant order ID
    const merchantOrderId = `DEP-${Math.floor(Date.now() / 1000)}-${userId}`;

    // Create transaction in database
    let transaction = await Transaction.create({
      user_id: userId,
      type: TransactionType.DEPOSIT,
      amount: amount,
      currency: currency,
      status: TransactionStatus.PENDING,
      merchant_order_id: merchantOrderId
    });

    try {
      const notifyUrl = process.env.WEBHOOK_URL;
      
      const paymentData = await ccPaymentService.createPaymentOrder({
        orderId: merchantOrderId,
        amount: amount,
        currency: currency,
        notifyUrl: notifyUrl,
        returnUrl: returnUrl
      });

      // Update transaction with payment info
      transaction.status = TransactionStatus.PENDING; // Still pending until webhook confirms
      transaction.payment_url = paymentData.paymentUrl || paymentData.payUrl; // Adjust based on actual CCPayment response key
      transaction.payment_address = paymentData.address; // If crypto deposit
      transaction.ccpayment_order_id = paymentData.orderId; // External ID
      
      // Save updates
      await transaction.save();

      return transaction;

    } catch (error) {
      transaction.status = TransactionStatus.FAILED;
      transaction.error_message = error.message || "Payment Provider Error";
      await transaction.save();
      throw error;
    }
  }

  /**
   * Create a withdrawal request
   */
  async createWithdrawal(userId, amount, walletAddress, currency) {
    // 1. Check balance and deduct (Atomic operation)
    // In Mongoose, we can use findOneAndUpdate with condition
    const user = await User.findOneAndUpdate(
      { 
        _id: userId, 
        balance: { $gte: amount } 
      },
      { $inc: { balance: -amount } },
      { new: true }
    );

    if (!user) {
      throw new Error("Insufficient balance");
    }

    // 2. Create Transaction
    const merchantOrderId = `WD-${Math.floor(Date.now() / 1000)}-${userId}`;

    try {
      const transaction = await Transaction.create({
        user_id: userId,
        type: TransactionType.WITHDRAWAL,
        amount: amount,
        currency: currency,
        status: TransactionStatus.PENDING, // Pending manual approval or auto-process
        merchant_order_id: merchantOrderId,
        wallet_address: walletAddress
      });

      // Note: If you have auto-withdrawal logic via CCPayment, call it here.
      // For now, we leave it as PENDING for admin approval or background worker.
      
      return transaction;

    } catch (error) {
      // Refund balance if transaction creation fails (unlikely but safe)
      await User.findByIdAndUpdate(userId, { $inc: { balance: amount } });
      throw error;
    }
  }
}

module.exports = new WalletService();
