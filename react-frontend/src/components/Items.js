import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Items.css'; // CSS for styling

const Items = () => {
  const { supermarketId, categoryId } = useParams(); // Get IDs from the URL
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [addedToCart, setAddedToCart] = useState(false); // To show the popup
  const [cartItems, setCartItems] = useState([]); // To track items in the cart
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
        setError('Error fetching items');
        console.error(err);
      }
      setLoading(false);
    };

    fetchItems();
  }, [supermarketId, categoryId]);

  // Add item to cart simulation
  const addToCart = async (item) => {
    try {
      // Here we simulate adding the item to the cart.
      // Normally, you would call an API to add the item to the backend cart.

      // Add the item to the cart array (mocking the backend operation)
      setCartItems([...cartItems, { ...item, quantity: 1 }]);

      // Show the popup confirmation
      setAddedToCart(true);

      // Set a timeout to hide the popup after 2 seconds
      setTimeout(() => {
        setAddedToCart(false);
      }, 2000);
    } catch (err) {
      console.error('Error adding item to cart:', err);
    }
  };

  // Navigate to the Cart page
  const viewCart = () => {
    navigate('/cart');
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
                  <p>Price: ${item.price}</p>
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
          <p>Item added to cart!</p>
        </div>
      )}

      {/* View Cart Button */}
      <button className="view-cart-btn" onClick={viewCart}>View Cart</button>
    </div>
  );
};

export default Items;
