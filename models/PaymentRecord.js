const mongoose = require('mongoose');

const paymentRecordSchema = new mongoose.Schema({
    merchant_order_id: {
        type: String,
        index: true
    },
    webhook_type: {
        type: String, // 'deposit', 'withdrawal', 'active_webhook', etc.
        default: 'unknown'
    },
    payload: {
        type: mongoose.Schema.Types.Mixed, // Stores the full raw JSON body
        required: true
    },
    headers: {
        type: mongoose.Schema.Types.Mixed // Optional: store significant headers like signature
    },
    ip_address: {
        type: String
    },
    processed_status: {
        type: String,
        enum: ['success', 'failed', 'ignored', 'duplicate'],
        default: 'success'
    },
    error_message: {
        type: String
    },
    created_at: {
        type: Date,
        default: Date.now,
        expires: 60 * 60 * 24 * 90 // Auto-delete after 90 days to save space (optional)
    }
});

module.exports = mongoose.model('PaymentRecord', paymentRecordSchema);
