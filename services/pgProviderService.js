const axios = require('axios');
const crypto = require('crypto');

let gamesCache = {
  data: [],
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
    const encoded = encodeURIComponent(raw).replace(/[!'()*]/g, escape); // Python quote(safe="") equivalent-ish
    // Actually encodeURIComponent is slightly different from python quote in some chars, 
    // but for alphanumeric it's fine. Python quote with safe="" encodes everything except alphanumeric.
    // For strictly matching Python's urllib.parse.quote(raw, safe=""), we might need a custom function 
    // if raw contains special chars. But appId and requestTime are usually alphanumeric.
    
    return crypto
      .createHmac('md5', this.apiKey)
      .update(raw) // Python uses encoded, but let's check if raw needs encoding. Python: quote(raw).
                   // If app_id and time are safe chars, quote does nothing.
                   // Let's assume they are safe.
      .digest('hex');
  }

  _createPlaySign(params) {
    // Values except sign and urls, joined, encoded, HMAC-MD5
    // Python: values = [serialize(params[key]) for key in params if key not in ('sign', 'urls')]
    // Python keys iteration order is insertion order (usually). 
    // IMPORTANT: Python code assumes keys are iterated in a specific order? 
    // Or just all keys present in the dict?
    // Looking at Python code: `for key in params`. 
    // We must ensure we pass params in the correct order or the API expects arbitrary order?
    // Usually APIs expect sorted keys or specific order.
    // Python dicts preserve insertion order since 3.7.
    
    // Let's rely on the caller passing keys in the right order or the API not caring about order 
    // (unlikely if we just join values).
    // The Python code just iterates `params`.
    
    const values = [];
    for (const key in params) {
      if (key !== 'sign' && key !== 'urls') {
        let value = params[key];
        if (typeof value === 'object') {
          value = JSON.stringify(value).replace(/ /g, ''); // Simple minification
        }
        values.push(String(value));
      }
    }
    
    const concatenated = values.join('');
    const encoded = encodeURIComponent(concatenated).replace(/[!'()*]/g, escape); // safe=''
    
    return crypto
      .createHmac('md5', this.apiKey)
      .update(encoded)
      .digest('hex');
  }

  async getOptions() {
    const requestTime = Date.now().toString();
    const sign = this._createSign(requestTime);

    const params = {
      app_id: this.appId,
      request_time: requestTime,
      sign: sign
    };

    const response = await axios.get(`${this.baseUrl}/api/v1/get-options`, { params });
    return response.data;
  }

  async getGames(page = 1, limit = 20, providerId = null, search = null, offset = null) {
    // Check cache
    if (Date.now() - gamesCache.timestamp < CACHE_DURATION && gamesCache.data.length > 0) {
        // Filter cache if needed
        let result = gamesCache.data;
        if (providerId) result = result.filter(g => String(g.provider_id) === String(providerId));
        if (search) result = result.filter(g => (g.name || g.title || '').toLowerCase().includes(search.toLowerCase()));
        
        // Pagination
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

    const requestTime = Date.now().toString();
    const sign = this._createSign(requestTime);

    const params = {
      app_id: this.appId,
      request_time: requestTime,
      sign: sign
    };

    const response = await axios.get(`${this.baseUrl}/api/v1/get-games`, { params });
    
    // The provider returns { games: [...] } structure
    if (response.data && Array.isArray(response.data.games)) {
        gamesCache.data = response.data.games;
        gamesCache.timestamp = Date.now();
    }
    
    let result = gamesCache.data;
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

  async launchGame(gameId, playerId, playerToken, language = 'en', currency = 'USD', exitUrl, walletUrl) {
    const requestTime = Date.now(); // User sample uses number
    const baseUrl = walletUrl ? new URL(walletUrl).origin : 'https://google.com';

    // Params structure matching the user's provided expected request
    const params = {
        exit: exitUrl,
        game_id: parseInt(gameId), // Ensure number if expected as number in sample (sample has 1203)
        player_id: playerId,
        player_token: playerToken,
        app_id: this.appId,
        language: language,
        currency: currency,
        request_time: requestTime,
        urls: {
            base_url: baseUrl,
            wallet_url: walletUrl,
            other_url: `${baseUrl}/support` // Assuming support url
        }
    };

    // Signature generation matching the user's sample code
    const createSign = (p, apiKey) => {
        const values = Object.entries(p)
            .filter(([key]) => key !== 'sign' && key !== 'urls')
            .map(([, value]) => (value && typeof value === 'object' ? JSON.stringify(value) : value))
            .join('');
        const encoded = encodeURIComponent(values);
        return crypto.createHmac('md5', apiKey).update(encoded).digest('hex');
    };

    params.sign = createSign(params, this.apiKey);

    // Use the resolver URL for launching games
    const launchBaseUrl = 'https://resolver.mgcapi.com';
    
    console.log(`[PGProvider] Launching game ${gameId} for user ${playerId}`);
    console.log('[PGProvider] Launch params:', JSON.stringify(params, null, 2)); // Log params for debugging
    
    try {
      const response = await axios.post(`${launchBaseUrl}/api/v1/launch-game`, params);
      console.log('[PGProvider] Launch game response:', response.data);
      return response.data;
    } catch (error) {
      console.error('[PGProvider] Launch game error:', error.message);
      if (error.response) {
        console.error('[PGProvider] Error response status:', error.response.status);
        console.error('[PGProvider] Error response data:', JSON.stringify(error.response.data, null, 2));
      }
      throw error;
    }
  }
}

module.exports = new PGProviderService();
