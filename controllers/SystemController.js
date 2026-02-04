const SystemSetting = require('../models/SystemSetting');
const SystemLog = require('../models/SystemLog');
const Admin = require('../models/Admin');
const bcrypt = require('bcryptjs');

class SystemController {
  
  // --- Settings ---

  /**
   * Get all system settings
   * @route GET /api/admin/system/settings
   */
  static async getSettings(req, res) {
    try {
      const settings = await SystemSetting.find({});
      // Convert array to object for easier frontend consumption { key: value }
      // Or return list if we want to edit them with metadata
      res.json(settings);
    } catch (error) {
      console.error('Error fetching settings:', error);
      res.status(500).json({ message: 'Server error fetching settings' });
    }
  }

  /**
   * Update system settings (batch)
   * @route PUT /api/admin/system/settings
   */
  static async updateSettings(req, res) {
    try {
      const updates = req.body; // Expects object { key: value } or array of updates

      const results = [];
      for (const [key, value] of Object.entries(updates)) {
        const setting = await SystemSetting.findOneAndUpdate(
          { key },
          { value },
          { new: true, upsert: true, setDefaultsOnInsert: true }
        );
        results.push(setting);
      }

      // Log action
      await SystemLog.create({
        admin_id: req.admin._id,
        action: 'UPDATE_SETTINGS',
        target: 'System Settings',
        details: updates,
        ip_address: req.ip,
        user_agent: req.get('User-Agent')
      });

      res.json(results);
    } catch (error) {
      console.error('Error updating settings:', error);
      res.status(500).json({ message: 'Server error updating settings' });
    }
  }

  /**
   * Initialize default settings (helper)
   */
  static async initDefaultSettings() {
    const defaults = [
      { key: 'maintenanceMode', value: false, label: 'Maintenance Mode', category: 'general', description: 'Enable maintenance mode for system updates' },
      { key: 'autoBackup', value: true, label: 'Auto Backup', category: 'general', description: 'Enable automatic daily backups' },
      { key: 'emailNotifications', value: true, label: 'Email Notifications', category: 'notifications', description: 'Send system notifications via email' },
      { key: 'userRegistration', value: true, label: 'User Registration', category: 'security', description: 'Allow new user registrations' },
      { key: 'maxLoginAttempts', value: 5, label: 'Max Login Attempts', category: 'security', description: 'Maximum failed login attempts before account lockout' },
      { key: 'sessionTimeout', value: 30, label: 'Session Timeout (minutes)', category: 'security', description: 'Time before user session expires' },
      { key: 'payment_min_deposit', value: 10.0, label: 'Min Deposit Amount (USDT)', category: 'payment', description: 'Minimum allowed deposit amount' },
      { key: 'payment_max_deposit', value: 100000.0, label: 'Max Deposit Amount (USDT)', category: 'payment', description: 'Maximum allowed deposit amount' },
      { key: 'payment_min_withdrawal', value: 10.0, label: 'Min Withdrawal Amount (USDT)', category: 'payment', description: 'Minimum allowed withdrawal amount' },
      { key: 'payment_max_withdrawal', value: 50000.0, label: 'Max Withdrawal Amount (USDT)', category: 'payment', description: 'Maximum allowed withdrawal amount' },
    ];

    for (const def of defaults) {
      await SystemSetting.findOneAndUpdate(
        { key: def.key },
        { $setOnInsert: def },
        { upsert: true }
      );
    }
  }

  // --- Logs ---

  /**
   * Get system logs
   * @route GET /api/admin/system/logs
   */
  static async getLogs(req, res) {
    try {
      const { page = 1, limit = 20, action } = req.query;
      const query = {};
      if (action) query.action = action;

      const logs = await SystemLog.find(query)
        .populate('admin_id', 'first_name last_name email')
        .sort({ created_at: -1 })
        .limit(limit * 1)
        .skip((page - 1) * limit);

      const count = await SystemLog.countDocuments(query);

      res.json({
        logs,
        totalPages: Math.ceil(count / limit),
        currentPage: page
      });
    } catch (error) {
      console.error('Error fetching logs:', error);
      res.status(500).json({ message: 'Server error fetching logs' });
    }
  }

