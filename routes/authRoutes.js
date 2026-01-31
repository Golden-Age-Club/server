const express = require('express');
const router = express.Router();
const { loginTelegram, registerEmail, loginEmail } = require('../controllers/authController');

router.post('/login/telegram', loginTelegram);
router.post('/register/email', registerEmail);
router.post('/login/email', loginEmail);

module.exports = router;
