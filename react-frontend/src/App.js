import React from "react";
import { BrowserRouter as Router, Route, Routes, Link } from "react-router-dom";
import Supermarkets from "./components/supermarkets";
import SupermarketShopping from "./components/SupermarketShopping";
import Items from "./components/Items";
import CartPage from "./components/CartPage";
import Account from "./components/Account";
import WalletTopUp from "./components/WalletTopUp"; // Import WalletTopUp component
import TotalOrders from "./components/TotalOrders"; // Import TotalOrders component
import "./App.css";

function App() {
  return (
    <Router>
      <div className="App">
        <header className="App-header">
          {/* Home Icon */}
          <Link to="/" className="home-icon">
            <img
              src="https://cdn-icons-png.flaticon.com/512/1946/1946436.png" // Home icon URL
              alt="Home"
              className="home-icon-img"
            />
          </Link>
          <h1>SSH Delivery Service</h1>
          {/* User Icon */}
          <Link to="/account" className="user-icon">
            <img
              src="https://images.rawpixel.com/image_png_social_square/cHJpdmF0ZS9sci9pbWFnZXMvd2Vic2l0ZS8yMDIzLTAxL3JtNjA5LXNvbGlkaWNvbi13LTAwMi1wLnBuZw.png"
              alt="User Account"
              className="user-icon-img"
            />
          </Link>
        </header>
        <main>
          <Routes>
            <Route path="/" element={<Supermarkets />} />
            <Route
              path="/supermarketshopping/:supermarketId"
              element={<SupermarketShopping />}
            />
            <Route
              path="/items/:supermarketId/:categoryId"
              element={<Items />}
            />
            <Route path="/cart" element={<CartPage />} />
            <Route path="/checkout" element={<CheckoutPage />} />
            <Route path="/order-confirmation" element={<OrderConfirmationPage />} />
            <Route path="/account" element={<Account />} />
            <Route path="/wallet-topup" element={<WalletTopUp />} /> {/* Add WalletTopUp route */}
            <Route path="/total-orders" element={<TotalOrders />} /> {/* Add TotalOrders route */}
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
