const axios = require('axios');
const crypto = require('crypto');

class CCPaymentService {
  constructor() {
    this.appId = process.env.CCPAYMENT_APP_ID;
    this.appSecret = process.env.CCPAYMENT_APP_SECRET;
    this.baseUrl = process.env.CCPAYMENT_API_URL;

    if (!this.appId || !this.appSecret || !this.baseUrl) {
      console.warn('CCPayment credentials missing');
    }
  }

  /**
   * Generate V2 Signature: SHA256(AppID + AppSecret + Timestamp + Body)
   */
  _generateV2Signature(timestamp, bodyStr) {
    const rawStr = `${this.appId}${this.appSecret}${timestamp}${bodyStr}`;
    return crypto.createHash('sha256').update(rawStr, 'utf8').digest('hex');
  }

  /**
   * Verify webhook signature
   */
  verifyWebhookSignature(timestamp, sign, data) {
    try {
      // Logic from Python: sort keys, join k=v, append timestamp, HMAC-SHA256
      // Note: Python _generate_signature seems to be for V1 or specific webhook format
      // Let's implement the one from the Python code exactly
      const sortedParams = Object.keys(data).sort();
      const signStrArr = [];

      for (const key of sortedParams) {
        if (data[key] !== null && data[key] !== undefined) {
          signStrArr.push(`${key}=${data[key]}`);
        }
      }

      let signStr = signStrArr.join('&');
      signStr = `${signStr}&timestamp=${timestamp}`;

      const expectedSignature = crypto
        .createHmac('sha256', this.appSecret)
        .update(signStr)
        .digest('hex');

      const expectedBuffer = Buffer.from(expectedSignature, 'utf8');
      const receivedBuffer = Buffer.from(sign, 'utf8');

      if (expectedBuffer.length !== receivedBuffer.length) {
        return false;
      }

      return crypto.timingSafeEqual(expectedBuffer, receivedBuffer);
    } catch (error) {
      console.error('Signature verification error:', error);
      return false;
    }
  }

  /**
   * Create Payment Order (Hosted Checkout)
   */
  async createPaymentOrder({ orderId, amount, currency, productName = "Casino Deposit", notifyUrl, returnUrl }) {
    try {
      const timestamp = Math.floor(Date.now() / 1000).toString();

      // V2 Payload
      const payload = {
        orderId: orderId,
        price: amount.toString(),
        product: productName,
        expiredAt: Math.floor(Date.now() / 1000) + 3600,
        fiatId: 1033 // USD
      };

      if (notifyUrl) payload.notifyUrl = notifyUrl;
      if (returnUrl) payload.returnUrl = returnUrl;

      const bodyStr = JSON.stringify(payload);
      const sign = this._generateV2Signature(timestamp, bodyStr);

      // robustness: Remove potential trailing slash from baseUrl
      const cleanBaseUrl = this.baseUrl.replace(/\/+$/, '');

      // robustness: Check if baseUrl already contains the path
      let endpoint = '/ccpayment/v2/createInvoiceUrl';
      if (cleanBaseUrl.includes('/ccpayment/v2')) {
        endpoint = '/createInvoiceUrl';
      }

      const response = await axios.post(
        `${cleanBaseUrl}${endpoint}`,
        payload,
        {
          headers: {
            'App-Id': this.appId,
            'Timestamp': timestamp,
            'Sign': sign,
            'Content-Type': 'application/json'
          }
        }
      );

      return response.data;
    } catch (error) {
      console.error('Create payment order error:', error.response?.data || error.message);
      throw error;
    }
  }
}

module.exports = new CCPaymentService();
