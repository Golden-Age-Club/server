const RiskRule = require('../models/RiskRule');
const RiskLog = require('../models/RiskLog');
const User = require('../models/User');
const { Transaction } = require('../models/Transaction');

class RiskEngine {
  
  /**
   * Helper to get active rule by name
   */
  async getRule(name) {
    return await RiskRule.findOne({ name, is_active: true });
  }

  /**
   * Helper to create a risk log
   */
  async createLog(user, rule, details) {
    // Check if active log exists for this rule/user to avoid spamming
    const existingLog = await RiskLog.findOne({
      user_id: user._id,
      rule_name: rule.name,
      status: 'active'
    });

    if (existingLog) {
      // Update existing log timestamp or count if needed
      return existingLog;
    }

    const log = await RiskLog.create({
      user_id: user._id,
      username: user.username,
      rule_name: rule.name,
      severity: rule.severity,
      details: details,
      status: 'active',
      action_taken: 'none' // Can be updated if auto-action is taken
    });

    // Update rule trigger count
    await RiskRule.findByIdAndUpdate(rule._id, {
      $inc: { triggered_count: 1 },
      last_triggered_at: new Date()
    });
    
    // Update User Risk Level
    if (rule.severity === 'High') {
      user.risk_level = 'high';
      await user.save();
    } else if (rule.severity === 'Medium' && user.risk_level !== 'high') {
      user.risk_level = 'medium';
      await user.save();
    }

    return log;
  }

  /**
   * Check Login Risk
   * Called when a login fails (with valid username/email)
   */
  async recordLoginFailure(user) {
    if (!user) return;

    const rule = await this.getRule("Multiple Failed Logins");
    if (!rule) return;

    const now = new Date();
    const oneHourAgo = new Date(now - 60 * 60 * 1000);

    // Reset counter if last failure was long ago
    if (user.last_failed_login && user.last_failed_login < oneHourAgo) {
      user.failed_login_attempts = 1;
    } else {
      user.failed_login_attempts = (user.failed_login_attempts || 0) + 1;
    }
    
    user.last_failed_login = now;
    await user.save();

    // Threshold check (hardcoded 5 as per rule description default, or dynamic if stored in rule)
    // For now assuming 5 is the threshold.
    if (user.failed_login_attempts > 5) {
      await this.createLog(user, rule, `User failed to login ${user.failed_login_attempts} times in the last hour.`);
    }
  }

  /**
   * Reset Login Failure
   * Called on successful login
   */
  async resetLoginFailure(user) {
    if (user.failed_login_attempts > 0) {
      user.failed_login_attempts = 0;
      await user.save();
    }
  }

  /**
   * Check Gameplay Risk
   * Called after a game win/bet
   */
  async checkGameplayRisk(user) {
    if (!user) return;

    // 1. Unusual Win Rate
    const winRateRule = await this.getRule("Unusual Win Rate");
    if (winRateRule) {
      // Minimum bets to be significant
      if (user.total_bet > 100) { // Assuming total_bet is count? No, schema says Number (likely amount). 
        // We need bet count. Let's check Transaction count for 'game_bet'
        // This might be expensive. Let's approximate or use aggregation.
        // For MVP, let's just use win/bet ratio if tracked, or just check simple heuristics.
        
        // Actually, user.total_bet and user.total_won are amounts. 
        // Win Rate usually means (wins / bets) * 100 in COUNT, or (total_won / total_bet) in ROI.
        // The rule desc says "Win rate above 90%". This usually implies frequency.
        // Let's check last 100 transactions.
        
        const recentBets = await Transaction.find({ 
          user_id: user._id, 
          type: { $in: ['game_bet', 'game_win'] } 
        }).sort({ created_at: -1 }).limit(100);

        if (recentBets.length >= 50) {
          const wins = recentBets.filter(t => t.type === 'game_win').length;
          const bets = recentBets.filter(t => t.type === 'game_bet').length;
          
          if (bets > 20) {
             const winRate = (wins / bets) * 100; // Simplified
             // If win rate > 90% (which is crazy high for slots)
             if (winRate > 90) {
               await this.createLog(user, winRateRule, `Win rate of ${winRate.toFixed(2)}% detected over last ${bets} bets.`);
             }
          }
        }
      }
    }

    // 2. Large Bet Variance
    // "Bet amount variance exceeds 1000% of average"
    const varianceRule = await this.getRule("Large Bet Variance");
    if (varianceRule) {
       // Get last 20 bets
       const lastBets = await Transaction.find({
         user_id: user._id,
         type: 'game_bet'
       }).sort({ created_at: -1 }).limit(20);

       if (lastBets.length >= 10) {
         const amounts = lastBets.map(b => b.amount);
         const sum = amounts.reduce((a, b) => a + b, 0);
         const avg = sum / amounts.length;
         
         const latestBet = amounts[0];
         
         if (latestBet > avg * 10) { // 1000% = 10x
           await this.createLog(user, varianceRule, `Bet amount ${latestBet} is > 10x average (${avg.toFixed(2)}).`);
         }
       }
    }
  }

  /**
   * Check Deposit Risk
   * Called after a deposit is completed
   */
  async checkDepositRisk(user, transaction) {
    if (!user) return;

    const rule = await this.getRule("Rapid Deposit Pattern");
    if (!rule) return;

    // Check deposits in last 24h
    const now = new Date();
    const oneDayAgo = new Date(now - 24 * 60 * 60 * 1000);

    // We can update a counter on User model to avoid heavy query, 
    // but query is safer for accuracy.
    const depositCount = await Transaction.countDocuments({
      user_id: user._id,
      type: 'deposit',
      status: 'completed',
      created_at: { $gte: oneDayAgo }
    });

    // Update user cache
    user.deposit_count_24h = depositCount;
    user.last_deposit_at = now;
    await user.save();

    if (depositCount > 10) {
      await this.createLog(user, rule, `User made ${depositCount} deposits in the last 24 hours.`);
    }
  }
}

module.exports = new RiskEngine();
