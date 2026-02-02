const jwt = require('jsonwebtoken');
const Admin = require('../models/Admin');

const protectAdmin = async (req, res, next) => {
  let token;

  if (
    req.headers.authorization &&
    req.headers.authorization.startsWith('Bearer')
  ) {
    try {
      // Get token from header
      token = req.headers.authorization.split(' ')[1];

      // Verify token
      const decoded = jwt.verify(token, process.env.JWT_SECRET_KEY);

      // Check if token is for admin
      if (!decoded.role || !['super_admin', 'admin', 'moderator'].includes(decoded.role)) {
         return res.status(403).json({ message: 'Not authorized, invalid role' });
      }

      // Get admin from the token
      req.admin = await Admin.findById(decoded.id).select('-password_hash');

      if (!req.admin) {
        return res.status(401).json({ message: 'Not authorized, admin not found' });
      }

      next();
    } catch (error) {
      console.error(error);
      res.status(401).json({ message: 'Not authorized, token failed' });
    }
  }

  if (!token) {
    res.status(401).json({ message: 'Not authorized, no token' });
  }
};

const checkPermission = (requiredPermission) => {
  return (req, res, next) => {
    // Ensure admin is attached (should be used after protectAdmin)
    if (!req.admin) {
      return res.status(401).json({ message: 'Not authorized, user not found' });
    }

    // Super admin has all permissions
    if (req.admin.role === 'super_admin') {
      return next();
    }

    // Check if admin has the required permission
    if (req.admin.permissions && req.admin.permissions.includes(requiredPermission)) {
      return next();
    }

    // If neither, deny access
    return res.status(403).json({ 
      message: `Access denied. Requires '${requiredPermission}' permission.` 
    });
  };
};

module.exports = { protectAdmin, checkPermission };
