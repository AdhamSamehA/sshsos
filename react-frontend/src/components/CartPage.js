import React, { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "./CartPage.css";

const CartPage = () => {
  const [cartItems, setCartItems] = useState([]); // Cart items
  const [loading, setLoading] = useState(true); // Loading state
  const [totalPrice, setTotalPrice] = useState(0); // Total price
  const [error, setError] = useState(null); // Error state
  const navigate = useNavigate();

  const cartId = localStorage.getItem("cartId"); // Fetch cartId from localStorage

  // Fetch cart data from the backend
  useEffect(() => {
    const fetchCartData = async () => {
      try {
        if (!cartId) {
          setError("Cart not found.");
          setLoading(false);
          return;
        }

        const response = await axios.get(`http://localhost:5200/carts/${cartId}`);
        setCartItems(response.data.items || []);
        setTotalPrice(response.data.total_price || 0);
      } catch (err) {
        setError("Error fetching cart data. Please try again.");
        console.error(err);
      }
      setLoading(false);
    };

    fetchCartData();
  }, [cartId]); // Dependency array ensures it runs whenever cartId changes

  // Add item to cart (for the plus button)
  const addItemToCart = async (itemId) => {
    try {
      await axios.post(`http://localhost:5200/carts/${cartId}/add-item`, {
        item_id: itemId,
        quantity: 1,
      });

      setCartItems((prevItems) =>
        prevItems.map((item) =>
          item.item_id === itemId
            ? { ...item, quantity: item.quantity + 1 }
            : item
        )
      );
      setTotalPrice((prevTotal) =>
        prevTotal +
        cartItems.find((item) => item.item_id === itemId)?.price || 0
      );
    } catch (err) {
      console.error("Error adding item to cart:", err);
    }
  };

  // Remove item or decrement quantity (for the minus button or "Remove" button)
  const removeItemFromCart = async (itemId, removeCompletely = false) => {
    try {
      const item = cartItems.find((cartItem) => cartItem.item_id === itemId);
      if (!item) return;

      if (item.quantity === 1 || removeCompletely) {
        // If quantity is 1 or the user explicitly wants to remove the item
        await axios.delete(`http://localhost:5200/carts/${cartId}/remove-item`, {
          data: { item_id: itemId },
        });
        setCartItems((prevItems) =>
          prevItems.filter((cartItem) => cartItem.item_id !== itemId)
        );
        setTotalPrice((prevTotal) => prevTotal - item.price * item.quantity);
      } else {
        // Decrease the quantity by 1
        await axios.post(`http://localhost:5200/carts/${cartId}/add-item`, {
          item_id: itemId,
          quantity: -1,
        });
        setCartItems((prevItems) =>
          prevItems.map((cartItem) =>
            cartItem.item_id === itemId
              ? { ...cartItem, quantity: cartItem.quantity - 1 }
              : cartItem
          )
        );
        setTotalPrice((prevTotal) => prevTotal - item.price);
      }
    } catch (err) {
      console.error("Error removing item from cart:", err);
    }
  };

  // Handle emptying the cart
  const emptyCart = async () => {
    try {
      await axios.delete(`http://localhost:5200/carts/${cartId}/empty`);
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
                  onClick={() => removeItemFromCart(item.item_id)}
                >
                  -
                </button>
                <span>{item.quantity}</span>
                <button
                  className="plus"
                  onClick={() => addItemToCart(item.item_id)}
                >
                  +
                </button>
              </div>
              <button
                className="remove-item"
                onClick={() => removeItemFromCart(item.item_id, true)} // Remove completely
              >
                Remove
              </button>
            </div>
          ))}
        </div>
      ) : (
        <p>Your cart is empty.</p>
      )}

      <div className="total-price">
        <h3>Total: ${totalPrice.toFixed(2)}</h3>
      </div>

      <div className="cart-buttons">
        <button className="empty-cart" onClick={emptyCart}>
          Empty Cart
        </button>
        <button
          className="checkout"
          onClick={() => navigate("/checkout")}
        >
          Proceed to Checkout
        </button>
      </div>
    </div>
  );
};

export default CartPage;
