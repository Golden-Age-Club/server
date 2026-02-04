/**
 * Frontend API Client for Golden Age CRM
 * 
 * Features:
 * - Automatic token management
 * - Token refresh on 401 errors
 * - Request/response interceptors
 * - Error handling
 */

import axios from 'axios';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1/admin';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Request interceptor - add token to all requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - handle token refresh
apiClient.interceptors.response.use(
  (response) => {
    // Return the data object directly for easier access
    return response.data;
  },
  async (error) => {
    const originalRequest = error.config;

    // If error is 401 and we haven't tried to refresh yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const refreshToken = localStorage.getItem('refresh_token');

      if (refreshToken) {
        try {
          // Try to refresh the token
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token, refresh_token: newRefreshToken } = response.data.data;

          // Store new tokens
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', newRefreshToken);

          // Retry the original request with new token
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          const retriedResponse = await axios(originalRequest);
          return retriedResponse.data;
        } catch (refreshError) {
          // Refresh failed, clear tokens and redirect to login
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/auth/sign-in';
          return Promise.reject(refreshError);
        }
      } else {
        // No refresh token, redirect to login
        window.location.href = '/auth/sign-in';
      }
    }

    // Handle other errors
    const errorMessage = error.response?.data?.error?.message || error.message || 'An error occurred';
    return Promise.reject(new Error(errorMessage));
  }
);

