const express = require('express');
const router = express.Router();
const { getTopUsers, getMe } = require('../controllers/userController');
const { protect } = require('../middleware/authMiddleware');

router.get('/top-users', getTopUsers);
router.get('/me', protect, getMe);

module.exports = router;
