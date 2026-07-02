// routes/orders.js
const express = require('express');
const router = express.Router();
const Order = require('../models/Order');
const { protect } = require('../middleware/authMiddleware');  // Middleware for protecting routes

// Routes

// Create a new order
router.post('/', protect, async (req, res) => { 
  try {
    const { items, totalAmount } = req.body; // Example fields
    const order = new Order({
      user: req.user._id,
      items,
      totalAmount,
    });
    const createdOrder = await order.save();
    res.status(201).json(createdOrder);
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Error creating order' });
  }
});

// Get all orders (public route for now)
router.get('/', async (req, res) => { 
  try {
    const orders = await Order.find({});
    res.json(orders);
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Error fetching orders' });
  }
});

// Update order status by ID
router.patch('/:id/status', protect, async (req, res) => { 
  const { status } = req.body; // Example field
  try {
    const order = await Order.findById(req.params.id);
    if (!order) {
      return res.status(404).json({ message: 'Order not found' });
    }
    
    order.status = status; // Update the status
    await order.save();
    res.json(order);
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Error updating order status' });
  }
});

module.exports = router;
