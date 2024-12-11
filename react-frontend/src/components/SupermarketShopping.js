import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import axios from "axios";
import "./SupermarketShopping.css";

const SupermarketShopping = () => {
  const { supermarketId } = useParams(); // Get supermarketId from URL
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  // Static images for categories (frontend assets)
  const categoryImages = {
    "Dairy & Eggs": "https://media.post.rvohealth.io/wp-content/uploads/2020/08/AN480-Eggs-Dairy-732x549-thumb-1-732x549.jpg",
    "Fruits & Vegetables": "https://domf5oio6qrcr.cloudfront.net/medialibrary/11499/3b360279-8b43-40f3-9b11-604749128187.jpg",
    Bakery: "https://blog.dubailocal.ae/wp-content/uploads/2024/06/The-best-Bakeries-in-Dubai-for-enjoying-everything-from-luxury-cakes-to-sourdough.webp",
    "Nuts & Seeds": "https://nyspiceshop.com/cdn/shop/articles/TYPES_OF_NUTS_AND_SEEDS_AND_THEIR_HEALTH_BENEFITS_4960x.jpeg?v=1730226897",
    "Chips & Snacks": "https://platform.vox.com/wp-content/uploads/sites/2/chorus/uploads/chorus_asset/file/13073991/snacksofourlives.0.0.1514259001.jpg?quality=90&strip=all&crop=0,2.072849269111,100,95.854301461778",
    Beverages: "https://nawon.com.vn/wp-content/uploads/2024/01/soft-drinks.jpg",
    "Hygiene & Personal Care": "https://5.imimg.com/data5/QS/TO/MY-44941618/personal-care.jpg",
    "Cereals & Packets": "https://www.outofeden.co.uk/prodimg/4210_1_Zoom.jpg",
    Stationary: "https://www.simplife.ae/product_images/product_1635419586.jpg",
  };

  // Fetch categories based on the supermarketId
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        console.log(`Fetching categories for supermarket ID: ${supermarketId}...`);
        const response = await axios.get(
          `http://localhost:5200/items/categories?supermarket_id=${supermarketId}`
        );
        setCategories(response.data); // Set categories from the backend
        console.log("Categories fetched successfully:", response.data);
      } catch (err) {
        setError("Error fetching categories");
        console.error("Error fetching categories:", err);
      }
      setLoading(false);
    };

    fetchCategories();
  }, [supermarketId]); // Re-run whenever supermarketId changes

  // Handle category click to navigate to the items page
  const handleCategoryClick = (categoryId) => {
    console.log(`Navigating to items page for category ID: ${categoryId}`);
    navigate(`/items/${supermarketId}/${categoryId}`); // Navigate to items page with categoryId
  };

  return (
    <div className="supermarket-shopping">
      <header className="header">
        <h2>24-7 Supermarket</h2>
      </header>

      {loading ? (
        <p>Loading categories...</p>
      ) : error ? (
        <p>{error}</p>
      ) : (
        <div className="categories-container">
          {categories.length > 0 ? (
            categories.map((category) => (
              <div
                key={category.id}
                className="category-card"
                onClick={() => handleCategoryClick(category.id)}
              >
                <img
                  src={categoryImages[category.name] || "/images/default.jpg"}
                  alt={category.name}
                  className="category-image"
                />
                <p className="category-name">{category.name}</p>
              </div>
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
