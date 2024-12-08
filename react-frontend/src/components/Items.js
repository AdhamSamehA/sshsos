import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import './Items.css'; // CSS for styling

const Items = () => {
  const { supermarketId, categoryId } = useParams(); // Get IDs from the URL
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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
                    e.target.src = "https://via.placeholder.com/150"; // Fallback image
                  }}
                />
                <h3>{item.name}</h3>
                <p>{item.description}</p>
                <p className="item-price">${item.price.toFixed(2)}</p>
                <button className="add-to-cart-btn">Add to Cart</button>
              </div>
            ))
          ) : (
            <p>No items available for this category.</p>
          )}
        </div>
      )}
    </div>
  );
};

export default Items;
