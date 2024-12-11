import React from "react";
import { useLocation, useNavigate } from "react-router-dom";
import "./OrderConfirmationPage.css";

const OrderConfirmationPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { address, deliveryTime } = location.state || {};

  // Log the received state data
  console.log("Order Confirmation Page Loaded:");
  console.log("Address:", address);
  console.log("Delivery Time:", deliveryTime);

  return (
    <div className="order-confirmation-page">
      <h2>Order Confirmation</h2>
      <p>Your order has been placed successfully!</p>
      <div className="order-details">
        <p>
          <strong>Delivery Address:</strong> {address}
        </p>
        <p>
          <strong>Delivery Time:</strong> Arriving {deliveryTime}
        </p>
      </div>
      <button
        onClick={() => {
          console.log("Navigating to Home Page...");
          navigate("/");
        }}
        className="home-button"
      >
        Go to Home
      </button>
    </div>
  );
};

export default OrderConfirmationPage;
