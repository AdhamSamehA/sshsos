import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./Account.css";

function Account() {
  const [accountDetails, setAccountDetails] = useState(null);
  const [addresses, setAddresses] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    // Fetch account details
    const fetchAccountDetails = async () => {
      try {
        console.log("Fetching account details...");
        const response = await fetch("http://localhost:5200/user/account?user_id=1");
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setAccountDetails(data);
        console.log("Account details fetched:", data);
      } catch (error) {
        console.error("Failed to fetch account details:", error);
      }
    };

    // Fetch addresses using the Order API
    const fetchAddresses = async () => {
      try {
        console.log("Fetching addresses...");
        const response = await fetch("http://localhost:5200/user/addresses?user_id=1");
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        const addressDetails = data.addresses.map((address) => address.address_details);
        setAddresses(addressDetails);
        console.log("Addresses fetched:", addressDetails);
      } catch (error) {
        console.error("Failed to fetch addresses:", error);
      }
    };

    fetchAccountDetails();
    fetchAddresses();
  }, []);

  const handleAddressEdit = () => {
    console.log("Toggling address dropdown...");
    setShowDropdown((prev) => !prev); // Toggle dropdown visibility
  };

  const handleSelectAddress = (address) => {
    console.log("Address selected:", address);
    setAccountDetails((prev) => ({
      ...prev,
      default_address: address,
    }));
    setShowDropdown(false); // Close dropdown after selection
  };

  if (!accountDetails) {
    console.log("Account details loading...");
    return <div className="account-container">Loading...</div>;
  }

  return (
    <div className="account-container">
      <h2>My Account</h2>
      <div className="account-list">
        {/* Wallet Balance */}
        <div className="account-item">
          <div className="account-info">
            <h4>Wallet Balance</h4>
            <p>${accountDetails.wallet_balance.toFixed(2)}</p>
          </div>
          <div className="account-action">
            <button
              className="button"
              onClick={() => {
                console.log("Navigating to wallet top-up...");
                navigate("/wallet-topup");
              }}
            >
              Top Up
            </button>
          </div>
        </div>

        {/* Default Address */}
        <div className="account-item">
          <div className="account-info">
            <h4>Default Address</h4>
            <p>{accountDetails.default_address}</p>
          </div>
          <div className="account-action">
            <button className="button" onClick={handleAddressEdit}>
              Select Address
            </button>
          </div>
        </div>
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

        {/* Total Orders */}
        <div className="account-item">
          <div className="account-info">
            <h4>Total Orders</h4>
            <p>{accountDetails.total_orders}</p>
          </div>
          <div className="account-action">
            <button
              className="button"
              onClick={() => {
                console.log("Navigating to total orders...");
                navigate("/total-orders");
              }}
            >
              View Orders
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Account;
