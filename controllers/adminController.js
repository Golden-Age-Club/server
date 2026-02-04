const Admin = require('../models/Admin');
const User = require('../models/User');
const { Transaction } = require('../models/Transaction');
const VipTier = require('../models/VipTier');
const PaymentRecord = require('../models/PaymentRecord');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

class AdminController {

  /**
   * Seed the super admin user if it doesn't exist
   */
  static async seedSuperAdmin() {
    try {
      const email = "admin@pghomeco";
      const existingAdmin = await Admin.findOne({ email });

      if (!existingAdmin) {
        const salt = await bcrypt.genSalt(10);
        const hashedPassword = await bcrypt.hash("Googe111", salt);

        await Admin.create({
          email,
          password_hash: hashedPassword,
          first_name: "Super",
          last_name: "Admin",
          title: "System Administrator",
          role: "super_admin",
          verified: true,
          permissions: ['dashboard', 'users', 'finance', 'bets', 'vip', 'risk', 'promotions', 'reports', 'system'],
          bio: "Default system super administrator."
        });
        console.log('✅ Super Admin created successfully');
      } else {
        console.log('ℹ️ Super Admin already exists');
      }
    } catch (error) {
      console.error('❌ Error seeding super admin:', error);
    }
  }

  /**
   * Admin Login
   * @route POST /api/admin/auth/login
   */
  static async login(req, res) {
    try {
      const { email, password } = req.body;

      // Check for admin email
      const admin = await Admin.findOne({ email });

      if (admin && (await bcrypt.compare(password, admin.password_hash))) {
        // Create token
        const token = jwt.sign(
          { id: admin._id, email: admin.email, role: admin.role },
          process.env.JWT_SECRET_KEY,
          { expiresIn: '12h' } // 12 hours expiration
        );

        // Update last login
        admin.last_login = new Date();
        await admin.save();

        res.json({
          _id: admin._id,
          name: `${admin.first_name} ${admin.last_name}`,
          email: admin.email,
          role: admin.role,
          permissions: admin.permissions,
          token
        });
      } else {
        res.status(401).json({ message: 'Invalid email or password' });
      }
    } catch (error) {
      console.error(error);
      res.status(500).json({ message: 'Server error' });
    }
  }

  /**
   * Get Current Admin Profile
   * @route GET /api/admin/auth/me
   */
  static async getProfile(req, res) {
    try {
      const admin = await Admin.findById(req.admin._id).select('-password_hash');

      if (admin) {
        // Format response to match ProfilePage.jsx expectations
        res.json({
          name: `${admin.first_name} ${admin.last_name}`,
          first_name: admin.first_name,
          last_name: admin.last_name,
          title: admin.title,
          email: admin.email,
          phone: admin.phone || '',
          location: admin.location || '',
          joinDate: admin.created_at.toLocaleDateString('en-US', { month: 'long', year: 'numeric' }),
          avatar: admin.avatar || `${admin.first_name[0]}${admin.last_name[0]}`,
          verified: admin.verified,
          bio: admin.bio || '',
          role: admin.role,
          permissions: admin.permissions
        });
      } else {
        res.status(404).json({ message: 'Admin not found' });
      }
    } catch (error) {
      console.error(error);
      res.status(500).json({ message: 'Server error' });
    }
  }

  /**
   * Update Admin Profile
   * @route PUT /api/admin/auth/profile
   */
  static async updateProfile(req, res) {
    try {
      const admin = await Admin.findById(req.admin._id);

      if (admin) {
        admin.first_name = req.body.first_name || admin.first_name;
        admin.last_name = req.body.last_name || admin.last_name;
        admin.email = req.body.email || admin.email;

        if (req.body.bio !== undefined) admin.bio = req.body.bio;
        if (req.body.phone !== undefined) admin.phone = req.body.phone;
        if (req.body.location !== undefined) admin.location = req.body.location;
        if (req.body.avatar !== undefined) admin.avatar = req.body.avatar;

        if (req.body.password) {
          res.status(400).json({ message: 'Password cannot be updated here' });
          return;
        }

        const updatedAdmin = await admin.save();

        res.json({
          _id: updatedAdmin._id,
          name: `${updatedAdmin.first_name} ${updatedAdmin.last_name}`,
          first_name: updatedAdmin.first_name,
          last_name: updatedAdmin.last_name,
          title: updatedAdmin.title,
          email: updatedAdmin.email,
          role: updatedAdmin.role,
          phone: updatedAdmin.phone || '',
          location: updatedAdmin.location || '',
          bio: updatedAdmin.bio || '',
          avatar: updatedAdmin.avatar || `${updatedAdmin.first_name[0]}${updatedAdmin.last_name[0]}`,
          verified: updatedAdmin.verified,
          permissions: updatedAdmin.permissions
        });
      } else {
        res.status(404).json({ message: 'Admin not found' });
      }
    } catch (error) {
      console.error(error);
      res.status(500).json({ message: 'Server error' });
    }
  }

