import React from "react";
import { useLocation, useNavigate } from "react-router-dom";
import "./OrderConfirmationPage.css";

const OrderConfirmationPage = () => {
  const location = useLocation();
  const navigate = useNavigate(); // Correctly define navigate using the hook
  const { address, deliveryTime } = location.state || {};

  return (
    <div className="order-confirmation-page">
      <h2>Order Confirmation</h2>
      <p>Your order has been placed successfully!</p>
      <div className="order-details">
        <p><strong>Delivery Address:</strong> {address}</p>
        <p><strong>Delivery Time:</strong> Arriving {deliveryTime}</p>
      </div>
      <button onClick={() => navigate("/")} className="home-button">
        Go to Home
      </button>
    </div>
  );
};

export default OrderConfirmationPage;
