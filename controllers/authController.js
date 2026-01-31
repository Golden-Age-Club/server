const User = require('../models/User');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const { validateTelegramWebAppData, parseTelegramUser } = require('../utils/telegramAuth');

// Generate JWT
const generateToken = (id, telegram_id) => {
  return jwt.sign({ user_id: id, telegram_id }, process.env.JWT_SECRET_KEY, {
    expiresIn: '30d',
  });
};

// @desc    Authenticate user with Telegram WebApp initData
// @route   POST /api/auth/login/telegram
// @access  Public
const loginTelegram = async (req, res) => {
  const { init_data } = req.body;

  if (!init_data) {
    return res.status(400).json({ message: 'Missing init_data' });
  }

  try {
    let userData;

    if (process.env.TESTING_MODE === 'true') {
      // Testing mode logic
      try {
        const telegramId = parseInt(init_data);
        userData = {
          telegram_id: telegramId,
          username: `test_user_${telegramId}`,
          first_name: "Test",
          last_name: "User"
        };
      } catch (error) {
        return res.status(401).json({ message: "Invalid telegram_id in testing mode" });
      }
    } else {
      // Production validation
      try {
        const validatedData = validateTelegramWebAppData(init_data, process.env.TELEGRAM_BOT_TOKEN);
        userData = parseTelegramUser(validatedData);
      } catch (error) {
        return res.status(401).json({ message: error.message });
      }
    }

    const { telegram_id } = userData;
    console.log(`Login attempt for telegram_id: ${telegram_id}`);

    let user = await User.findOne({ telegram_id });

    if (!user) {
      console.log(`Creating new user: ${telegram_id}`);
      user = await User.create(userData);
    } else {
      // Update user info
      user.username = userData.username || user.username;
      user.first_name = userData.first_name || user.first_name;
      user.last_name = userData.last_name || user.last_name;
      user.photo_url = userData.photo_url || user.photo_url;
      user.language_code = userData.language_code || 'en';
      if (userData.is_premium !== undefined) user.is_premium = userData.is_premium;
      
      await user.save();
    }

    res.json({
      access_token: generateToken(user._id, user.telegram_id),
      token_type: "bearer",
      user: {
        _id: user._id,
        telegram_id: user.telegram_id,
        username: user.username,
        first_name: user.first_name,
        last_name: user.last_name,
        balance: user.balance,
        is_active: user.is_active,
        is_premium: user.is_premium,
        language_code: user.language_code,
        photo_url: user.photo_url
      }
    });

  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ message: 'Server error during login' });
  }
};

// @desc    Register new user with Email/Password
// @route   POST /api/auth/register/email
// @access  Public
const registerEmail = async (req, res) => {
  const { email, username, password, first_name, last_name } = req.body;

  if (!email || !username || !password) {
    return res.status(400).json({ message: 'Please add all required fields' });
  }

  try {
    // Check email
    const userExists = await User.findOne({ email });
    if (userExists) {
      return res.status(400).json({ message: 'Email already registered' });
    }

    // Check username
    const usernameExists = await User.findOne({ username });
    if (usernameExists) {
      return res.status(400).json({ message: 'Username already taken' });
    }

    // Hash password
    const salt = await bcrypt.genSalt(10);
    const passwordHash = await bcrypt.hash(password, salt);

    // Create user
    const user = await User.create({
      email,
      username,
      password_hash: passwordHash,
      first_name,
      last_name
    });

    if (user) {
      res.status(201).json({
        access_token: generateToken(user._id, null),
        token_type: "bearer",
        user: {
          _id: user._id,
          email: user.email,
          username: user.username,
          first_name: user.first_name,
          last_name: user.last_name,
          balance: user.balance
        }
      });
    } else {
      res.status(400).json({ message: 'Invalid user data' });
    }
  } catch (error) {
    console.error('Registration error:', error);
    res.status(500).json({ message: 'Server error during registration' });
  }
};

// @desc    Login user with Email/Password
// @route   POST /api/auth/login/email
// @access  Public
const loginEmail = async (req, res) => {
  const { email, password } = req.body;

  if (!email || !password) {
    return res.status(400).json({ message: 'Please add email and password' });
  }

  try {
    // Check for user email
    const user = await User.findOne({ email });

    if (user && (await bcrypt.compare(password, user.password_hash))) {
      res.json({
        access_token: generateToken(user._id, null),
        token_type: "bearer",
        user: {
          _id: user._id,
          email: user.email,
          username: user.username,
          first_name: user.first_name,
          last_name: user.last_name,
          balance: user.balance
        }
      });
    } else {
      res.status(400).json({ message: 'Invalid credentials' });
    }
  } catch (error) {
    console.error('Email login error:', error);
    res.status(500).json({ message: 'Server error during login' });
  }
};

module.exports = {
  loginTelegram,
  registerEmail,
  loginEmail
};
