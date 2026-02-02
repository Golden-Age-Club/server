const axios = require('axios');
const crypto = require('crypto');
const GameSetting = require('../models/GameSetting');
const { Transaction } = require('../models/Transaction');

let gamesCache = {
  data: [],
  timestamp: 0
};
let optionsCache = {
  data: null,
  timestamp: 0
};
const CACHE_DURATION = 600 * 1000; // 600 seconds in ms

class PGProviderService {
  constructor() {
    this.appId = process.env.PG_APP_ID;
    this.apiKey = process.env.PG_API_KEY;
    this.baseUrl = process.env.PG_API_BASE_URL ? process.env.PG_API_BASE_URL.replace(/\/$/, '') : '';

    if (!this.appId || !this.apiKey) {
      console.warn('PG Provider credentials missing');
    }
  }

  _createSign(requestTime) {
    const raw = `${this.appId}${requestTime}`;
    // Using encodeURIComponent then replacing strictly to match python quote(safe="")
    const encoded = encodeURIComponent(raw).replace(/[!'()*]/g, escape);
    
    return crypto
      .createHmac('md5', this.apiKey)
      .update(raw)
      .digest('hex');
  }

  async getOptions() {
    if (Date.now() - optionsCache.timestamp < CACHE_DURATION && optionsCache.data) {
        return optionsCache.data;
    }

    const requestTime = Date.now().toString();
    const sign = this._createSign(requestTime);

    const params = {
      app_id: this.appId,
      request_time: requestTime,
      sign: sign
    };

    const response = await axios.get(`${this.baseUrl}/api/v1/get-options`, { params });
    if (response.data) {
        optionsCache.data = response.data;
        optionsCache.timestamp = Date.now();
    }
    return response.data;
  }

  async _fetchGamesFromProvider() {
     // Check cache first
     if (Date.now() - gamesCache.timestamp < CACHE_DURATION && gamesCache.data.length > 0) {
         return gamesCache.data;
     }

    const requestTime = Date.now().toString();
    const sign = this._createSign(requestTime);

    const params = {
      app_id: this.appId,
      request_time: requestTime,
      sign: sign
    };

    const response = await axios.get(`${this.baseUrl}/api/v1/get-games`, { params });
    
    if (response.data && Array.isArray(response.data.games)) {
        gamesCache.data = response.data.games;
        gamesCache.timestamp = Date.now();
        return gamesCache.data;
    }
    return [];
  }

  async getGames(page = 1, limit = 20, providerId = null, search = null, offset = null) {
    let result = await this._fetchGamesFromProvider();
    
    // 1. Filter by Active Providers
    // Get active providers from options
    try {
        const options = await this.getOptions();
        if (options && options.providers) {
            const activeProviderIds = options.providers
                .filter(p => p.is_active === 1 || p.is_active === true) // Assuming 1/true is active
                .map(p => String(p.id));
            
            // Filter games whose provider is active
            result = result.filter(g => activeProviderIds.includes(String(g.provider_id)));
        }
    } catch (e) {
        console.warn("Failed to filter by provider status", e);
    }

    // 2. Filter by Local Game Settings (Disabled games)
    try {
        const disabledGames = await GameSetting.find({ status: 'disabled' }).distinct('game_id');
        if (disabledGames.length > 0) {
            result = result.filter(g => !disabledGames.includes(String(g.game_id)));
        }
    } catch (e) {
        console.warn("Failed to filter by local game settings", e);
    }

    // 3. Standard Filtering
    if (providerId) result = result.filter(g => String(g.provider_id) === String(providerId));
    if (search) result = result.filter(g => (g.name || g.title || '').toLowerCase().includes(search.toLowerCase()));
    
    const start = offset !== null ? parseInt(offset) : (page - 1) * limit;
    const end = start + limit;
    const total = result.length;
    const totalPages = Math.ceil(total / limit);
    
    return {
        games: result.slice(start, end),
        page: parseInt(page),
        limit: parseInt(limit),
        total: total,
        total_pages: totalPages
    };
  }

  // Admin Method: Get all games with stats and provider status
  async getGamesWithStats(page = 1, limit = 20, search = null) {
    let games = await this._fetchGamesFromProvider();
    
    // Get Providers to map status
    const options = await this.getOptions();
    const providerStatusMap = {};
    if (options && options.providers) {
        options.providers.forEach(p => {
            providerStatusMap[p.id] = p.is_active;
        });
    }

    // Get Local Settings
    const localSettings = await GameSetting.find({});
    const localStatusMap = {};
    localSettings.forEach(s => {
        localStatusMap[s.game_id] = s.status;
    });

    // Get Stats (Aggregated)
    const stats = await Transaction.aggregate([
        { 
            $match: { 
                type: { $in: ['game_bet', 'game_win'] } 
            } 
        },
        { 
            $group: {
                _id: '$game_id',
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
    
    const statsMap = {};
    stats.forEach(s => {
        statsMap[s._id] = s;
    });

    // Merge Data
    let result = games.map(g => {
        const pStatus = providerStatusMap[g.provider_id];
        const lStatus = localStatusMap[g.game_id] || 'enabled';
        const gStats = statsMap[g.game_id] || { totalBets: 0, betCount: 0, totalWins: 0 };
        const rtp = gStats.totalBets > 0 ? (gStats.totalWins / gStats.totalBets) * 100 : 0;

        return {
            ...g,
            provider_status: pStatus, // 1 or 0
            local_status: lStatus,
            stats: {
                total_bets: gStats.totalBets,
                bet_count: gStats.betCount,
                total_wins: gStats.totalWins,
                rtp: parseFloat(rtp.toFixed(2))
            }
        };
    });

    if (search) result = result.filter(g => (g.name || g.title || '').toLowerCase().includes(search.toLowerCase()));

    // Pagination
    const start = (page - 1) * limit;
    const end = start + limit;
    const total = result.length;
    const totalPages = Math.ceil(total / limit);

    return {
        games: result.slice(start, end),
        page: parseInt(page),
        limit: parseInt(limit),
        total: total,
        total_pages: totalPages
    };
  }

  async launchGame(gameId, playerId, playerToken, language = 'en', currency = 'USD', exitUrl, walletUrl) {
    const requestTime = Date.now(); 
    const baseUrl = walletUrl ? new URL(walletUrl).origin : 'https://google.com';

    const params = {
        exit: exitUrl,
        game_id: parseInt(gameId), 
        player_id: playerId,
        player_token: playerToken,
        app_id: this.appId,
        language: language,
        currency: currency,
        request_time: requestTime,
        urls: {
            base_url: baseUrl,
            wallet_url: walletUrl,
            other_url: `${baseUrl}/support` 
        }
    };

    const createSign = (p, apiKey) => {
        const values = Object.entries(p)
            .filter(([key]) => key !== 'sign' && key !== 'urls')
            .map(([, value]) => (value && typeof value === 'object' ? JSON.stringify(value) : value))
            .join('');
        const encoded = encodeURIComponent(values);
        return crypto.createHmac('md5', apiKey).update(encoded).digest('hex');
    };

    params.sign = createSign(params, this.apiKey);

    const launchBaseUrl = 'https://resolver.mgcapi.com';
    
    console.log(`[PGProvider] Launching game ${gameId} for user ${playerId}`);
    
    try {
      const response = await axios.post(`${launchBaseUrl}/api/v1/launch-game`, params);
      return response.data;
    } catch (error) {
      console.error('[PGProvider] Launch game error:', error.message);
      if (error.response) {
        console.error('[PGProvider] Error response data:', JSON.stringify(error.response.data, null, 2));
      }
      throw error;
    }
  }
}

module.exports = new PGProviderService();
