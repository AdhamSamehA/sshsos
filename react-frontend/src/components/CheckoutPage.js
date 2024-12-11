import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "./CheckoutPage.css";

const CheckoutPage = () => {
  const navigate = useNavigate();
  const cartId = localStorage.getItem("cartId");
  const [walletBalance, setWalletBalance] = useState(0);
  const [addresses, setAddresses] = useState([]);
  const [selectedAddress, setSelectedAddress] = useState("");
  const [selectedSlot, setSelectedSlot] = useState("now");
  const [deliverySlots, setDeliverySlots] = useState([]);
  const [showSchedule, setShowSchedule] = useState(false);
  const [cartItems, setCartItems] = useState([]);
  const [basketValue, setBasketValue] = useState(0);
  const [deliveryFee, setDeliveryFee] = useState(5);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [redirecting, setRedirecting] = useState(false);

  useEffect(() => {
    const fetchCheckoutDetails = async () => {
      try {
        if (!cartId) {
          setError("Cart not found. Please create a cart first.");
          setLoading(false);
          return;
        }

        const cartResponse = await axios.get(
          `http://localhost:5200/carts/${cartId}`
        );
        const items = cartResponse.data.items || [];
        const basketValue = items.reduce(
          (total, item) => total + item.price * item.quantity,
          0
        );

        setCartItems(items);
        setBasketValue(basketValue);
        setDeliveryFee(33);

        const addressResponse = await axios.get(
          `http://localhost:5200/user/addresses?user_id=1`
        );

        setAddresses(addressResponse.data.addresses || []);
        if (addressResponse.data.addresses.length > 0) {
          setSelectedAddress(addressResponse.data.addresses[0].address_details);
        }

        const walletResponse = await axios.get(
          `http://localhost:5200/wallet/balance?user_id=1`
        );

        setWalletBalance(walletResponse.data.balance || 0);

        const slotsResponse = await axios.get(
          `http://localhost:5200/orders/slots?supermarket_id=1`
        );
        setDeliverySlots(slotsResponse.data.available_slots || []);
      } catch (err) {
        console.error("Error fetching checkout details:", err);
        setError("Failed to fetch checkout details. Please try again.");
      }
      setLoading(false);
    };

    fetchCheckoutDetails();
  }, [cartId]);

  const handlePlaceOrder = async () => {
    if (!cartId) {
      alert("Cart not found. Please create a cart first.");
      return;
    }
  
    const selectedAddressId = addresses.find(
      (addr) => addr.address_details === selectedAddress
    )?.address_id;
  
    if (!selectedAddressId) {
      alert("Please select a valid address.");
      return;
    }
  
    if (!selectedSlot) {
      alert("Please select a delivery option.");
      return;
    }
  
    if (redirecting) return;
    setRedirecting(true);
  
    try {
      const response = await axios.post(
        `http://localhost:5200/carts/${cartId}/submit-delivery`,
        {
          user_id: 1,
          supermarket_id: 1,
          address_id: selectedAddressId,
          order_time: selectedSlot,
        }
      );
  
      // Navigate to order confirmation page
      navigate("/order-confirmation", {
        state: {
          orderDetails: response.data,
          address: selectedAddress,
          deliveryTime:
            selectedSlot === "now" ? "in 15 mins" : `at ${selectedSlot}`,
        },
      });
    } catch (error) {
      console.error("Error placing the order:", error);
      alert("Failed to place the order. Please try again.");
      setRedirecting(false);
    }
  };
  

  const toggleScheduleOrder = () => setShowSchedule(!showSchedule);

  const totalAmount = basketValue + deliveryFee;

  if (loading) return <div>Loading...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div className="checkout-page">
      <h2>Checkout</h2>

      <div className="section">
        <h3>Delivery</h3>
        <div className="delivery-buttons">
          <button
            className="delivery-button"
            onClick={() => {
              setSelectedSlot("now");
              setShowSchedule(false);
            }}
          >
            Order Now (15 mins)
          </button>
          <button className="delivery-button" onClick={toggleScheduleOrder}>
            Schedule Order
          </button>
        </div>

        {showSchedule && (
          <div className="schedule-options">
            <h4>Available Slots</h4>
            <select
              value={selectedSlot}
              onChange={(e) => setSelectedSlot(e.target.value)}
            >
              {deliverySlots.map((slot, index) => (
                <option key={index} value={slot}>
                  {slot}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      <div className="section">
        <h3>Address</h3>
        <select
          value={selectedAddress}
          onChange={(e) => setSelectedAddress(e.target.value)}
        >
          {addresses.map((address) => (
            <option key={address.address_id} value={address.address_details}>
              {address.address_details}
            </option>
          ))}
        </select>
      </div>

      <div className="section">
        <h3>Cart Items</h3>
        {cartItems.map((item) => (
          <div key={item.item_id} className="item-details">
            <p>
              {item.name} x {item.quantity} - AED {item.price?.toFixed(2) || "0.00"}
            </p>
          </div>
        ))}
      </div>

      <div className="section">
        <h3>Payment Summary</h3>
        <p>Basket Value: AED {basketValue.toFixed(2)}</p>
        <p>Delivery Fee: AED {deliveryFee.toFixed(2)}</p>
        <p>Total: AED {totalAmount.toFixed(2)}</p>
        <p>Wallet Balance: AED {walletBalance.toFixed(2)}</p>
      </div>

      <button
        className="pay-button"
        onClick={handlePlaceOrder}
        disabled={walletBalance < totalAmount || redirecting}
      >
        Pay Now (AED {totalAmount.toFixed(2)} - Wallet Balance: AED{" "}
        {walletBalance.toFixed(2)})
      </button>

      {walletBalance < totalAmount && (
        <p className="error">
          Insufficient wallet balance. Please top up your wallet.
        </p>
      )}
    </div>
  );
};

export default CheckoutPage;
