import React, { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "./CartPage.css";

const CartPage = () => {
  const [cartItems, setCartItems] = useState([]); // Cart items
  const [loading, setLoading] = useState(true); // Loading state
  const [totalPrice, setTotalPrice] = useState(0); // Total price
  const [walletBalance, setWalletBalance] = useState(0); // Wallet balance
  const [error, setError] = useState(null); // Error state
  const navigate = useNavigate();

  const cartId = localStorage.getItem("cartId"); // Fetch cartId from localStorage

  // Fetch cart data from the backend
  useEffect(() => {
    const fetchCartItems = async () => {
      if (!cartId) {
        console.error("Cart ID not found in localStorage.");
        setError("Cart not found.");
        setLoading(false);
        return;
      }

      try {
        console.log(`Fetching cart data for cartId: ${cartId}`);
        const response = await axios.get(`http://localhost:5200/carts/${cartId}`);
        if (response.data) {
          console.log("Cart data fetched successfully:", response.data);
          setCartItems(response.data.items || []); // Update items
          setTotalPrice(response.data.total_price || 0); // Update total price
          setWalletBalance(response.data.wallet_balance || 0); // Update wallet balance
        } else {
          console.error("Invalid cart data:", response);
          setError("Invalid cart data received from the server.");
        }
      } catch (err) {
        console.error("Error fetching cart data:", err);
        setError("Error fetching cart data. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    fetchCartItems();
  }, [cartId]);

  // Handle quantity change
  const updateQuantity = async (itemId, quantity) => {
    if (quantity < 1) {
      removeItemFromCart(itemId); // Remove item if quantity drops below 1
      return;
    }

    try {
      const response = await axios.post(`http://localhost:5200/carts/${cartId}/add-item`, {
        item_id: itemId,
        quantity,
      });
      if (response.data) {
        console.log("Item quantity updated successfully:", response.data);
        setCartItems(response.data.items || []); // Update items
        setTotalPrice(response.data.total_price || 0); // Update total price
      }
    } catch (err) {
      console.error("Error updating item quantity:", err);
    }
  };

  // Handle removing an item from the cart
  const removeItemFromCart = async (itemId) => {
    try {
      const response = await axios.delete(`http://localhost:5200/carts/${cartId}/remove-item`, {
        data: { item_id: itemId },
      });
      if (response.data) {
        console.log("Item removed from cart successfully:", response.data);
        setCartItems(response.data.items || []); // Update items
        setTotalPrice(response.data.total_price || 0); // Update total price
      }
    } catch (err) {
      console.error("Error removing item from cart:", err);
    }
  };

  // Handle emptying the cart
  const emptyCart = async () => {
    try {
      await axios.delete(`http://localhost:5200/carts/${cartId}/empty`);
      console.log("Cart emptied successfully.");
      setCartItems([]); // Empty cart items
      setTotalPrice(0); // Reset total price
    } catch (err) {
      console.error("Error emptying the cart:", err);
    }
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>{error}</div>;
  }

  return (
    <div className="cart-page">
      <h2>Your Shopping Cart</h2>

      {/* Display cart items */}
      {cartItems.length > 0 ? (
        <div className="cart-items">
          {cartItems.map((item) => (
            <div key={item.item_id} className="cart-item">
              <img src={item.photo_url} alt={item.name} className="item-photo" />
              <div className="item-info">
                <h3>{item.name}</h3>
                <p className="item-price">${item.price.toFixed(2)}</p>
              </div>
              <div className="quantity-controls">
                <button
                  className="minus"
                  onClick={() => updateQuantity(item.item_id, item.quantity - 1)}
                >
                  -
                </button>
                <span>{item.quantity}</span>
                <button
                  className="plus"
                  onClick={() => updateQuantity(item.item_id, item.quantity + 1)}
                >
                  +
                </button>
              </div>
              <button
                className="remove-item"
                onClick={() => removeItemFromCart(item.item_id)}
              >
                Remove
              </button>
            </div>
          ))}
        </div>
      ) : (
        <p>Your cart is empty.</p>
      )}

      {/* Display total price and wallet balance */}
      <div className="total-price">
        <h3>Total: ${totalPrice.toFixed(2)}</h3>
        <h4>Wallet Balance: ${walletBalance.toFixed(2)}</h4>
      </div>

      {/* Buttons */}
      <div className="cart-buttons">
        <button className="empty-cart" onClick={emptyCart}>
          Empty Cart
        </button>
        <button className="checkout" onClick={() => navigate("/checkout")}>
          Proceed to Checkout
        </button>
      </div>
    </div>
  );
};

export default CartPage;
