const express = require('express');
const router = express.Router();
const { createTicket, listTickets, getTicketHistory } = require('../controllers/supportController');
const { protect } = require('../middleware/authMiddleware');

router.post('/tickets', protect, createTicket);
router.get('/tickets', protect, listTickets);
router.get('/tickets/:ticket_id/messages', protect, getTicketHistory);

module.exports = router;
