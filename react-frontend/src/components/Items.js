import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import "./Items.css"; // CSS for styling

const Items = () => {
  const { supermarketId, categoryId } = useParams(); // Get IDs from the URL
  const [items, setItems] = useState([]); // List of items in the current category
  const [loading, setLoading] = useState(true); // Loading state
  const [error, setError] = useState(null); // Error state
  const [cartId, setCartId] = useState(localStorage.getItem("cartId") || null); // Persistent cart ID
  const [cartItems, setCartItems] = useState(JSON.parse(localStorage.getItem("cartItems")) || []); // Persistent cart items
  const [addedToCart, setAddedToCart] = useState(false); // To show the popup
  const [addedItem, setAddedItem] = useState(null); // Tracks the item added to the cart
  const navigate = useNavigate();

  // Fetch items based on supermarketId and categoryId
  useEffect(() => {
    const fetchItems = async () => {
      try {
        const response = await axios.get(
          `http://localhost:5200/items?supermarket_id=${supermarketId}&category_id=${categoryId}`
        );
        setItems(response.data.items); // Set items from the backend
      } catch (err) {
        setError("Error fetching items");
        console.error(err);
      }
      setLoading(false);
    };

    fetchItems();
  }, [supermarketId, categoryId]);

  // Create a cart if it doesn't already exist
  const createCart = async () => {
    if (!cartId) {
      try {
        const response = await axios.post(`http://localhost:5200/carts/create`, {
          user_id: 1, // Replace with the actual user ID
          supermarket_id: supermarketId,
        });
        const newCartId = response.data.cart_id;
        setCartId(newCartId); // Store the created cart ID
        localStorage.setItem("cartId", newCartId); // Persist cart ID
      } catch (err) {
        console.error("Error creating cart:", err);
      }
    }
  };

  // Add item to the cart
  const addToCart = async (item) => {
    try {
      // Create the cart if it doesn't exist
      await createCart();

      // Add the item to the cart in the backend
      await axios.post(`http://localhost:5200/carts/${cartId}/add-item`, {
        item_id: item.id,
        quantity: 1, // Default quantity to add
      });

      // Update the cart items locally
      const existingItem = cartItems.find((cartItem) => cartItem.id === item.id);
      if (existingItem) {
        // Update the quantity of the existing item
        const updatedCartItems = cartItems.map((cartItem) =>
          cartItem.id === item.id
            ? { ...cartItem, quantity: cartItem.quantity + 1 }
            : cartItem
        );
        setCartItems(updatedCartItems);
        localStorage.setItem("cartItems", JSON.stringify(updatedCartItems));
      } else {
        // Add a new item to the cart
        const updatedCartItems = [...cartItems, { ...item, quantity: 1 }];
        setCartItems(updatedCartItems);
        localStorage.setItem("cartItems", JSON.stringify(updatedCartItems));
      }

      // Show the popup with the item added
      setAddedToCart(true);
      setAddedItem(item);

      // Hide the popup after 2 seconds
      setTimeout(() => {
        setAddedToCart(false);
        setAddedItem(null);
      }, 2000);
    } catch (err) {
      console.error("Error adding item to cart:", err);
    }
  };

  // Navigate to the Cart page
  const viewCart = () => {
    navigate("/cart"); // Navigate to the cart page
  };

  return (
    <div>
      <h2>Items</h2>
      {loading ? (
        <p>Loading...</p>
      ) : error ? (
        <p>{error}</p>
      ) : (
        <div className="items-container">
          {items.length > 0 ? (
            items.map((item) => (
              <div key={item.id} className="item-card">
                <img
                  src={item.photo_url} // Backend-provided image
                  alt={item.name}
                  className="item-image"
                  onError={(e) => {
                    e.target.src = "https://via.placeholder.com/150"; // Fallback if image doesn't load
                  }}
                />
                <div className="item-details">
                  <h3>{item.name}</h3>
                  <p>{item.description}</p>
                  <p>Price: ${item.price.toFixed(2)}</p>
                  <button onClick={() => addToCart(item)}>Add to Cart</button>
                </div>
              </div>
            ))
          ) : (
            <p>No items available</p>
          )}
        </div>
      )}

      {/* Confirmation Popup */}
      {addedToCart && (
        <div className="popup">
          <p>{addedItem?.name} added to cart!</p>
          <button onClick={viewCart}>View Cart</button>
        </div>
      )}

      {/* View Cart Button (only if cart is created) */}
      {cartId && (
        <button className="view-cart-btn" onClick={viewCart}>
          View Cart
        </button>
      )}
    </div>
  );
};

export default Items;
