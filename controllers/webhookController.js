const jwt = require('jsonwebtoken');
const { Transaction } = require('../models/Transaction');
const User = require('../models/User');
const ccPaymentService = require('../services/ccPaymentService');
const RiskEngine = require('../services/RiskEngine');

// CCPayment Webhook
exports.ccPaymentWebhook = async (req, res) => {
  try {
    const body = req.body;
    const timestamp = req.headers['timestamp'];
    const sign = req.headers['sign'];

    console.log(`Webhook received: order_id=${body.merchant_order_id}, status=${body.order_status}`);

    // Verify signature
    if (body.type === 'ActivateWebhookURL') {
      if (ccPaymentService.verifyActivationSignature(timestamp, sign, body)) {
        console.log('✅ Webhook Activation Successful');
        return res.status(200).json({ msg: 'Success' });
      } else {
        console.warn('⚠️ Webhook Activation Failed: Invalid Signature');
        return res.status(401).json({ error: 'Invalid signature' });
      }
    }

    if (!ccPaymentService.verifyWebhookSignature(timestamp, sign, body)) {
      console.warn(`⚠️ Invalid webhook signature for order: ${body.merchant_order_id}`);
      return res.status(401).json({ message: 'Invalid signature' });
    }

    const merchant_order_id = body.merchant_order_id;
    const order_status = body.order_status;

    // Get transaction
    const transaction = await Transaction.findOne({ merchant_order_id });
    if (!transaction) {
      return res.status(404).json({ message: 'Transaction not found' });
    }

    // Handle Deposit
    if (transaction.type === 'deposit') {
      if (order_status === 'paid' || order_status === 'confirmed') {
        // Atomic update to ensure idempotency
        // Only update if status is NOT 'completed'
        const updatedTx = await Transaction.findOneAndUpdate(
          { _id: transaction._id, status: { $ne: 'completed' } },
          {
            $set: {
              status: 'completed',
              completed_at: new Date(),
              webhook_data: body
            }
          },
          { new: true }
        );

        if (updatedTx) {
          console.log(`Processing deposit confirmation: user=${transaction.user_id}, amount=${transaction.amount}`);

          // Only credit balance if transaction update succeeded
          await User.findByIdAndUpdate(transaction.user_id, { $inc: { balance: transaction.amount } });

          console.log(`✅ Deposit completed: transaction_id=${transaction._id}`);
        } else {
          console.log(`⚠️ Deposit already processed (duplicate webhook): transaction_id=${transaction._id}`);
        }
      } else if (order_status === 'expired' || order_status === 'failed') {
        await Transaction.updateOne({ _id: transaction._id }, { status: 'failed', webhook_data: body });
      }
    }
    // Handle Withdrawal
    else if (transaction.type === 'withdrawal') {
      if (order_status === 'success' || order_status === 'completed') {
        // Atomic update
        const updatedTx = await Transaction.findOneAndUpdate(
          { _id: transaction._id, status: { $ne: 'completed' } },
          {
            $set: {
              status: 'completed',
              completed_at: new Date(),
              webhook_data: body
            }
          }
        );

        if (updatedTx) {
          console.log(`✅ Withdrawal completed: transaction_id=${transaction._id}`);
        }

      } else if (order_status === 'failed') {
        // Refund balance ONLY if we are the ones properly marking it as failed
        // Prevents double-refund on duplicate 'failed' webhooks
        const updatedTx = await Transaction.findOneAndUpdate(
          { _id: transaction._id, status: { $nin: ['failed', 'completed'] } }, // Ensure not already processed
          {
            $set: {
              status: 'failed',
              webhook_data: body
            }
          },
          { new: true }
        );

        if (updatedTx) {
          // Refund balance
          console.warn(`⚠️ Withdrawal failed, refunding: user=${transaction.user_id}, amount=${transaction.amount}`);
          await User.findByIdAndUpdate(transaction.user_id, { $inc: { balance: transaction.amount } });
        } else {
          console.warn(`⚠️ Withdrawal failed webhook received but transaction already final: ${transaction._id}`);
        }
      }
    }

    res.json({ status: 'success' });
  } catch (error) {
    console.error('CCPayment webhook error:', error);
    res.status(500).json({ message: error.message });
  }
};