  // --- Admin Management ---

  /**
   * Get all admins
   * @route GET /api/admin/system/admins
   */
  static async getAdmins(req, res) {
    try {
      const admins = await Admin.find({}).select('-password_hash');
      res.json(admins);
    } catch (error) {
      console.error('Error fetching admins:', error);
      res.status(500).json({ message: 'Server error fetching admins' });
    }
  }

  /**
   * Create new admin
   * @route POST /api/admin/system/admins
   */
  static async createAdmin(req, res) {
    try {
      // Only super_admin can create admins
      if (req.admin.role !== 'super_admin') {
        return res.status(403).json({ message: 'Not authorized' });
      }

      const { email, password, first_name, last_name, role, permissions } = req.body;

      const existingAdmin = await Admin.findOne({ email });
      if (existingAdmin) {
        return res.status(400).json({ message: 'Admin with this email already exists' });
      }

      const salt = await bcrypt.genSalt(10);
      const password_hash = await bcrypt.hash(password, salt);

      const newAdmin = await Admin.create({
        email,
        password_hash,
        first_name,
        last_name,
        role: role || 'admin',
        permissions: permissions || [],
        verified: true
      });

      // Log action
      await SystemLog.create({
        admin_id: req.admin._id,
        action: 'CREATE_ADMIN',
        target: `Admin: ${email}`,
        ip_address: req.ip,
        user_agent: req.get('User-Agent')
      });

      const adminResponse = newAdmin.toObject();
      delete adminResponse.password_hash;

      res.status(201).json(adminResponse);
    } catch (error) {
      console.error('Error creating admin:', error);
      res.status(500).json({ message: 'Server error creating admin' });
    }
  }

  /**
   * Update admin
   * @route PUT /api/admin/system/admins/:id
   */
  static async updateAdmin(req, res) {
    try {
      if (req.admin.role !== 'super_admin') {
        return res.status(403).json({ message: 'Not authorized' });
      }

      const { first_name, last_name, role, permissions, password } = req.body;
      const updateData = { first_name, last_name, role, permissions };

      if (password) {
        const salt = await bcrypt.genSalt(10);
        updateData.password_hash = await bcrypt.hash(password, salt);
      }

      const updatedAdmin = await Admin.findByIdAndUpdate(
        req.params.id,
        updateData,
        { new: true }
      ).select('-password_hash');

      if (!updatedAdmin) {
        return res.status(404).json({ message: 'Admin not found' });
      }

      // Log action
      await SystemLog.create({
        admin_id: req.admin._id,
        action: 'UPDATE_ADMIN',
        target: `Admin: ${updatedAdmin.email}`,
        details: { role, permissions },
        ip_address: req.ip,
        user_agent: req.get('User-Agent')
      });

      res.json(updatedAdmin);
    } catch (error) {
      console.error('Error updating admin:', error);
      res.status(500).json({ message: 'Server error updating admin' });
    }
  }

  /**
   * Delete admin
   * @route DELETE /api/admin/system/admins/:id
   */
  static async deleteAdmin(req, res) {
    try {
      if (req.admin.role !== 'super_admin') {
        return res.status(403).json({ message: 'Not authorized' });
      }

      if (req.params.id === req.admin._id.toString()) {
        return res.status(400).json({ message: 'Cannot delete yourself' });
      }

      const admin = await Admin.findByIdAndDelete(req.params.id);
      
      if (!admin) {
        return res.status(404).json({ message: 'Admin not found' });
      }

      // Log action
      await SystemLog.create({
        admin_id: req.admin._id,
        action: 'DELETE_ADMIN',
        target: `Admin: ${admin.email}`,
        ip_address: req.ip,
        user_agent: req.get('User-Agent')
      });

      res.json({ message: 'Admin deleted successfully' });
    } catch (error) {
      console.error('Error deleting admin:', error);
      res.status(500).json({ message: 'Server error deleting admin' });
    }
  }
}

module.exports = SystemController;
