// backend/server.js
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const http = require('http');
const { Server } = require('socket.io');

// Import route files
const orderRoutes = require('./routes/orders');
const authRoutes = require('./routes/auth');
const adminRoutes = require('./routes/admin');

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: { 
    origin: 'http://localhost:3000', 
    methods: ['GET', 'POST', 'PATCH', 'DELETE'] 
  },
});

// ===== MIDDLEWARE (Applied in order) =====
app.use(cors());
app.use(express.json());

// Share io instance with routes (so they can emit real-time events)
app.set('io', io);

// ===== ROUTES =====
// 1. Authentication routes (login/register)
app.use('/api/auth', authRoutes);

// 2. Order routes (CRUD operations)
app.use('/api/orders', orderRoutes);

// 3. Admin routes (user management, analytics)
app.use('/api/admin', adminRoutes);

// 4. Health check route
app.get('/', (req, res) => {
  res.json({ 
    message: 'CloudCuisine API is running',
    version: '1.0.0',
    endpoints: {
      auth: '/api/auth',
      orders: '/api/orders',
      admin: '/api/admin'
    }
  });
});

// ===== DATABASE CONNECTION =====
mongoose.connect('mongodb://localhost:27017/cloudcuisine', {
  useNewUrlParser: true,
  useUnifiedTopology: true,
})
.then(() => console.log('✅ MongoDB connected successfully'))
.catch(err => console.log('❌ MongoDB connection error:', err));

// ===== SOCKET.IO SETUP =====
io.on('connection', (socket) => {
  console.log('🟢 A client connected:', socket.id);

  socket.on('disconnect', () => {
    console.log('🔴 Client disconnected:', socket.id);
  });
});

// ===== START SERVER =====
const PORT = process.env.PORT || 5000;
server.listen(PORT, () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
});
