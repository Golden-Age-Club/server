const User = require('../models/User');
const RiskRule = require('../models/RiskRule');
const RiskLog = require('../models/RiskLog');

class RiskController {
  
  // @desc    Get abnormal users (High/Medium risk)
  // @route   GET /api/admin/risk/users
  static async getAbnormalUsers(req, res) {
    try {
      const { search } = req.query;
      let query = {
        risk_level: { $in: ['medium', 'high', 'Medium', 'High'] }
      };

      if (search) {
        query.username = { $regex: search, $options: 'i' };
      }

      const users = await User.find(query).select('-password_hash');
      
      // Enrich with latest risk reasons from logs
      const enrichedUsers = await Promise.all(users.map(async (user) => {
        const logs = await RiskLog.find({ user_id: user._id, status: 'active' })
          .sort({ created_at: -1 })
          .limit(3);
        
        const riskReasons = logs.map(log => log.rule_name);
        // Fallback reasons if no logs but high risk
        if (riskReasons.length === 0 && user.risk_level === 'high') {
          riskReasons.push('Manual high risk assignment');
        }

        // Calculate win rate
        const winRate = user.total_bet > 0 
          ? ((user.total_won / user.total_bet) * 100).toFixed(1) 
          : 0;

        return {
          id: user._id,
          username: user.username,
          riskLevel: user.risk_level.charAt(0).toUpperCase() + user.risk_level.slice(1),
          riskReasons: riskReasons,
          lastActivity: user.updated_at,
          status: user.is_frozen ? 'frozen' : (user.is_active ? 'active' : 'restricted'),
          totalBets: user.total_bet,
          winRate: winRate
        };
      }));

      res.json(enrichedUsers);
    } catch (error) {
      console.error('Error fetching abnormal users:', error);
      res.status(500).json({ message: 'Failed to fetch abnormal users' });
    }
  }

  // @desc    Get all risk rules
  // @route   GET /api/admin/risk/rules
  static async getRiskRules(req, res) {
    try {
      let rules = await RiskRule.find().sort({ severity: -1 });
      
      // Seed default rules if empty
      if (rules.length === 0) {
        const defaultRules = [
          { name: "Multiple Failed Logins", description: "More than 5 failed login attempts in 1 hour", severity: "High" },
          { name: "Unusual Win Rate", description: "Win rate above 90% with more than 100 bets", severity: "High" },
          { name: "Rapid Deposit Pattern", description: "More than 10 deposits in 24 hours", severity: "Medium" },
          { name: "Large Bet Variance", description: "Bet amount variance exceeds 1000% of average", severity: "Medium" }
        ];
        await RiskRule.insertMany(defaultRules);
        rules = await RiskRule.find().sort({ severity: -1 });
      }

      res.json(rules);
    } catch (error) {
      console.error('Error fetching risk rules:', error);
      res.status(500).json({ message: 'Failed to fetch risk rules' });
    }
  }

  // @desc    Get risk history logs
  // @route   GET /api/admin/risk/history
  static async getRiskHistory(req, res) {
    try {
      const { search } = req.query;
      let query = {};
      
      if (search) {
        query.$or = [
          { username: { $regex: search, $options: 'i' } },
          { rule_name: { $regex: search, $options: 'i' } }
        ];
      }

      const logs = await RiskLog.find(query).sort({ created_at: -1 }).limit(100);
      
      const formattedLogs = logs.map(log => ({
        id: log._id,
        userId: log.user_id,
        username: log.username,
        rule: log.rule_name,
        severity: log.severity,
        timestamp: log.created_at,
        details: log.details,
        status: log.status
      }));

      res.json(formattedLogs);
    } catch (error) {
      console.error('Error fetching risk history:', error);
      res.status(500).json({ message: 'Failed to fetch risk history' });
    }
  }

  // @desc    Take action on a user (Freeze/Restrict)
  // @route   POST /api/admin/risk/action
  static async takeAction(req, res) {
    try {
      const { userId, actionType, reason } = req.body;
      
      const user = await User.findById(userId);
      if (!user) {
        return res.status(404).json({ message: 'User not found' });
      }

      let logAction = 'none';
      
      if (actionType === 'freeze') {
        user.is_frozen = true;
        user.is_active = false;
        logAction = 'freeze';
      } else if (actionType === 'restrict') {
        user.is_active = false; // Or some other flag for restricted
        logAction = 'restrict';
      } else if (actionType === 'unfreeze') {
        user.is_frozen = false;
        user.is_active = true;
        logAction = 'none';
      }

      await user.save();

      // Create a log entry for this action
      await RiskLog.create({
        user_id: user._id,
        username: user.username,
        rule_name: `Manual Action: ${actionType}`,
        severity: 'High',
        details: reason || `Manual action ${actionType} applied by admin`,
        status: 'resolved',
        action_taken: logAction
      });

      res.json({ message: `Action ${actionType} applied successfully`, user });
    } catch (error) {
      console.error('Error taking risk action:', error);
      res.status(500).json({ message: 'Failed to apply action' });
    }
  }
}

module.exports = RiskController;
