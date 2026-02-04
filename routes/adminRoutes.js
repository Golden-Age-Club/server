const express = require('express');
const router = express.Router();
const AdminController = require('../controllers/adminController');
const AdminGameController = require('../controllers/adminGameController');
const RiskController = require('../controllers/RiskController');
const PromotionController = require('../controllers/PromotionController');
const SystemController = require('../controllers/SystemController');
const { protectAdmin, checkPermission } = require('../middleware/adminMiddleware');

// Public routes
router.post('/auth/login', AdminController.login);

// Protected routes
router.get('/auth/me', protectAdmin, AdminController.getProfile);
router.put('/auth/profile', protectAdmin, AdminController.updateProfile);
router.put('/auth/password', protectAdmin, AdminController.updatePassword);
router.get('/stats', protectAdmin, checkPermission('dashboard'), AdminController.getDashboardStats);
router.get('/charts', protectAdmin, checkPermission('dashboard'), AdminController.getChartStats);
router.get('/export', protectAdmin, checkPermission('dashboard'), AdminController.exportData);
router.get('/payment-logs', protectAdmin, AdminController.getPaymentLogs);


// User Management
router.get('/users/stats', protectAdmin, checkPermission('users'), AdminController.getUserStats);
router.get('/users', protectAdmin, checkPermission('users'), AdminController.getUsers);
router.post('/users', protectAdmin, checkPermission('users'), AdminController.createUser);
router.get('/users/:id', protectAdmin, checkPermission('users'), AdminController.getUser);
router.put('/users/:id', protectAdmin, checkPermission('users'), AdminController.updateUser);
router.delete('/users/:id', protectAdmin, checkPermission('users'), AdminController.deleteUser);

// Bets & Games Management
router.get('/bets', protectAdmin, checkPermission('bets'), AdminGameController.getBets);
router.get('/games', protectAdmin, checkPermission('bets'), AdminGameController.getGames);
router.post('/games/toggle', protectAdmin, checkPermission('bets'), AdminGameController.toggleGame);

// Risk Management
router.get('/risk/users', protectAdmin, checkPermission('risk'), RiskController.getAbnormalUsers);
router.get('/risk/rules', protectAdmin, checkPermission('risk'), RiskController.getRiskRules);
router.get('/risk/history', protectAdmin, checkPermission('risk'), RiskController.getRiskHistory);
router.post('/risk/action', protectAdmin, checkPermission('risk'), RiskController.takeAction);

// VIP Management
router.get('/vip/tiers', protectAdmin, checkPermission('vip'), AdminController.getVipTiers);
router.post('/vip/tiers', protectAdmin, checkPermission('vip'), AdminController.updateVipTier);
router.get('/vip/users', protectAdmin, checkPermission('vip'), AdminController.getVipUsers);

// Promotions & Bonuses
router.get('/promotions', protectAdmin, checkPermission('promotions'), PromotionController.getPromotions);
router.post('/promotions', protectAdmin, checkPermission('promotions'), PromotionController.createPromotion);
router.put('/promotions/:id', protectAdmin, checkPermission('promotions'), PromotionController.updatePromotion);
router.delete('/promotions/:id', protectAdmin, checkPermission('promotions'), PromotionController.deletePromotion);
router.get('/promotions/user-bonuses', protectAdmin, checkPermission('promotions'), PromotionController.getUserBonuses);
router.post('/promotions/assign', protectAdmin, checkPermission('promotions'), PromotionController.assignBonus);

// System Management
router.get('/system/settings', protectAdmin, checkPermission('system'), SystemController.getSettings);
router.put('/system/settings', protectAdmin, checkPermission('system'), SystemController.updateSettings);
router.get('/system/logs', protectAdmin, checkPermission('system'), SystemController.getLogs);
router.get('/system/admins', protectAdmin, checkPermission('system'), SystemController.getAdmins);
router.post('/system/admins', protectAdmin, checkPermission('system'), SystemController.createAdmin);
router.put('/system/admins/:id', protectAdmin, checkPermission('system'), SystemController.updateAdmin);
router.delete('/system/admins/:id', protectAdmin, checkPermission('system'), SystemController.deleteAdmin);

module.exports = router;
