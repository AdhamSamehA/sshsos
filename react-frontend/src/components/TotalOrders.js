import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./TotalOrders.css";

function TotalOrders() {
  const [normalOrders, setNormalOrders] = useState([]);
  const [sharedOrders, setSharedOrders] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        // Fetch normal (non-shared) orders
        const normalResponse = await fetch("http://localhost:5200/orders?user_id=1");
        const normalData = await normalResponse.json();

        // Fetch shared (scheduled) orders
        const sharedResponse = await fetch("http://localhost:5200/shared-orders-test?user_id=1");
        const sharedData = await sharedResponse.json();

        // normalData are normal orders
        setNormalOrders(normalData);

        // sharedData are shared (scheduled) orders
        setSharedOrders(sharedData);
      } catch (error) {
        console.error("Failed to fetch orders:", error);
      }
    };

    fetchOrders();
  }, []);

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
            <p className="no-orders-message">No orders</p>
          )}
        </div>

        {/* Shared (Scheduled) Orders */}
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
            <p className="no-orders-message">No scheduled orders</p>
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
