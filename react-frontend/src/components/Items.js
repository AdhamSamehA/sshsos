import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import "./Items.css";

const Items = () => {
  const { supermarketId, categoryId } = useParams();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [cartId, setCartId] = useState(localStorage.getItem("cartId") || null);
  const [cartTotal, setCartTotal] = useState(0);
  const [addedToCart, setAddedToCart] = useState(false);
  const [addedItem, setAddedItem] = useState(null);
  const navigate = useNavigate();

  // Fetch items for the current supermarket and category
  useEffect(() => {
    const fetchItems = async () => {
      console.log(`Fetching items for supermarket ID: ${supermarketId}, category ID: ${categoryId}...`);
      try {
        const response = await axios.get(
          `http://localhost:5200/items?supermarket_id=${supermarketId}&category_id=${categoryId}`
        );
        setItems(response.data.items || []);
        console.log("Items fetched successfully:", response.data.items);
      } catch (err) {
        setError("Error fetching items.");
        console.error("Error fetching items:", err);
      }
      setLoading(false);
    };

    fetchItems();
  }, [supermarketId, categoryId]);

  // Fetch cart total if a cart exists
  useEffect(() => {
    const fetchCartTotal = async () => {
      if (!cartId) {
        console.log("No cart ID found. Skipping cart total fetch.");
        return;
      }

      console.log(`Fetching cart total for cart ID: ${cartId}...`);
      try {
        const response = await axios.get(`http://localhost:5200/carts/${cartId}`);
        setCartTotal(response.data.total_price || 0);
        console.log("Cart total fetched successfully:", response.data.total_price);
      } catch (err) {
        console.error("Error fetching cart total:", err);
      }
    };

    fetchCartTotal();
  }, [cartId]);

  // Create a cart if it doesn't exist
  const createCart = async () => {
    if (!cartId) {
      console.log("No cart ID found. Creating a new cart...");
      try {
        const response = await axios.post(`http://localhost:5200/carts/create`, {
          user_id: 1,
          supermarket_id: supermarketId,
        });
        const newCartId = response.data.cart_id;
        setCartId(newCartId);
        localStorage.setItem("cartId", newCartId); // Persist cart ID
        console.log("New cart created successfully. Cart ID:", newCartId);
      } catch (err) {
        console.error("Error creating cart:", err);
      }
    }
  };

  // Add item to cart
  const addToCart = async (item) => {
    console.log(`Adding item to cart:`, item);
    try {
      await createCart();
      console.log(`Adding item ID: ${item.id} to cart ID: ${cartId}...`);
      await axios.post(`http://localhost:5200/carts/${cartId}/add-item`, {
        item_id: item.id,
        quantity: 1,
      });

      console.log("Item added successfully. Updating cart total...");
      const response = await axios.get(`http://localhost:5200/carts/${cartId}`);
      setCartTotal(response.data.total_price || 0);

      setAddedToCart(true);
      setAddedItem(item);
      console.log("Item added to cart successfully:", item);

      setTimeout(() => {
        setAddedToCart(false);
        setAddedItem(null);
      }, 2000);
    } catch (err) {
      console.error("Error adding item to cart:", err);
    }
  };

  const viewCart = () => {
    console.log("Navigating to cart page...");
    navigate("/cart");
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
          {items.map((item) => (
            <div key={item.id} className="item-card">
              <img
                src={item.photo_url}
                alt={item.name}
                className="item-image"
                onError={(e) => {
                  e.target.src = "https://via.placeholder.com/150";
                }}
              />
              <div className="item-details">
                <h3>{item.name}</h3>
                <p>{item.description}</p>
                <p>Price: AED {item.price.toFixed(2)}</p>
                <button onClick={() => addToCart(item)}>Add to Cart</button>
              </div>
            </div>
          ))}
        </div>
      )}

      {addedToCart && (
        <div className="popup">
          <p>{addedItem?.name} added to cart!</p>
          <button onClick={viewCart}>View Cart</button>
        </div>
      )}

      {cartId && (
        <button className="view-cart-btn" onClick={viewCart}>
          View Cart (Total: AED {cartTotal.toFixed(2)})
        </button>
      )}
    </div>
  );
};

export default Items;
