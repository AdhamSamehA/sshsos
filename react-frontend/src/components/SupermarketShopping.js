import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import './SupermarketShopping.css'; // Correct CSS file for styling

const SupermarketShopping = () => {
  const { supermarketId } = useParams(); // Get supermarketId from URL
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  // Fetch categories based on the supermarketId
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await axios.get(`http://localhost:5200/items/categories?supermarket_id=${supermarketId}`);
        setCategories(response.data); // Set categories from the backend
      } catch (err) {
        setError('Error fetching categories');
        console.error(err);
      }
      setLoading(false);
    };

    fetchCategories();
  }, [supermarketId]); // Re-run whenever supermarketId changes

  // Handle category click to navigate to the items page
  const handleCategoryClick = (categoryId) => {
    navigate(`/items/${supermarketId}/${categoryId}`); // Navigate to items page with categoryId
  };

  return (
    <div>
      <h2>Supermarket Shopping</h2>

      {loading ? (
        <p>Loading categories...</p>
      ) : error ? (
        <p>{error}</p>
      ) : (
        <div className="categories-container">
          {categories.length > 0 ? (
            categories.map((category) => (
              <button
                key={category.id}
                className="category-button"
                onClick={() => handleCategoryClick(category.id)}
              >
                {category.name}
              </button>
            ))
          ) : (
            <p>No categories available.</p>
          )}
        </div>
      )}
    </div>
  );
};

export default SupermarketShopping;
