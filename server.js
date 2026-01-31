require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 8000;

// Middleware
const allowedOrigins = process.env.ALLOWED_ORIGINS 
  ? process.env.ALLOWED_ORIGINS.split(',') 
  : [];

app.use(cors({
  origin: allowedOrigins,
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With']
}));

app.use(express.json());

// MongoDB Connection
const connectDB = async () => {
  try {
    const mongoUrl = process.env.MONGODB_URL;
    if (!mongoUrl) {
      throw new Error('MONGODB_URL is not defined in .env');
    }

    // Simplified connection options for troubleshooting
    await mongoose.connect(mongoUrl);
    
    console.log(`Connected to MongoDB: ${mongoUrl.split('@')[1]}`); // Log only the host part for security
  } catch (error) {
    console.error('MongoDB connection error:', error);
    process.exit(1);
  }
};

const authRoutes = require('./routes/authRoutes');
const userRoutes = require('./routes/userRoutes');
const casinoRoutes = require('./routes/casinoRoutes');
const walletRoutes = require('./routes/walletRoutes');
const transactionRoutes = require('./routes/transactionRoutes');
const supportRoutes = require('./routes/supportRoutes');
const webhookRoutes = require('./routes/webhookRoutes');

// Routes
app.use('/api/auth', authRoutes);
app.use('/api/users', userRoutes);
app.use('/api/casino', casinoRoutes);
app.use('/api/wallet', walletRoutes);
app.use('/api/transactions', transactionRoutes);
app.use('/api/support', supportRoutes);
app.use('/api', webhookRoutes);

app.get('/', (req, res) => {
  res.json({
    message: "Golden Age USDT Wallet API (Node.js)",
    version: "1.0.0",
    testing_mode: process.env.TESTING_MODE === 'true',
    docs: "/docs",
    health: "/health"
  });
});

app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    database: mongoose.connection.readyState === 1 ? 'connected' : 'disconnected'
  });
});

// Start Server
const startServer = async () => {
  await connectDB();
  app.listen(PORT, () => {
    console.log(`🚀 Server running on http://localhost:${PORT}`);
    console.log(`Allowed origins: ${allowedOrigins.join(', ')}`);
  });
};

startServer();
