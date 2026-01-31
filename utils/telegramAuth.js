const crypto = require('crypto');

/**
 * Validate Telegram WebApp initData using HMAC-SHA256
 * 
 * @param {string} initData - The initData string from Telegram WebApp
 * @param {string} botToken - Your Telegram bot token
 * @param {number} maxAge - Maximum age of the data in seconds (default 24 hours)
 * @returns {Object|null} - Parsed data if valid, null otherwise
 */
const validateTelegramWebAppData = (initData, botToken, maxAge = 86400) => {
  try {
    if (!initData) {
      throw new Error('Missing initData');
    }

    // Parse the init_data string
    const urlParams = new URLSearchParams(initData);
    const parsedData = {};
    for (const [key, value] of urlParams.entries()) {
      parsedData[key] = value;
    }

    // Extract hash
    const receivedHash = parsedData.hash;
    if (!receivedHash) {
      throw new Error('Missing hash in initData');
    }

    // Remove hash from data to be checked
    delete parsedData.hash;

    // Check data freshness
    const authDate = parseInt(parsedData.auth_date);
    if (isNaN(authDate)) {
      throw new Error('Missing or invalid auth_date');
    }

    const currentTimestamp = Math.floor(Date.now() / 1000);
    if (currentTimestamp - authDate > maxAge) {
      throw new Error(`initData is too old. Max age: ${maxAge} seconds`);
    }

    // Create data check string
    // Data-check-string is a chain of all received fields, sorted alphabetically, 
    // in the format key=<value> with a line feed character ('\n') as separator
    const dataCheckArr = Object.keys(parsedData)
      .sort()
      .map(key => `${key}=${parsedData[key]}`);
    
    const dataCheckString = dataCheckArr.join('\n');

    // Calculate secret key
    // The secret key is the HMAC-SHA256 of the bot token, with "WebAppData" as the key
    const secretKey = crypto
      .createHmac('sha256', 'WebAppData')
      .update(botToken)
      .digest();

    // Calculate hash
    const calculatedHash = crypto
      .createHmac('sha256', secretKey)
      .update(dataCheckString)
      .digest('hex');

    // Compare hashes
    if (calculatedHash !== receivedHash) {
      throw new Error('Invalid initData hash');
    }

    return parsedData;
  } catch (error) {
    console.error('Telegram validation error:', error.message);
    throw error;
  }
};

/**
 * Parse Telegram user data from validated initData
 * 
 * @param {Object} validatedData - Dictionary from validateTelegramWebAppData
 * @returns {Object} - User information
 */
const parseTelegramUser = (validatedData) => {
  const userData = {};
  
  if (validatedData && validatedData.user) {
    try {
      const userJson = JSON.parse(validatedData.user);
      userData.telegram_id = userJson.id;
      userData.username = userJson.username;
      userData.first_name = userJson.first_name;
      userData.last_name = userJson.last_name;
      userData.language_code = userJson.language_code || 'en';
      userData.is_premium = userJson.is_premium || false;
      userData.photo_url = userJson.photo_url;
    } catch (e) {
      console.error('Error parsing user JSON:', e);
    }
  }
  
  return userData;
};

module.exports = {
  validateTelegramWebAppData,
  parseTelegramUser
};
