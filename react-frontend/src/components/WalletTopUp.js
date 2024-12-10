import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./WalletTopUp.css";

function WalletTopUp() {
  const [amount, setAmount] = useState("");
  const [currentBalance, setCurrentBalance] = useState(null);
  const [message, setMessage] = useState(null); // General message for both success and error
  const [isError, setIsError] = useState(false); // To differentiate between success and error messages
  const navigate = useNavigate();

  useEffect(() => {
    const fetchBalance = async () => {
      try {
        const response = await fetch("http://localhost:5200/wallet/balance?user_id=1");
        const data = await response.json();
        if (response.ok) {
          setCurrentBalance(data.balance);
        } else {
          console.error("Failed to fetch wallet balance:", data.detail);
        }
      } catch (error) {
        console.error("Error fetching balance:", error);
      }
    };
    fetchBalance();
  }, []);

  const handleSubmit = async () => {
    if (!amount || isNaN(amount) || parseFloat(amount) <= 0) {
      setMessage("Please enter a valid amount."); // Set error message
      setIsError(true); // Mark as an error
      return;
    }
    try {
      const response = await fetch("http://localhost:5200/wallet/top-up", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ user_id: 1, amount: parseFloat(amount) }),
      });

      const data = await response.json();
      if (response.ok) {
        setMessage(
          `Amount: $${amount} added successfully. New balance is: $${data.balance.toFixed(2)}`
        );
        setIsError(false); // Mark as success
        setCurrentBalance(data.balance);
        setAmount(""); // Clear the input field

        // Redirect to Supermarkets.js after 3 seconds
        setTimeout(() => {
          navigate("/");
        }, 3000);
      } else {
        setMessage(`Failed to top up wallet: ${data.detail}`);
        setIsError(true); // Mark as an error
      }
    } catch (error) {
      console.error("Error during top-up:", error);
      setMessage("An error occurred. Please try again.");
      setIsError(true); // Mark as an error
    }
  };

  return (
    <div className="wallet-topup-container">
      <div className="wallet-topup-box">
        <h2>Wallet Top-Up</h2>
        {currentBalance !== null && (
          <p className="current-balance">Current Balance: ${currentBalance.toFixed(2)}</p>
        )}
        <p>Enter Top-Up Amount</p>
        <input
          type="number"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          placeholder="Enter amount"
        />
        <div className="wallet-topup-actions">
          <button className="button" onClick={handleSubmit}>
            Submit
          </button>
          <button className="button cancel" onClick={() => navigate("/account")}>
            Cancel
          </button>
        </div>
        {message && (
          <div className={`message-box ${isError ? "error-message" : "success-message"}`}>
            <p>{message}</p>
            {!isError && (
              <p className="redirect-message" onClick={() => navigate("/")}>
                Click here to return to Supermarkets.
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default WalletTopUp;
