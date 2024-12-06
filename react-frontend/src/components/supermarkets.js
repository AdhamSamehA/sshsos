import React, { useEffect, useState } from 'react';
import axios from 'axios';

const Supermarkets = () => {
  const [supermarkets, setSupermarkets] = useState([]);

  useEffect(() => {
    const fetchSupermarkets = async () => {
      try {
        const response = await axios.get('http://localhost:5200/supermarket/feed');  // Updated to match backend
        setSupermarkets(response.data.supermarkets);
      } catch (error) {
        console.error('Error fetching supermarkets:', error);
      }
    };

    fetchSupermarkets();
  }, []);

  return (
    <div>
      <h2>Available Supermarkets</h2>
      {supermarkets.length === 0 ? (
        <p>Loading...</p>
      ) : (
        supermarkets.map((supermarket) => (
          <div key={supermarket.id}>
            <p>{supermarket.name}</p>
            <p>{supermarket.address}</p>
          </div>
        ))
      )}
    </div>
  );
};

export default Supermarkets;
