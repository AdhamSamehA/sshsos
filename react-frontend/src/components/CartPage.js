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
      console.log("Fetching cart data for cart ID:", cartId);
      try {
        if (!cartId) {
          console.warn("Cart not found.");
          setError("Cart not found.");
          setLoading(false);
          return;
        }

        const response = await axios.get(`http://localhost:5200/carts/${cartId}`);
        setCartItems(response.data.items || []);
        setTotalPrice(response.data.total_price || 0);
        console.log("Cart data fetched successfully:", response.data);
      } catch (err) {
        console.error("Error fetching cart data:", err);
        setError("Error fetching cart data. Please try again.");
      }
      setLoading(false);
    };

    fetchCartData();
  }, [cartId]); // Dependency array ensures it runs whenever cartId changes

  // Add item to cart (for the plus button)
  const addItemToCart = async (itemId) => {
    console.log("Adding item to cart:", itemId);
    try {
      await axios.post(`http://localhost:5200/carts/${cartId}/add-item`, {
        item_id: itemId,
        quantity: 1,
      });

      console.log("Item added successfully. Updating cart items...");
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

  // Remove one quantity from the cart
  const removeItemFromCart = async (itemId) => {
    console.log("Removing item from cart:", itemId);
    try {
      const item = cartItems.find((cartItem) => cartItem.item_id === itemId);
      if (!item) {
        console.warn("Item not found in cart:", itemId);
        return;
      }

      await axios.delete(`http://localhost:5200/carts/${cartId}/remove-item`, {
        data: { item_id: itemId },
      });

      console.log("Item removed successfully. Updating cart items...");
      if (item.quantity > 1) {
        // Decrement quantity if more than one exists
        setCartItems((prevItems) =>
          prevItems.map((cartItem) =>
            cartItem.item_id === itemId
              ? { ...cartItem, quantity: cartItem.quantity - 1 }
              : cartItem
          )
        );
        setTotalPrice((prevTotal) => prevTotal - item.price);
      } else {
        // Remove the item entirely if quantity becomes zero
        setCartItems((prevItems) =>
          prevItems.filter((cartItem) => cartItem.item_id !== itemId)
        );
        setTotalPrice((prevTotal) => prevTotal - item.price);
      }
    } catch (err) {
      console.error("Error removing item from cart:", err);
    }
  };

  // Handle emptying the cart
  const emptyCart = async () => {
    console.log("Emptying cart...");
    try {
      await axios.delete(`http://localhost:5200/carts/${cartId}/empty`);
      setCartItems([]); // Empty cart items
      setTotalPrice(0); // Reset total price
      console.log("Cart emptied successfully.");
    } catch (err) {
      console.error("Error emptying the cart:", err);
    }
  };

  if (loading) {
    console.log("Loading cart data...");
    return <div>Loading...</div>;
  }

  if (error) {
    console.error("Error state:", error);
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
                <p className="item-price">AED {item.price.toFixed(2)}</p>
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
                onClick={() => removeItemFromCart(item.item_id)} // Remove one quantity
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
        <h3>Total: AED {totalPrice.toFixed(2)}</h3>
      </div>

      <div className="cart-buttons">
        <button className="empty-cart" onClick={emptyCart}>
          Empty Cart
        </button>
        <button
          className="checkout"
          onClick={() => {
            console.log("Navigating to checkout page...");
            navigate("/checkout");
          }}
        >
          Proceed to Checkout
        </button>
      </div>
    </div>
  );
};

export default CartPage;
