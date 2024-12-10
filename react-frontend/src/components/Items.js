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
      try {
        const response = await axios.get(
          `http://localhost:5200/items?supermarket_id=${supermarketId}&category_id=${categoryId}`
        );
        setItems(response.data.items || []);
      } catch (err) {
        setError("Error fetching items.");
        console.error(err);
      }
      setLoading(false);
    };

    fetchItems();
  }, [supermarketId, categoryId]);

  // Fetch cart total if a cart exists
  useEffect(() => {
    const fetchCartTotal = async () => {
      if (!cartId) return;

      try {
        const response = await axios.get(`http://localhost:5200/carts/${cartId}`);
        setCartTotal(response.data.total_price || 0);
      } catch (err) {
        console.error("Error fetching cart total:", err);
      }
    };

    fetchCartTotal();
  }, [cartId]);

  // Create a cart if it doesn't exist
  const createCart = async () => {
    if (!cartId) {
      try {
        const response = await axios.post(`http://localhost:5200/carts/create`, {
          user_id: 1,
          supermarket_id: supermarketId,
        });
        const newCartId = response.data.cart_id;
        setCartId(newCartId);
        localStorage.setItem("cartId", newCartId); // Persist cart ID
      } catch (err) {
        console.error("Error creating cart:", err);
      }
    }
  };

  // Add item to cart
  const addToCart = async (item) => {
    try {
      await createCart();

      await axios.post(`http://localhost:5200/carts/${cartId}/add-item`, {
        item_id: item.id,
        quantity: 1,
      });

      const response = await axios.get(`http://localhost:5200/carts/${cartId}`);
      setCartTotal(response.data.total_price || 0);

      setAddedToCart(true);
      setAddedItem(item);

      setTimeout(() => {
        setAddedToCart(false);
        setAddedItem(null);
      }, 2000);
    } catch (err) {
      console.error("Error adding item to cart:", err);
    }
  };

  const viewCart = () => {
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
                <p>Price: ${item.price.toFixed(2)}</p>
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
          View Cart (Total: ${cartTotal.toFixed(2)})
        </button>
      )}
    </div>
  );
};

export default Items;