// Auth API
export const authAPI = {
  /**
   * Login with username and password
   * @param {string} username
   * @param {string} password
   * @returns {Promise<{access_token, refresh_token, user}>}
   */
  login: async (username, password) => {
    const response = await apiClient.post('/auth/login', { username, password });

    // Store tokens
    if (response.success && response.data) {
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('refresh_token', response.data.refresh_token);
    }

    return response;
  },

  /**
   * Get current user information
   * @returns {Promise<{admin_id, username, email, role, permissions}>}
   */
  getCurrentUser: async () => {
    const response = await apiClient.get('/auth/me');
    return response;
  },

  /**
   * Logout current user
   */
  logout: async () => {
    try {
      await apiClient.post('/auth/logout');
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  },

  /**
   * Setup MFA (TOTP)
   * @returns {Promise<{secret, qr_code, provisioning_uri}>}
   */
  setupMFA: async () => {
    const response = await apiClient.post('/auth/mfa/setup');
    return response;
  },

  /**
   * Enable MFA with verification code
   * @param {string} code - 6-digit TOTP code
   */
  enableMFA: async (code) => {
    const response = await apiClient.post('/auth/mfa/enable', { code });
    return response;
  },

  /**
   * Verify MFA code
   * @param {string} code - 6-digit TOTP code
   */
  verifyMFA: async (code) => {
    const response = await apiClient.post('/auth/mfa/verify', { code });
    return response;
  },
};

// Admin Management API
export const adminAPI = {
  /**
   * List all admins
   * @param {Object} filters - { status, role, search, page, page_size }
   */
  list: async (filters = {}) => {
    const response = await apiClient.get('/admins', { params: filters });
    return response;
  },

  /**
   * Get admin by ID
   * @param {string} adminId
   */
  get: async (adminId) => {
    const response = await apiClient.get(`/admins/${adminId}`);
    return response;
  },

  /**
   * Create new admin
   * @param {Object} data - { username, email, password, roles }
   */
  create: async (data) => {
    const response = await apiClient.post('/admins', data);
    return response;
  },

  /**
   * Update admin
   * @param {string} adminId
   * @param {Object} data - { email, roles }
   */
  update: async (adminId, data) => {
    const response = await apiClient.patch(`/admins/${adminId}`, data);
    return response;
  },

  /**
   * Update admin status
   * @param {string} adminId
   * @param {string} status - 'active' or 'suspended'
   * @param {string} reason - Optional reason
   */
  updateStatus: async (adminId, status, reason = null) => {
    const response = await apiClient.patch(`/admins/${adminId}/status`, { status, reason });
    return response;
  },

  /**
   * Delete admin (soft delete)
   * @param {string} adminId
   */
  delete: async (adminId) => {
    const response = await apiClient.delete(`/admins/${adminId}`);
    return response;
  },
};

// Player Management API
export const playerAPI = {
  /**
   * List all players
   * @param {Object} filters - { status, search, page, page_size }
   */
  list: async (filters = {}) => {
    const response = await apiClient.get('/players', { params: filters });
    return response;
  },

  /**
   * Get player by ID
   * @param {string} playerId
   */
  get: async (playerId) => {
    const response = await apiClient.get(`/players/${playerId}`);
    return response;
  },

  /**
   * Create new player
   * @param {Object} data - { username, password, email, ... }
   */
  create: async (data) => {
    const response = await apiClient.post('/players', data);
    return response;
  },

  /**
   * Update player
   * @param {string} playerId
   * @param {Object} data
   */
  update: async (playerId, data) => {
    const response = await apiClient.patch(`/players/${playerId}`, data);
    return response;
  },
};

// Game Management API
export const gameAPI = {
  /**
   * List all games
   * @param {Object} params - { status, search, page, page_size }
   */
  list: async (params) => {
    const response = await apiClient.get('/games', { params });
    return response;
  },
  /**
   * Create new game
   * @param {Object} data - { name, description, ... }
   */
  create: async (data) => {
    const response = await apiClient.post('/games', data);
    return response;
  },
  /**
   * Update game
   * @param {string} id
   * @param {Object} data
   */
  update: async (id, data) => {
    const response = await apiClient.patch(`/games/${id}`, data);
    return response;
  },
  /**
   * Delete game (soft delete)
   * @param {string} id
   */
  delete: async (id) => {
    await apiClient.delete(`/games/${id}`);
  }
};

// Dashboard Statistics API
export const statsAPI = {
  getOverview: async () => {
    const response = await apiClient.get('/stats/overview');
    return response;
  },
};

// Finance API
export const financeAPI = {
  /**
   * List transactions
   * @param {Object} params - { player_id, type, page, page_size }
   */
  list: async (params = {}) => {
    const response = await apiClient.get('/finance/transactions', { params });
    return response;
  },
  /**
   * Manual balance adjustment
   * @param {Object} data - { player_id, amount, type, remarks }
   */
  adjust: async (data) => {
    const response = await apiClient.post('/finance/adjust', data);
    return response;
  },
  /**
   * List pending approvals
   */
  getPendingApprovals: async () => {
    const response = await apiClient.get('/finance/approvals/pending');
    return response;
  },
  /**
   * Approve a transaction
   * @param {string} id
   */
  approveTransaction: async (id) => {
    const response = await apiClient.post(`/finance/approvals/${id}/approve`);
    return response;
  },
  /**
   * Reject a transaction
   * @param {string} id
   */
  rejectTransaction: async (id) => {
    const response = await apiClient.post(`/finance/approvals/${id}/reject`);
    return response;
  },
  /**
   * Request a withdrawal
   * @param {Object} data - { player_id, amount, remarks }
   */
  requestWithdrawal: async (data) => {
    const response = await apiClient.post('/finance/withdrawals/request', data);
    return response;
  },
};

// Audit API
export const auditAPI = {
  /**
   * List audit logs
   * @param {Object} params - { admin_id, action, resource_type, page, page_size }
   */
  listLogs: async (params = {}) => {
    const response = await apiClient.get('/audit/logs', { params });
    return response;
  },

  /**
   * List payment (webhook) logs
   * @param {Object} params - { page, limit }
   */
  listPaymentLogs: async (params = {}) => {
    const response = await apiClient.get('/payment-logs', { params });
    return response;
  },
};

// VIP Management API
export const vipAPI = {
  /**
   * Get VIP configurations
   */
  getConfigs: async () => {
    const response = await apiClient.get('/vip/configs');
    return response;
  },
  /**
   * Update VIP configurations
   * @param {Array} tiers
   */
  updateConfigs: async (tiers) => {
    const response = await apiClient.put('/vip/configs', { tiers });
    return response;
  },
  /**
   * Get high-value players
   */
  getHighValuePlayers: async () => {
    const response = await apiClient.get('/vip/high-value');
    return response;
  },
  /**
   * Manually adjust player VIP level
   * @param {Object} data - { player_id, new_level, reason }
   */
  adjustPlayerVIP: async (data) => {
    const response = await apiClient.post('/vip/adjust-level', data);
    return response;
  },
};

// Risk Management API
export const riskAPI = {
  getRules: async () => {
    const response = await apiClient.get('/risk/rules');
    return response;
  },
  getAlerts: async () => {
    const response = await apiClient.get('/risk/alerts');
    return response;
  }
};

// Promotions Management API
export const promotionsAPI = {
  list: async () => {
    const response = await apiClient.get('/promotions/');
    return response;
  },
  create: async (data) => {
    const response = await apiClient.post('/promotions/', data);
    return response;
  }
};

export default apiClient;
