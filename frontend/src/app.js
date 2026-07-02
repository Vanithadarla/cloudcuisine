import React from 'react';
import OrderForm from './components/OrderForm';
import OrderList from './components/OrderList';
import KitchenDashboard from './components/KitchenDashboard';

function App() {
  return (
    <div style={{ padding: 20 }}>
      <h1>CloudCuisine - Restaurant Order System</h1>
      <div style={{ display: 'flex', gap: 40, flexWrap: 'wrap' }}>
        <div>
          <h2>Place Order</h2>
          <OrderForm />
        </div>
        <div>
          <h2>All Orders</h2>
          <OrderList />
        </div>
        <div>
          <h2>Kitchen Dashboard (Real-time)</h2>
          <KitchenDashboard />
        </div>
      </div>
    </div>
  );
}

export default App;
