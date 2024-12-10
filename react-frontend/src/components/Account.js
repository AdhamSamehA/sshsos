import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./Account.css";

function Account() {
  const [accountDetails, setAccountDetails] = useState(null);
  const [addresses, setAddresses] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);

  const navigate = useNavigate();

  useEffect(() => {
    const fetchAccountDetails = async () => {
      try {
        const response = await fetch("http://localhost:5200/user/account?user_id=1");
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setAccountDetails(data);

        // Mock addresses for now
        setAddresses([
          "123 Main Street, Springfield",
          "456 Elm Street, Shelbyville",
          "789 Oak Avenue, Capital City",
        ]);
      } catch (error) {
        console.error("Failed to fetch account details:", error);
      }
    };

    fetchAccountDetails();
  }, []);

  const handleAddressEdit = () => {
    setShowDropdown((prev) => !prev); // Toggle dropdown visibility
  };

  const handleSelectAddress = (address) => {
    setAccountDetails((prev) => ({
      ...prev,
      default_address: address,
    }));
    setShowDropdown(false); // Close dropdown after selection
  };

  if (!accountDetails) {
    return <div className="account-container">Loading...</div>;
  }

  return (
    <div className="account-container">
      <h2>My Account</h2>
      <div className="account-list">
        {/* Wallet Balance */}
        <div className="account-item">
          <div className="account-icon">
            <i className="fas fa-wallet"></i>
          </div>
          <div className="account-info">
            <h4>Wallet Balance</h4>
            <p>${accountDetails.wallet_balance.toFixed(2)}</p>
          </div>
          <div className="account-action">
            <button className="button">Top Up</button>
          </div>
        </div>

        {/* Default Address */}
        <div className="account-item">
          <div className="account-icon">
            <i className="fas fa-map-marker-alt"></i>
          </div>
          <div className="account-info">
            <h4>Default Address</h4>
            <p>{accountDetails.default_address}</p>
            {showDropdown && (
              <ul className="dropdown-list">
                {addresses.map((address, index) => (
                  <li
                    key={index}
                    onClick={() => handleSelectAddress(address)}
                    className="dropdown-item"
                  >
                    {address}
                  </li>
                ))}
              </ul>
            )}
          </div>
          <div className="account-action">
            <button className="button" onClick={handleAddressEdit}>
              Edit
            </button>
          </div>
        </div>

        {/* Total Orders */}
        <div className="account-item" onClick={() => navigate("/total-orders")}>
          <div className="account-icon">
            <i className="fas fa-shopping-basket"></i>
          </div>
          <div className="account-info">
            <h4>Total Orders</h4>
            <p>{accountDetails.total_orders}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Account;
