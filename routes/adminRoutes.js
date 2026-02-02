const express = require('express');
const router = express.Router();
const AdminController = require('../controllers/adminController');
const { protectAdmin } = require('../middleware/adminMiddleware');

// Public routes
router.post('/auth/login', AdminController.login);

// Protected routes
router.get('/auth/me', protectAdmin, AdminController.getProfile);
router.put('/auth/profile', protectAdmin, AdminController.updateProfile);
router.put('/auth/password', protectAdmin, AdminController.updatePassword);
router.get('/stats', protectAdmin, AdminController.getDashboardStats);
router.get('/charts', AdminController.getChartStats);

module.exports = router;
