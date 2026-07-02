// frontend/src/components/OrderList.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import socket from '../socket';

const statusColors = {
  pending: 'red',
  preparing: 'orange',
  ready: 'green',
  delivered: 'gray',
};

const OrderList = () => {
  const [orders, setOrders] = useState([]);

  // Fetch all orders on mount
  useEffect(() => {
    const fetchOrders = async () => {
      try {
        const res = await axios.get('http://localhost:5000/api/orders');
        setOrders(res.data);
      } catch (err) {
        console.error('Error fetching orders:', err);
      }
    };
    fetchOrders();
  }, []);

  // Listen for real-time updates
  useEffect(() => {
    socket.on('newOrder', (order) => {
      setOrders((prev) => [order, ...prev]);
    });

    socket.on('orderStatusChanged', (updatedOrder) => {
      setOrders((prev) =>
        prev.map((order) =>
          order._id === updatedOrder._id ? updatedOrder : order
        )
      );
    });

    return () => {
      socket.off('newOrder');
     StatusChanged');
    };
  }, []);

  return (
    <div style={{ border: '1px solid #ccc', padding: 20, borderRadius: 8, maxWidth: 500 }}>
      <h3>All Orders ({orders.length})</h3>
      {orders.length === 0 ? (
        <p>No orders yet.</p>
      ) : (
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {orders.map((order) => (
            <li
              key={order._id}
              style={{
                border: '1px solid #ddd',
                borderRadius: 6,
                padding: 10,
                marginBottom: 8,
                backgroundColor: '#fafafa',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <strong>{order.customerName}</strong>
                <span style={{ color: statusColors[orderbold' }}>
                  {order.status.toUpperCase()}
                </span>
              </div>
              <ul style={{ margin: '5px 0', paddingLeft: 20 }}>
                {order.items.map((item, i) => (
                  <li key={i}>
                    {item.name} x{item.item.price * item.quantity).toFixed(2)}
                  </li>
                ))}
              </ul>
              <div style={{ fontSize: '0.9em', color: '#555' }}>
                Total: ${order.total.toFixed(2)} | Placed: {new Date(order.createdAt).toLocaleTimeString()}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default OrderList;