// Unified Callback (Game Provider)
exports.unifiedCallback = async (req, res) => {
  try {
    const data = req.body;
    console.log(`Callback Received:`, JSON.stringify(data));

    const {
      cmd,
      player_token,
      transactionId,
      roundId,
      gameId,
      currencyId,
      betAmount = 0,
      winAmount = 0,
      amount = 0,
      betInfo,
      signature
    } = data;

    // 1. Decode Player Token
    let userId = null;

    // Try JWT
    try {
      const decoded = jwt.verify(player_token, process.env.JWT_SECRET_KEY);
      userId = decoded.user_id || decoded.sub;
    } catch (e) {
      // Try Base64 JSON
      try {
        const buffer = Buffer.from(player_token, 'base64');
        const decodedStr = buffer.toString('utf-8');
        if (decodedStr.startsWith('{')) {
          const decodedJson = JSON.parse(decodedStr);
          userId = decodedJson.player_id || decodedJson.user_id;
        } else {
          userId = decodedStr;
        }
      } catch (err) {
        console.error(`Token decode failed: ${err.message}`);
        return res.json({
          result: true,
          err_desc: 'Invalid token',
          err_code: 401
        });
      }
    }

    if (!userId) {
      return res.json({
        result: true,
        err_desc: 'Player not found',
        err_code: 2
      });
    }

    // 2. Get User
    let user = await User.findById(userId);
    if (!user && !isNaN(userId)) {
      // Fallback for numeric ID (Telegram ID)
      user = await User.findOne({ telegram_id: userId });
    }

    if (!user) {
      return res.json({
        result: true,
        err_desc: 'Player not found',
        err_code: 2
      });
    }

    const userIdStr = user._id.toString();

    // 3. Handle Commands
    if (cmd === 'withdraw') { // Game Bet
      const existingTx = await Transaction.findOne({ merchant_order_id: transactionId });
      if (existingTx) {
        // Update existing transaction
        existingTx.updated_at = new Date();
        if (betInfo) existingTx.bet_info = betInfo;
        await existingTx.save();

        return res.json({
          result: true,
          err_desc: 'OK',
          err_code: 0,
          balance: user.balance,
          before_balance: user.balance,
          transactionId
        });
      }

      const betAmt = parseFloat(betAmount);
      const beforeBalance = user.balance;
      const newBalance = beforeBalance - betAmt;

      if (newBalance < 0) {
        return res.json({
          result: true,
          err_desc: 'Insufficient balance',
          err_code: 3,
          balance: beforeBalance,
          before_balance: beforeBalance,
          transactionId
        });
      }

      // Deduct Balance
      user.balance = newBalance;
      // Update stats if needed (skipped for brevity, but recommended)
      await user.save();

      // Create Transaction
      await Transaction.create({
        user_id: userIdStr,
        type: 'game_bet',
        amount: betAmt,
        currency: currencyId || 'USD',
        status: 'completed',
        merchant_order_id: transactionId,
        game_id: gameId,
        round_id: roundId,
        bet_info: betInfo,
        balance_after: newBalance
      });

      // Check Gameplay Risk
      await RiskEngine.checkGameplayRisk(user);

      return res.json({
        result: true,
        err_desc: 'OK',
        err_code: 0,
        balance: newBalance,
        before_balance: beforeBalance,
        transactionId
      });

    } else if (cmd === 'deposit') { // Game Win
      const existingTx = await Transaction.findOne({ merchant_order_id: transactionId });
      if (existingTx) {
        // Update existing transaction
        existingTx.updated_at = new Date();
        if (betInfo) existingTx.bet_info = betInfo;
        await existingTx.save();

        return res.json({
          result: true,
          err_desc: 'OK',
          err_code: 0,
          balance: user.balance,
          before_balance: user.balance,
          transactionId
        });
      }

      const winAmt = parseFloat(winAmount);
      const beforeBalance = user.balance;
      const newBalance = beforeBalance + winAmt;

      // Add Balance
      user.balance = newBalance;
      await user.save();

      // Create Transaction
      await Transaction.create({
        user_id: userIdStr,
        type: 'game_win',
        amount: winAmt,
        currency: currencyId || 'USD',
        status: 'completed',
        merchant_order_id: transactionId,
        game_id: gameId,
        round_id: roundId,
        bet_info: betInfo,
        balance_after: newBalance
      });

      // Check Gameplay Risk
      await RiskEngine.checkGameplayRisk(user);

      return res.json({
        result: true,
        err_desc: 'OK',
        err_code: 0,
        balance: newBalance,
        before_balance: beforeBalance,
        transactionId
      });

    } else if (cmd === 'rollback') {
      const originalTx = await Transaction.findOne({ merchant_order_id: transactionId });
      if (!originalTx) {
        return res.json({
          result: true,
          err_desc: 'Transaction not found',
          err_code: 2
        });
      }

      // Check if already refunded
      if (originalTx.status === 'refunded') {
        return res.json({
          result: true,
          err_desc: 'OK',
          err_code: 0,
          balance: user.balance,
          before_balance: user.balance,
          transactionId
        });
      }

      const txAmount = parseFloat(originalTx.amount);
      const beforeBalance = user.balance;
      let newBalance = beforeBalance;

      if (originalTx.type === 'game_bet') {
        // Reverse bet -> Refund money
        newBalance = beforeBalance + txAmount;
        user.balance = newBalance;
        await user.save();
      } else if (originalTx.type === 'game_win') {
        // Reverse win -> Deduct money
        newBalance = beforeBalance - txAmount;
        if (newBalance < 0) {
          return res.json({
            result: true,
            err_desc: 'Insufficient balance for rollback',
            err_code: 4,
            balance: beforeBalance,
            before_balance: beforeBalance,
            transactionId
          });
        }
        user.balance = newBalance;
        await user.save();
      } else {
        return res.json({
          result: true,
          err_desc: 'Invalid transaction type for rollback',
          err_code: 5
        });
      }

      // Update original transaction instead of creating new one
      originalTx.status = 'refunded';
      originalTx.updated_at = new Date();
      if (betInfo) originalTx.bet_info = betInfo;
      await originalTx.save();

      return res.json({
        result: true,
        err_desc: 'OK',
        err_code: 0,
        balance: newBalance,
        before_balance: beforeBalance,
        transactionId
      });

    } else if (cmd === 'getPlayerInfo' || cmd === 'getBalance') {
      return res.json({
        result: true,
        err_desc: 'OK',
        err_code: 0,
        currency: currencyId || user.currency || 'USD',
        balance: user.balance,
        display_name: user.username || 'Player',
        gender: user.gender || 'Male',
        country: user.country || 'TR',
        player_id: user.telegram_id || userIdStr,
        city: user.city || 'Istanbul',
        email: user.email || ''
      });
    } else {
      return res.json({
        result: true,
        err_desc: 'Invalid command',
        err_code: 4
      });
    }

  } catch (error) {
    console.error('Unified callback error:', error);
    res.status(500).json({ message: error.message });
  }
};
