import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./WalletTopUp.css";

function WalletTopUp() {
  const [topUpAmount, setTopUpAmount] = useState("");
  const [currentBalance, setCurrentBalance] = useState(99960); // Mocked current balance
  const [successMessage, setSuccessMessage] = useState("");
  const navigate = useNavigate();

  const handleTopUp = () => {
    console.log("Top-Up initiated. Entered amount:", topUpAmount);

    const amount = parseFloat(topUpAmount);
    if (isNaN(amount) || amount <= 0) {
      console.error("Invalid top-up amount:", topUpAmount);
      setSuccessMessage("Please enter a valid amount.");
      return;
    }

    const newBalance = currentBalance + amount;
    console.log(`Top-Up successful. Amount: $${amount}, New balance: $${newBalance.toFixed(2)}`);
    setCurrentBalance(newBalance);
    setSuccessMessage(
      `Amount: $${amount} added successfully. New balance is: $${newBalance.toFixed(2)}`
    );
    setTopUpAmount("");
  };

  return (
    <div className="wallet-topup-container">
      <h2>Wallet Top-Up</h2>
      <div className="wallet-box">
        <p>Current Balance: ${currentBalance.toFixed(2)}</p>
        <label htmlFor="topup-amount">Enter Top-Up Amount:</label>
        <input
          type="number"
          id="topup-amount"
          placeholder="Enter amount"
          value={topUpAmount}
          onChange={(e) => {
            console.log("Top-Up amount changed:", e.target.value);
            setTopUpAmount(e.target.value);
          }}
        />
        <div className="wallet-buttons">
          <button className="submit-button" onClick={handleTopUp}>
            Submit
          </button>
          <button
            className="cancel-button"
            onClick={() => {
              console.log("Top-Up canceled. Navigating to home.");
              navigate("/");
            }}
          >
            Cancel
          </button>
        </div>
        {successMessage && (
          <div
            className={`message-box ${
              successMessage.startsWith("Amount:") ? "success" : "error"
            }`}
          >
            <p>{successMessage}</p>
            {successMessage.startsWith("Amount:") && (
              <p>
                <span
                  className="home-link"
                  onClick={() => {
                    console.log("Navigating back to Supermarkets page.");
                    navigate("/");
                  }}
                >
                  Click here to return to Supermarkets.
                </span>
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default WalletTopUp;
