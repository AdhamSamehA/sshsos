import React, { useState, useEffect } from "react";
import "./Account.css";

function Account() {
  const [accountDetails, setAccountDetails] = useState(null);
  const [addresses, setAddresses] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedAddress, setSelectedAddress] = useState("");

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
        setSelectedAddress(data.default_address); // Set the initial selected address
      } catch (error) {
        console.error("Failed to fetch account details:", error);
      }
    };

    fetchAccountDetails();
  }, []);

  const handleAddressChange = (address) => {
    setSelectedAddress(address);
    setIsModalOpen(false); // Close the modal after selection

    // Optionally send the new address to the backend
    console.log(`Set new default address: ${address}`);
    // Example API call to update default address
    // fetch("http://localhost:5200/user/update-address", {
    //   method: "POST",
    //   headers: { "Content-Type": "application/json" },
    //   body: JSON.stringify({ user_id: 1, new_address: address }),
    // });
  };

  if (!accountDetails) {
    return <div className="account-container">Loading...</div>;
  }

  return (
    <div className="account-container">
      <h2>Account Details</h2>
      <div className="account-item">
        <strong>Wallet Balance:</strong> ${accountDetails.wallet_balance.toFixed(2)}
        <button className="button">TOP UP</button>
      </div>
      <div className="account-item">
        <strong>Default Address:</strong>
        <span className="default-address" onClick={() => setIsModalOpen(true)}>
          {selectedAddress}
        </span>
      </div>
      <div className="account-item">
        <strong>Total Orders:</strong>
        <span className="clickable"> {accountDetails.total_orders}</span>
      </div>

      {/* Modal for address selection */}
      {isModalOpen && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>Select Address</h3>
            <ul className="address-list">
              {addresses.map((address, index) => (
                <li
                  key={index}
                  className={`address-item ${address === selectedAddress ? "selected" : ""}`}
                  onClick={() => handleAddressChange(address)}
                >
                  {address}
                </li>
              ))}
            </ul>
            <button className="button close-btn" onClick={() => setIsModalOpen(false)}>
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default Account;
