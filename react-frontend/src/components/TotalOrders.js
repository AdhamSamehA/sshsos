import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./TotalOrders.css";

function TotalOrders() {
  const [normalOrders, setNormalOrders] = useState([]);
  const [sharedOrders, setSharedOrders] = useState([]);
  const [loading, setLoading] = useState(true); // Loading state
  const navigate = useNavigate();

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        const response = await fetch("http://localhost:5200/orders?user_id=1");
        const orders = await response.json();

        // Debugging fetched orders
        console.log("Fetched Orders:", orders);

        // Categorize orders based on shared_cart_id
        const normal = orders.filter((order) => !order.shared_cart_id);
        const shared = orders.filter((order) => order.shared_cart_id);

        setNormalOrders(normal);
        setSharedOrders(shared);
      } catch (error) {
        console.error("Failed to fetch orders:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchOrders();
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="total-orders-container">
      <h2>My Orders</h2>
      <div className="orders-grid">
        {/* Normal Orders */}
        <div className="orders-box">
          <h3>Normal Orders</h3>
          {normalOrders.length > 0 ? (
            normalOrders.map((order) => (
              <div key={order.order_id} className="order-item">
                <p>Order ID: {order.order_id}</p>
                <p>Cost: ${order.total_cost.toFixed(2)}</p>
                <p>Status: {order.status}</p>
              </div>
            ))
          ) : (
            <p className="no-orders-message">No normal orders</p>
          )}
        </div>

        {/* Shared Orders */}
        <div className="orders-box">
          <h3>Shared Orders</h3>
          {sharedOrders.length > 0 ? (
            sharedOrders.map((order) => (
              <div key={order.order_id} className="order-item">
                <p>Order ID: {order.order_id}</p>
                <p>Cost: ${order.total_cost.toFixed(2)}</p>
                <p>Status: {order.status}</p>
              </div>
            ))
          ) : (
            <p className="no-orders-message">No shared orders</p>
          )}
        </div>
      </div>

      {/* New Order Button */}
      <button className="new-order-button" onClick={() => navigate("/")}>
        Make a New Order
      </button>
    </div>
  );
}

export default TotalOrders;
