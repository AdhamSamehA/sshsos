import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./TotalOrders.css";

function TotalOrders() {
  const [normalOrders, setNormalOrders] = useState([]);
  const [sharedOrders, setSharedOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        console.log("Fetching normal orders...");
        const normalResponse = await fetch("http://localhost:5200/orders?user_id=1");
        const normalData = await normalResponse.json();
        console.log("Normal orders fetched:", normalData);

        console.log("Fetching shared orders...");
        const sharedResponse = await fetch("http://localhost:5200/shared-orders-test?user_id=1");
        const sharedData = await sharedResponse.json();
        console.log("Shared orders fetched:", sharedData);

        setNormalOrders(normalData);
        setSharedOrders(sharedData);
      } catch (error) {
        console.error("Failed to fetch orders:", error);
      } finally {
        setLoading(false);
        console.log("Finished fetching orders.");
      }
    };

    fetchOrders();
  }, []);

  const handleOrderClick = async (order) => {
    try {
      console.log("Fetching details for order:", order.order_id);
      if (order.shared_cart_id) {
        const response = await fetch(`http://localhost:5200/order/details?order_id=${order.order_id}`);
        const data = await response.json();
        console.log("Shared order details fetched:", data);
        setSelectedOrder(data);
      } else {
        console.log("Normal order selected:", order);
        setSelectedOrder(order);
      }
    } catch (error) {
      console.error("Failed to fetch order details:", error);
    }
  };

  const closeDetails = () => {
    console.log("Closing order details modal.");
    setSelectedOrder(null);
  };

  if (loading) {
    console.log("Orders are still loading...");
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
              <div
                key={order.order_id}
                className="order-card"
                onClick={() => handleOrderClick(order)}
              >
                <p>Order ID: {order.order_id}</p>
                <p>Total Cost: AED {order.total_cost.toFixed(2)}</p>
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
              <div
                key={order.order_id}
                className="order-card"
                onClick={() => handleOrderClick(order)}
              >
                <p>Order ID: {order.order_id}</p>
                <p>Total Contribution: AED {order.contributions[0]?.total_contribution.toFixed(2)}</p>
                <p>Delivery Fee Contribution: AED {order.contributions[0]?.delivery_fee_contribution.toFixed(2)}</p>
                <p>Status: {order.status}</p>
              </div>
            ))
          ) : (
            <p className="no-orders-message">No shared orders</p>
          )}
        </div>
      </div>

      {/* Order Details Modal */}
      {selectedOrder && (
        <div className="order-details-modal">
          <div className="order-details-content">
            <button className="close-button" onClick={closeDetails}>
              Close
            </button>
            <h3>Order Details</h3>
            <p>Order ID: {selectedOrder.order_id}</p>
            <p>Total Cost: AED {selectedOrder.total_cost.toFixed(2)}</p>
            <p>Status: {selectedOrder.status}</p>
            {selectedOrder.contributors && selectedOrder.contributors.length > 0 && (
              <>
                <h4>Contributors:</h4>
                <ul>
                  {selectedOrder.contributors.map((contributor) => (
                    <li key={contributor.user_id}>
                      <p>Name: {contributor.name}</p>
                      <p>Delivery Fee Contribution: AED {contributor.delivery_fee_contribution.toFixed(2)}</p>
                    </li>
                  ))}
                </ul>
              </>
            )}
            <div className="order-items">
              <h4>Items:</h4>
              {selectedOrder.items.map((item) => (
                <div key={item.item_id} className="order-item">
                  <p>{item.name}</p>
                  <p>Quantity: {item.quantity}</p>
                  <p>Price: AED {item.price.toFixed(2)}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* New Order Button */}
      <button className="new-order-button" onClick={() => navigate("/")}>
        Make a New Order
      </button>
    </div>
  );
}

export default TotalOrders;
