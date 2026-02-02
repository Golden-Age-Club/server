const Promotion = require('../models/Promotion');
const UserBonus = require('../models/UserBonus');
const User = require('../models/User');

class PromotionController {
  
  /**
   * Get All Promotions
   * @route GET /api/admin/promotions
   */
  static async getPromotions(req, res) {
    try {
      const { status } = req.query;
      let query = {};
      
      if (status === 'active') query.is_active = true;
      if (status === 'inactive') query.is_active = false;

      const promotions = await Promotion.find(query).sort({ created_at: -1 });
      res.json(promotions);
    } catch (error) {
      console.error('Error fetching promotions:', error);
      res.status(500).json({ message: 'Failed to fetch promotions' });
    }
  }

  /**
   * Create New Promotion
   * @route POST /api/admin/promotions
   */
  static async createPromotion(req, res) {
    try {
      const { 
        title, description, type, value, min_deposit, 
        max_bonus, wager_multiplier, valid_days, 
        start_date, end_date, applicable_games 
      } = req.body;

      const newPromotion = await Promotion.create({
        title,
        description,
        type,
        value,
        min_deposit,
        max_bonus,
        wager_multiplier,
        valid_days,
        start_date,
        end_date,
        applicable_games,
        is_active: true
      });

      res.status(201).json(newPromotion);
    } catch (error) {
      console.error('Error creating promotion:', error);
      res.status(500).json({ message: 'Failed to create promotion' });
    }
  }

  /**
   * Update Promotion
   * @route PUT /api/admin/promotions/:id
   */
  static async updatePromotion(req, res) {
    try {
      const promotion = await Promotion.findByIdAndUpdate(
        req.params.id,
        { $set: req.body },
        { new: true }
      );

      if (!promotion) {
        return res.status(404).json({ message: 'Promotion not found' });
      }

      res.json(promotion);
    } catch (error) {
      console.error('Error updating promotion:', error);
      res.status(500).json({ message: 'Failed to update promotion' });
    }
  }

  /**
   * Delete Promotion
   * @route DELETE /api/admin/promotions/:id
   */
  static async deletePromotion(req, res) {
    try {
      const promotion = await Promotion.findByIdAndDelete(req.params.id);
      
      if (!promotion) {
        return res.status(404).json({ message: 'Promotion not found' });
      }

      res.json({ message: 'Promotion deleted successfully' });
    } catch (error) {
      console.error('Error deleting promotion:', error);
      res.status(500).json({ message: 'Failed to delete promotion' });
    }
  }

  /**
   * Get User Bonuses (All or specific user)
   * @route GET /api/admin/promotions/user-bonuses
   */
  static async getUserBonuses(req, res) {
    try {
      const { user_id, status, page = 1, limit = 20 } = req.query;
      const skip = (page - 1) * limit;
      
      let query = {};
      if (user_id) query.user_id = user_id;
      if (status) query.status = status;

      const bonuses = await UserBonus.find(query)
        .populate('user_id', 'username email first_name last_name')
        .sort({ claimed_at: -1 })
        .skip(skip)
        .limit(parseInt(limit));

      const total = await UserBonus.countDocuments(query);

      res.json({
        bonuses,
        total,
        page: parseInt(page),
        pages: Math.ceil(total / limit)
      });
    } catch (error) {
      console.error('Error fetching user bonuses:', error);
      res.status(500).json({ message: 'Failed to fetch user bonuses' });
    }
  }

  /**
   * Assign Bonus to User Manually
   * @route POST /api/admin/promotions/assign
   */
  static async assignBonus(req, res) {
    try {
      const { user_id, promotion_id, amount } = req.body;

      const user = await User.findById(user_id);
      if (!user) return res.status(404).json({ message: 'User not found' });

      const promotion = await Promotion.findById(promotion_id);
      if (!promotion) return res.status(404).json({ message: 'Promotion not found' });

      // Calculate wager requirements
      const wager_required = amount * promotion.wager_multiplier;
      const expires_at = new Date();
      expires_at.setDate(expires_at.getDate() + promotion.valid_days);

      const userBonus = await UserBonus.create({
        user_id,
        promotion_id,
        promotion_title: promotion.title,
        type: promotion.type,
        amount,
        initial_amount: amount,
        wager_required,
        wager_remaining: wager_required,
        status: 'active',
        expires_at
      });

      res.status(201).json(userBonus);
    } catch (error) {
      console.error('Error assigning bonus:', error);
      res.status(500).json({ message: 'Failed to assign bonus' });
    }
  }
}

module.exports = PromotionController;
