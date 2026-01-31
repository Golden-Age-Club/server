const express = require('express');
const router = express.Router();
const { ccPaymentWebhook, unifiedCallback } = require('../controllers/webhookController');

router.post('/webhook/ccpayment', ccPaymentWebhook);
router.post('/callback', unifiedCallback);

module.exports = router;
