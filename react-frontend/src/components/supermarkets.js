import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './supermarkets.css'; // Import CSS for styling

const Supermarkets = () => {
  const [supermarkets, setSupermarkets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  // Fetch supermarkets data
  useEffect(() => {
    const fetchSupermarkets = async () => {
      try {
        const response = await axios.get('http://localhost:5200/supermarket/feed');
        setSupermarkets(response.data.supermarkets);
      } catch (err) {
        setError('Error fetching supermarkets');
        console.error(err);
      }
      setLoading(false);
    };

    fetchSupermarkets();
  }, []);

  // Handle navigation to the shopping page
  const handleNavigate = (supermarketId) => {
    navigate(`/supermarketshopping/${supermarketId}`);
  };

  return (
    <div className="supermarket-container">
      <h2>Available Supermarkets</h2>

      {loading ? (
        <p>Loading...</p>
      ) : error ? (
        <p>{error}</p>
      ) : (
        <div className="supermarket-list">
          {supermarkets.map((supermarket) => (
            <div
              key={supermarket.id}
              className="supermarket-card"
              onClick={() => handleNavigate(supermarket.id)}
            >
              <img
                src={supermarket.photo_url}
                alt={supermarket.name}
                className="supermarket-image"
              />
              <div className="supermarket-details">
                <h3>{supermarket.name}</h3>
                <p><strong>Address:</strong> {supermarket.address}</p>
                <p><strong>Phone:</strong> {supermarket.phone_number}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Supermarkets;
