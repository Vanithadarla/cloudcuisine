// frontend/src/components/AdminDashboard.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import socket from '../socket';

const AdminDashboard = () => {
  const [users, setUsers] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [newUser, setNewUser] = useState({ username: '', password: '', role: 'waitstaff' });
  const [activeTab, setActiveTab] = useState('analytics');

  // Fetch users and analytics on mount
  useEffect(() => {
    fetchUsers();
    fetchAnalytics();
  }, []);

  const fetchUsers = async () => {
    try {
      const res = await axios.get('http://localhost:5000/api/admin/users');
      setUsers(res.data);
    } catch (err) {
      console.error('Error fetching users:', err);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const res = await axios.get('http://localhost:5000/api/admin/analytics');
      setAnalytics(res.data);
    } catch (err) {
      console.error('Error fetching analytics:', err);
    }
  };

  // Create new user
  const handleCreateUser = async (e) => {
    e.preventDefault();
    try {
      await axios.post('http://localhost:5000/api/admin/users', newUser);
      setNewUser({ username: '', password: '', role: 'waitstaff' });
      fetchUsers();
    } catch (err) {
      console.error('Error creating user:', err);
      alert('Failed to create user');
    }
  };

  // Delete user
  const handleDeleteUser = async (userId) => {
    if (!window.confirm('Are you sure you want to delete this user?')) return;
    try {
      await axios.delete(`http://localhost:5000/api/admin/users/${userId}`);
      fetchUsers();
    } catch (err) {
      console.error('Error deleting user:', err);
    }
  };

  // Change user role
  const handleChangeRole = async (userId, newRole) => {
    try {
      await axios.patch(`http://localhost:5000/api/admin/users/${userId}/role`, { role: newRole });
      fetchUsers();
    } catch (err) {
      console.error('Error changing role:', err);
    }
  };

  // Listen for real-time order updates
  useEffect(() => {
    socket.on('newOrder', () => fetchAnalytics());
    socket.on('orderStatusChanged', () => fetchAnalytics());
    return () => {
      socket.off('newOrder');
      socket.off('orderStatusChanged');
    };
  }, []);

  return (
    <div style={{ padding: 20 }}>
      <h2>Admin Dashboard</h2>

      {/* Tab Navigation */}
      <div style={{ marginBottom: 20 }}>
        <button
          onClick={() => setActiveTab('analytics')}
          style={tabButtonStyle(activeTab === 'analytics')}
        >
          Analytics
        </button>
        <button
          onClick={() => setActiveTab('users')}
          style={tabButtonStyle(activeTab === 'users')}
        >
          Manage Users
        </button>
      </div>

      {/* Analytics Tab */}
      {activeTab === 'analytics' && analytics && (
        <div>
          <h3>Order Analytics</h3>
          <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap', marginBottom: 20 }}>
            <div style={cardStyle}>
              <h4>Total Orders</h4>
              <p style={{ fontSize: 24, fontWeight: 'bold' }}>{analytics.totalOrders}</p>
            </div>
            <div style={cardStyle}>
              <h4>Today's Orders</h4>
              <p style={{ fontSize: 24, fontWeight: 'bold' }}>{analytics.todayOrders}</p>
            </div>
            <div style={cardStyle}>
              <h4>Total Revenue</h4>
              <p style={{ fontSize: 24, fontWeight: 'bold' }}>
                ${analytics.totalRevenue.toFixed(2)}
              </p>
            </div>
          </div>

          <h4>Orders by Status</h4>
          <ul>
            {analytics.ordersByStatus.map((status) => (
              <li key={status._id}>
                {status._id}: {status.count}
              </li>
            ))}
          </ul>

          <h4>Popular Items (Top 5)</h4>
          <ol>
            {analytics.popularItems.map((item, index) => (
              <li key={index}>
                {item._id} – ordered {item.totalQuantity} times
              </li>
            ))}
         
