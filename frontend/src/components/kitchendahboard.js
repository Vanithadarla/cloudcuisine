// frontend/src/components/KitchenDashboard.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import socket from '../socket';

const KitchenDashboard = () => {
  const [orders, setOrders] = useState([]);

  // Fetch initial orders from backend
  useEffect(() = async () => {
      try {
        const res = await axios.get('http://localhost:5000/api/orders');
        setOrders(res.data);
      } catch (err) {
        console.error('Error fetching orders:', err);
      }
    };
    fetchOrders();
  }, []);

  // Listen for real-time events via Socket.IO
  useEffect(() => {
    // When a new order is placed
    socket.on('newOrder', (order) => {
      setOrders((prev) => [order, ...prev]);
    });

    // When an order status is updated by the kitchen
    socket.on('orderStatusChanged', (updatedOrder) => {
      setOrders((prev) =>
        prev.map((order) =>
          order._id === updatedOrder._id ? updatedOrder : order
        )
      );
    });

    return () => {
      socket.off('newOrder');
      socket.off('orderStatusChanged');
    };
  }, []);

  // Update order status (called from buttons)
  const updateStatus = async (orderId, newStatus) => {
    try {
      await axios.patch(`http://localhost:5000/api/orders/${orderId}/status`, {
        status: newStatus,
      });
    } catch (err) {
      console.error('Error updating status:', err);
    }
  };

  // Group orders by status for better display
  const pendingOrders = orders.filter((o) => o.status === 'pending');
  const preparingOrders = orders.filter((o) => o.status === 'preparing');
  const readyOrders = orders.filter((o) => o.status === 'ready');
  const deliveredOrders = orders.filter((o) => o.status === 'delivered');

  return (
    <div style={{ border: '1px solid #ccc', padding: 20, borderRadius: 8 }}>
      <h3>Kitchen Dashboard</h3>

      <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap' }}>
        {/* Pending Column */}
        <div style={{ flex: 1, minWidth: 200 }}>
          <h4 style={{ color: 'red' }}>Pending ({4>
          {pendingOrders.map((order) => (
            <div key={order._id} style={orderCardStyle}>
              <strong>{order.customerName}</strong>
              <ul>
                {order.items.map((item, i) => (
                  <li key={i}>{item.name} x{item.quantity}</li>
                ))}
              </ul>
              <button onClick={() => updateStatus(order._id, 'preparing')}>
                Start Preparing
              </button>
            </div>
          ))}
        </div>

        {/* Preparing Column */}
        <div style={{ flex: 1, minWidth: 200 }}>
          <h4 style={{ color: 'orange' }}>Preparing ({preparingOrders.length})</h4>
          {preparingOrders.map((order) => (
            <div key={order._id} style={orderCardStyle}>
              <strong>{order.customerName}</strong>
              <ul>
                {order.items.map((item, i) => (
                  <li key={i}>{item.name} x{item.quantity}</li>
                ))}
              </ul>
              <button onClick={() => updateStatus(order._id, 'ready')}>
                Mark as Ready
              </button>
            </div>
          ))}
        </div>

        {/* Ready Column */}
        <div style={{ flex: 1, minWidth: 200 }}>
          <h4 style={{ color: 'green' }}>Ready ({readyOrders.length})</h4>
          {readyOrders.map((order) => (
            <div key={order._id} style={orderCardStyle}>
              <strong>{order.customerName}</strong>
              <ul>
                {order.items.map((item, i) => (
                  <li key={i}>{item.name} x{item.quantity}</li>
                ))}
              </ul>
              <button onClick={() => updateStatus(order._id, 'delivered')}>
                Mark as Delivered
              </button>
            </div>
          ))}
        </div>

        {/* Delivered Column (optional) */}
        <div style={{ flex: 1, minWidth: 200 }}>
          <h4 style={{ color: 'gray' }}>Delivered ({deliveredOrders.length})</h4>
          {deliveredOrders.map((order) => (
            <div key={order._id} style={orderCardStyle}>
              <strong>{order.customerName}</strong>
              <ul>
                {order.items.map((item, i) => (
                  <li key={i}>{item.name} x{item.quantity}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Simple inline style for each order card
const orderCardStyle = {
  border: '1px solid #ddd',
  borderRadius: 6,
  padding: 10,
  marginBottom: 10,
  backgroundColor: '#f9f9f9',
};

export default KitchenDashboard;