  /**
   * Update Admin Password
   * @route PUT /api/admin/auth/password
   */
  static async updatePassword(req, res) {
    try {
      const { currentPassword, newPassword } = req.body;
      const admin = await Admin.findById(req.admin._id);

      if (admin && (await bcrypt.compare(currentPassword, admin.password_hash))) {
        const salt = await bcrypt.genSalt(10);
        admin.password_hash = await bcrypt.hash(newPassword, salt);
        await admin.save();
        res.json({ message: 'Password updated successfully' });
      } else {
        res.status(401).json({ message: 'Invalid current password' });
      }
    } catch (error) {
      console.error(error);
      res.status(500).json({ message: 'Server error' });
    }
  }

  /**
   * Get Dashboard Statistics
   * @route GET /api/admin/stats
   */
  static async getDashboardStats(req, res) {
    try {
      const now = new Date();
      const oneDayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);
      const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
      const fourteenDaysAgo = new Date(now.getTime() - 14 * 24 * 60 * 60 * 1000);

      // --- Helper for aggregation ---
      const aggregateStats = async (matchQuery) => {
        const result = await Transaction.aggregate([
          { $match: { ...matchQuery, status: 'completed' } },
          {
            $group: {
              _id: null,
              totalBets: {
                $sum: {
                  $cond: [{ $eq: ["$type", "game_bet"] }, "$amount", 0]
                }
              },
              totalWins: {
                $sum: {
                  $cond: [{ $eq: ["$type", "game_win"] }, "$amount", 0]
                }
              },
              betCount: {
                $sum: {
                  $cond: [{ $eq: ["$type", "game_bet"] }, 1, 0]
                }
              }
            }
          }
        ]);
        return result[0] || { totalBets: 0, totalWins: 0, betCount: 0 };
      };

      // 1. All Time Stats
      const allTimeStats = await aggregateStats({});

      // 2. Last 7 Days Stats
      const currentPeriodStats = await aggregateStats({
        created_at: { $gte: sevenDaysAgo }
      });

      // 3. Previous 7 Days Stats
      const previousPeriodStats = await aggregateStats({
        created_at: { $gte: fourteenDaysAgo, $lt: sevenDaysAgo }
      });

      // --- Calculations ---

      // GGR
      const ggr = allTimeStats.totalBets - allTimeStats.totalWins;
      const ggrCurrent = currentPeriodStats.totalBets - currentPeriodStats.totalWins;
      const ggrPrevious = previousPeriodStats.totalBets - previousPeriodStats.totalWins;
      const ggrChange = ggrPrevious !== 0 ? ((ggrCurrent - ggrPrevious) / Math.abs(ggrPrevious)) * 100 : 0;

      // RTP
      const rtp = allTimeStats.totalBets > 0 ? (allTimeStats.totalWins / allTimeStats.totalBets) * 100 : 0;
      const rtpCurrent = currentPeriodStats.totalBets > 0 ? (currentPeriodStats.totalWins / currentPeriodStats.totalBets) * 100 : 0;
      const rtpPrevious = previousPeriodStats.totalBets > 0 ? (previousPeriodStats.totalWins / previousPeriodStats.totalBets) * 100 : 0;
      const rtpChange = rtpPrevious !== 0 ? ((rtpCurrent - rtpPrevious) / Math.abs(rtpPrevious)) * 100 : 0;

      // Total Bets (Count)
      const bets = allTimeStats.betCount;
      const betsCurrent = currentPeriodStats.betCount;
      const betsPrevious = previousPeriodStats.betCount;
      const betsChange = betsPrevious !== 0 ? ((betsCurrent - betsPrevious) / betsPrevious) * 100 : 0;

      // DAU (Active Users)
      // Current: Users active in last 24h
      const dauCurrentResult = await Transaction.distinct('user_id', {
        created_at: { $gte: oneDayAgo }
      });
      const dauCurrent = dauCurrentResult.length;

      // Previous: Users active 24h-48h ago
      const dauPreviousResult = await Transaction.distinct('user_id', {
        created_at: { $gte: new Date(now.getTime() - 48 * 60 * 60 * 1000), $lt: oneDayAgo }
      });
      const dauPrevious = dauPreviousResult.length;

      const dauChange = dauPrevious !== 0 ? ((dauCurrent - dauPrevious) / dauPrevious) * 100 : 0;


      res.json({
        ggr: {
          value: ggr,
          percentage: parseFloat(ggrChange.toFixed(2)),
          is_positive: ggrChange >= 0
        },
        rtp: {
          value: parseFloat(rtp.toFixed(2)),
          percentage: parseFloat(rtpChange.toFixed(2)),
          is_positive: rtpChange >= 0
        },
        dau: {
          value: dauCurrent,
          percentage: parseFloat(dauChange.toFixed(2)),
          is_positive: dauChange >= 0
        },
        bets: {
          value: bets,
          percentage: parseFloat(betsChange.toFixed(2)),
          is_positive: betsChange >= 0
        }
      });

    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
      res.status(500).json({ message: 'Failed to fetch dashboard statistics' });
    }
  }

  /**
   * Get Chart Statistics
   * @route GET /api/admin/charts
   */
  static async getChartStats(req, res) {
    try {
      const { range = 'year' } = req.query; // year, month, week
      const now = new Date();
      let startDate;
      let groupBy;
      let labels = [];

      if (range === 'week') {
        startDate = new Date(now);
        startDate.setDate(now.getDate() - 6); // Last 7 days
        startDate.setHours(0, 0, 0, 0);
        groupBy = {
          $dateToString: { format: "%Y-%m-%d", date: "$created_at" }
        };
        // Generate labels for last 7 days
        for (let i = 0; i < 7; i++) {
          const d = new Date(startDate);
          d.setDate(d.getDate() + i);
          labels.push(d.toLocaleDateString('en-US', { weekday: 'short' }));
        }
      } else if (range === 'month') {
        startDate = new Date(now);
        startDate.setDate(now.getDate() - 29); // Last 30 days
        startDate.setHours(0, 0, 0, 0);
        groupBy = {
          $dateToString: { format: "%Y-%m-%d", date: "$created_at" }
        };
        // Generate labels? Too many points for x-axis maybe, but okay for line chart
        // Let's rely on the aggregation result to sort and map
      } else {
        // Default: year (Last 12 months)
        startDate = new Date(now);
        startDate.setMonth(now.getMonth() - 11);
        startDate.setDate(1);
        startDate.setHours(0, 0, 0, 0);
        groupBy = {
          $dateToString: { format: "%Y-%m", date: "$created_at" }
        };
      }

      const stats = await Transaction.aggregate([
        {
          $match: {
            created_at: { $gte: startDate },
            status: 'completed'
          }
        },
        {
          $group: {
            _id: groupBy,
            totalBets: {
              $sum: {
                $cond: [{ $eq: ["$type", "game_bet"] }, "$amount", 0]
              }
            },
            totalWins: {
              $sum: {
                $cond: [{ $eq: ["$type", "game_win"] }, "$amount", 0]
              }
            },
            totalDeposits: {
              $sum: {
                $cond: [{ $eq: ["$type", "deposit"] }, "$amount", 0]
              }
            },
            totalWithdrawals: {
              $sum: {
                $cond: [{ $eq: ["$type", "withdrawal"] }, "$amount", 0]
              }
            }
          }
        },
        { $sort: { _id: 1 } }
      ]);

      // Process data to match labels
      let processedLabels = [];
      let revenueData = []; // GGR
      let expensesData = []; // Wins
      let profitData = []; // Net Profit (same as GGR usually)

      if (range === 'year') {
        const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
        // Initialize last 12 months map
        let dataMap = {};
        let current = new Date(startDate);
        while (current <= now) {
          const key = current.toISOString().slice(0, 7); // YYYY-MM
          const label = monthNames[current.getMonth()];
          processedLabels.push(label);
          dataMap[key] = { revenue: 0, expenses: 0 };
          current.setMonth(current.getMonth() + 1);
        }

        stats.forEach(item => {
          if (dataMap[item._id]) {
            dataMap[item._id].revenue = item.totalBets - item.totalWins;
            dataMap[item._id].expenses = item.totalWins;
          }
        });

        Object.values(dataMap).forEach(val => {
          revenueData.push(val.revenue);
          expensesData.push(val.expenses);
        });

      } else if (range === 'week') {
        // Map 7 days
        let dataMap = {};
        let current = new Date(startDate);
        for (let i = 0; i < 7; i++) {
          const key = current.toISOString().slice(0, 10); // YYYY-MM-DD
          dataMap[key] = { revenue: 0, expenses: 0 };
          current.setDate(current.getDate() + 1);
        }

        // Re-generate labels to match the keys order
        processedLabels = labels;

        stats.forEach(item => {
          if (dataMap[item._id]) {
            dataMap[item._id].revenue = item.totalBets - item.totalWins;
            dataMap[item._id].expenses = item.totalWins;
          }
        });

        Object.values(dataMap).forEach(val => {
          revenueData.push(val.revenue);
          expensesData.push(val.expenses);
        });

      } else {
        // Month - just return raw daily data
        stats.forEach(item => {
          processedLabels.push(item._id.slice(5)); // MM-DD
          revenueData.push(item.totalBets - item.totalWins);
          expensesData.push(item.totalWins);
        });
      }

      res.json({
        labels: processedLabels,
        revenue: revenueData,
        expenses: expensesData
      });

    } catch (error) {
      console.error('Error fetching chart stats:', error);
      res.status(500).json({ message: 'Failed to fetch chart statistics' });
    }
  }

  /**
   * Get User Statistics (Total, Active, VIP, Frozen)
   * @route GET /api/admin/users/stats
   */
  static async getUserStats(req, res) {
    try {
      const total = await User.countDocuments();
      const active = await User.countDocuments({ is_active: true });
      const vip = await User.countDocuments({ vip_level: { $gt: 0 } });
      const frozen = await User.countDocuments({ is_frozen: true });

      res.json({
        total,
        active,
        vip,
        frozen
      });
    } catch (error) {
      console.error('Error fetching user stats:', error);
      res.status(500).json({ message: 'Failed to fetch user stats' });
    }
  }

  /**
   * Get Users List with Pagination, Search, and Filters
   * @route GET /api/admin/users
   */
  static async getUsers(req, res) {
    try {
      const { page = 1, limit = 10, search = '', role, status } = req.query;
      const skip = (page - 1) * limit;

      let query = {};

      if (search) {
        query.$or = [
          { username: { $regex: search, $options: 'i' } },
          { email: { $regex: search, $options: 'i' } },
          { first_name: { $regex: search, $options: 'i' } },
          { last_name: { $regex: search, $options: 'i' } }
        ];
      }

      if (role) {
        // Assuming role logic if implemented in future, current User model doesn't have role
      }

      if (status) {
        if (status === 'active') query.is_active = true;
        if (status === 'frozen') query.is_frozen = true;
        // If conflict between is_active and is_frozen, handle accordingly
        // Usually is_frozen = true implies is_active = false or blocked
      }

      const users = await User.find(query)
        .select('-password_hash')
        .sort({ created_at: -1 })
        .skip(skip)
        .limit(parseInt(limit));

      const total = await User.countDocuments(query);

      res.json({
        users,
        total,
        page: parseInt(page),
        pages: Math.ceil(total / limit)
      });
    } catch (error) {
      console.error('Error fetching users:', error);
      res.status(500).json({ message: 'Failed to fetch users' });
    }
  }

  /**
   * Create New User
   * @route POST /api/admin/users
   */
  static async createUser(req, res) {
    try {
      const { username, email, password, first_name, last_name, vip_level, risk_level, balance } = req.body;

      const existingUser = await User.findOne({ $or: [{ email }, { username }] });
      if (existingUser) {
        return res.status(400).json({ message: 'User with this email or username already exists' });
      }

      let password_hash = null;
      if (password) {
        const salt = await bcrypt.genSalt(10);
        password_hash = await bcrypt.hash(password, salt);
      }

      const newUser = await User.create({
        username,
        email,
        password_hash,
        first_name,
        last_name,
        vip_level: vip_level || 0,
        risk_level: risk_level || 'low',
        balance: balance || 0,
        is_active: true,
        is_frozen: false
      });

      res.status(201).json(newUser);
    } catch (error) {
      console.error('Error creating user:', error);
      res.status(500).json({ message: 'Failed to create user' });
    }
  }

  /**
   * Get User Details
   * @route GET /api/admin/users/:id
   */
  static async getUser(req, res) {
    try {
      const user = await User.findById(req.params.id).select('-password_hash');
      if (!user) {
        return res.status(404).json({ message: 'User not found' });
      }
      res.json(user);
    } catch (error) {
      console.error('Error fetching user:', error);
      res.status(500).json({ message: 'Failed to fetch user' });
    }
  }

  /**
   * Update User
   * @route PUT /api/admin/users/:id
   */
  static async updateUser(req, res) {
    try {
      const { first_name, last_name, email, vip_level, risk_level, is_active, is_frozen, balance } = req.body;

      const user = await User.findById(req.params.id);
      if (!user) {
        return res.status(404).json({ message: 'User not found' });
      }

      if (first_name) user.first_name = first_name;
      if (last_name) user.last_name = last_name;
      if (email) user.email = email;
      if (vip_level !== undefined) user.vip_level = vip_level;
      if (risk_level) user.risk_level = risk_level;
      if (is_active !== undefined) user.is_active = is_active;
      if (is_frozen !== undefined) user.is_frozen = is_frozen;
      if (balance !== undefined) user.balance = balance;

      await user.save();
      res.json(user);
    } catch (error) {
      console.error('Error updating user:', error);
      res.status(500).json({ message: 'Failed to update user' });
    }
  }

  /**
   * Delete User
   * @route DELETE /api/admin/users/:id
   */
  static async deleteUser(req, res) {
    try {
      const user = await User.findByIdAndDelete(req.params.id);
      if (!user) {
        return res.status(404).json({ message: 'User not found' });
      }
      res.json({ message: 'User deleted successfully' });
    } catch (error) {
      console.error('Error deleting user:', error);
      res.status(500).json({ message: 'Failed to delete user' });
    }
  }

  // --- VIP Management ---

  /**
   * Get VIP Tiers
   * @route GET /api/admin/vip/tiers
   */
  static async getVipTiers(req, res) {
    try {
      let tiers = await VipTier.find().sort({ level: 1 });

      // Seed default tiers if empty
      if (tiers.length === 0) {
        const defaultTiers = [
          { level: 1, name: "Bronze", min_deposit: 0, min_bets: 0, benefits: "Basic support, 1% cashback", color: "bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200" },
          { level: 2, name: "Silver", min_deposit: 1000, min_bets: 5000, benefits: "Priority support, 2% cashback, weekly bonus", color: "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200" },
          { level: 3, name: "Gold", min_deposit: 5000, min_bets: 20000, benefits: "VIP support, 3% cashback, daily bonus, exclusive games", color: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200" },
          { level: 4, name: "Platinum", min_deposit: 25000, min_bets: 100000, benefits: "Dedicated manager, 5% cashback, custom bonuses", color: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200" },
          { level: 5, name: "Diamond", min_deposit: 100000, min_bets: 500000, benefits: "Personal account manager, 7% cashback, exclusive events", color: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200" }
        ];
        await VipTier.insertMany(defaultTiers);
        tiers = await VipTier.find().sort({ level: 1 });
      }

      res.json(tiers);
    } catch (error) {
      console.error('Error fetching VIP tiers:', error);
      res.status(500).json({ message: 'Failed to fetch VIP tiers' });
    }
  }

  /**
   * Update VIP Tier
   * @route POST /api/admin/vip/tiers
   */
  static async updateVipTier(req, res) {
    try {
      const { level, name, min_deposit, min_bets, benefits, color } = req.body;

      const tier = await VipTier.findOneAndUpdate(
        { level },
        { name, min_deposit, min_bets, benefits, color },
        { upsert: true, new: true }
      );

      res.json(tier);
    } catch (error) {
      console.error('Error updating VIP tier:', error);
      res.status(500).json({ message: 'Failed to update VIP tier' });
    }
  }

  /**
   * Get High Value Users (VIP)
   * @route GET /api/admin/vip/users
   */
  static async getVipUsers(req, res) {
    try {
      const { search = '' } = req.query;
      let query = {};

      if (search) {
        query.$or = [
          { username: { $regex: search, $options: 'i' } },
          { email: { $regex: search, $options: 'i' } }
        ];
      }

      // Users with high bets or explicitly VIP
      // We can define "High Value" as total_bet > 1000 OR vip_level > 0
      query.$or = [
        ...(query.$or || []),
        { total_bet: { $gt: 1000 } },
        { vip_level: { $gt: 0 } }
      ];

      // If search is present, we need to combine it carefully.
      // Actually, standard logic: (search) AND (high value)
      if (search) {
        query = {
          $and: [
            { $or: [{ username: { $regex: search, $options: 'i' } }, { email: { $regex: search, $options: 'i' } }] },
            { $or: [{ total_bet: { $gt: 1000 } }, { vip_level: { $gt: 0 } }] }
          ]
        };
      } else {
        query = { $or: [{ total_bet: { $gt: 1000 } }, { vip_level: { $gt: 0 } }] };
      }

      const users = await User.find(query)
        .select('username email vip_level total_bet total_won balance created_at last_login')
        .sort({ total_bet: -1 })
        .limit(50);

      // Fetch tiers to map level to name
      const tiers = await VipTier.find().lean();
      const tierMap = tiers.reduce((acc, tier) => ({ ...acc, [tier.level]: tier.name }), {});

      const formattedUsers = users.map(user => ({
        id: user._id,
        username: user.username,
        email: user.email,
        currentVip: tierMap[user.vip_level] || `Level ${user.vip_level}`,
        vipLevel: user.vip_level,
        totalDeposit: 0, // Need transaction aggregation for this, or store in User model. For now, 0 or simple mock.
        // Actually, let's just use balance or total_bet
        totalBets: user.total_bet,
        lastActivity: user.updated_at ? new Date(user.updated_at).toLocaleDateString() : 'N/A',
        status: user.is_active ? 'active' : 'inactive'
      }));

      res.json(formattedUsers);
    } catch (error) {
      console.error('Error fetching VIP users:', error);
      res.status(500).json({ message: 'Failed to fetch VIP users' });
    }
  }

  /**
   * Export Data (CSV)
   * @route GET /api/admin/export
   */
  static async exportData(req, res) {
    try {
      const { range = 'month' } = req.query;
      const now = new Date();
      let startDate = new Date();

      if (range === 'week') {
        startDate.setDate(now.getDate() - 7);
      } else if (range === 'month') {
        startDate.setDate(now.getDate() - 30);
      } else if (range === 'year') {
        startDate.setFullYear(now.getFullYear() - 1);
      }

      const transactions = await Transaction.find({
        created_at: { $gte: startDate }
      })
        .populate('user_id', 'username email')
        .sort({ created_at: -1 });

      // CSV Header
      let csv = 'Date,Transaction ID,User,Type,Amount,Status,Description\n';

      // CSV Rows
      transactions.forEach(tx => {
        const date = tx.created_at.toISOString().split('T')[0];
        const user = tx.user_id ? tx.user_id.username : 'Unknown';
        const type = tx.type;
        const amount = tx.amount;
        const status = tx.status;
        const description = (tx.description || '').replace(/,/g, ' '); // Escape commas

        csv += `${date},${tx._id},${user},${type},${amount},${status},${description}\n`;
      });

      res.setHeader('Content-Type', 'text/csv');
      res.setHeader('Content-Disposition', `attachment; filename=report-${range}-${Date.now()}.csv`);
      res.status(200).send(csv);

    } catch (error) {
      console.error('Error exporting data:', error);
      res.status(500).json({ message: 'Failed to export data' });
    }
  }


  /**
   * Get Payment/Webhook Logs
   * @route GET /api/admin/payment-logs
   */
  static async getPaymentLogs(req, res) {
    try {
      const { page = 1, limit = 20, search = '', status, type } = req.query;
      const skip = (page - 1) * limit;

      let query = {};

      if (search) {
        query.$or = [
          { merchant_order_id: { $regex: search, $options: 'i' } },
          { ip_address: { $regex: search, $options: 'i' } }
        ];
      }

      if (status) {
        query.processed_status = status;
      }

      if (type) {
        query.webhook_type = type;
      }

      const logs = await PaymentRecord.find(query)
        .sort({ created_at: -1 })
        .skip(skip)
        .limit(parseInt(limit));

      const total = await PaymentRecord.countDocuments(query);

      res.json({
        logs,
        total,
        page: parseInt(page),
        pages: Math.ceil(total / limit)
      });
    } catch (error) {
      console.error('Error fetching payment logs:', error);
      res.status(500).json({ message: 'Failed to fetch payment logs' });
    }
  }
}

module.exports = AdminController;
