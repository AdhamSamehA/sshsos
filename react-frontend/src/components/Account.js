import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';

const Account = () => {
  const { userId } = useParams(); // Get userId from the URL parameter
  const [accountDetails, setAccountDetails] = useState(null);
  const [orderHistory, setOrderHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch account details and order history for the user
  const fetchAccountDetails = async () => {
    setLoading(true); // Set loading state to true before fetching data
    try {
      // Fetch account details
      const accountResponse = await axios.get(`http://localhost:5200/user/account?user_id=${userId}`);
      setAccountDetails(accountResponse.data); // Update state with account details

      // Fetch order history for the user
      const orderResponse = await axios.get(`http://localhost:5200/user/orders?user_id=${userId}`);
      setOrderHistory(orderResponse.data.orders); // Update state with order history
    } catch (err) {
      setError('Error fetching account or order data.');
      console.error(err);
    } finally {
      setLoading(false); // Set loading state to false after fetching data
    }
  };

  useEffect(() => {
    fetchAccountDetails(); // Call function to fetch data when the component mounts
  }, [userId]);

  if (loading) {
    return <p>Loading account details...</p>;
  }

  if (error) {
    return <p>{error}</p>;
  }

  return (
    <div>
      <h2>Account Details</h2>
      {accountDetails && (
        <div>
          <p><strong>Wallet Balance:</strong> ${accountDetails.wallet_balance}</p>
          <p><strong>Address:</strong> {accountDetails.default_address}</p>
          <p><strong>Total Orders:</strong> {accountDetails.total_orders}</p>
        </div>
      )}

      <h3>Order History</h3>
      {orderHistory.length === 0 ? (
        <p>No past orders found.</p>
      ) : (
        <ul>
          {orderHistory.map((order, index) => (
            <li key={index}>
              <p><strong>Order ID:</strong> {order.id}</p>
              <p><strong>Items:</strong> {order.items.join(', ')}</p>
              <p><strong>Total Price:</strong> ${order.total_price}</p>
              <p><strong>Status:</strong> {order.status}</p>
              <hr />
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default Account;
