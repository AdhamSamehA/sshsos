import React, { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "./supermarkets.css";

const SUPERMARKET_FEED_API = "http://localhost:5200/supermarket/feed";
const USER_ACCOUNT_API = "http://localhost:5200/user/account?user_id=1";

export default function Supermarkets() {
  const [supermarkets, setSupermarkets] = useState([]);
  const [address, setAddress] = useState("");
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // Fetch user default address
  const fetchUserAddress = async () => {
    try {
      const response = await axios.get(USER_ACCOUNT_API);
      setAddress(response.data.default_address);
    } catch (error) {
      console.error("Error fetching user address:", error);
    }
  };

  // Fetch supermarkets
  const fetchSupermarkets = async () => {
    try {
      const response = await axios.get(SUPERMARKET_FEED_API);
      setSupermarkets(response.data.supermarkets);
    } catch (error) {
      console.error("Error fetching supermarket feed:", error);
    } finally {
      setLoading(false);
    }
  };

  // Handle Supermarket Click: Create cart and navigate to items page
  const handleSupermarketClick = async (supermarketId) => {
    try {
      const response = await axios.post(`http://localhost:5200/carts/create`, {
        user_id: 1, // Replace with actual user ID
        supermarket_id: supermarketId,
      });
      const newCartId = response.data.cart_id;
      localStorage.setItem("cartId", newCartId); // Persist cart ID
      navigate(`/supermarketshopping/${supermarketId}`); // Navigate to items page
    } catch (error) {
      console.error("Error creating cart:", error);
    }
  };

  useEffect(() => {
    fetchUserAddress();
    fetchSupermarkets();
  }, []);

  if (loading) {
    return (
      <div className="loadingContainer">
        <div className="loader">Loading...</div>
      </div>
    );
  }

  return (
    <div className="mainContainer">
      {/* Address Bar */}
      <div className="addressBar">
        <p className="addressText">Delivering to:</p>
        <p className="address">{address}</p>
      </div>

      {/* Supermarkets List */}
      <div className="supermarketsContainer">
        {supermarkets.map((item) => (
          <div
            key={item.id}
            className="supermarketCard"
            onClick={() => handleSupermarketClick(item.id)}
          >
            <img
              src={item.photo_url}
              alt={item.name}
              className="supermarketImage"
            />
            <div className="supermarketDetails">
              <h3 className="supermarketName">{item.name}</h3>
              <p className="supermarketMeta">{item.address}</p>
              <div className="supermarketExtras">
                <p className="deliveryTime">15 mins</p>
                <div className="ratingContainer">
                  <span className="rating">4.7</span>
                  <span className="ratingText">(500+)</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
