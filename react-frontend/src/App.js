import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import Supermarkets from './components/supermarkets';
import SupermarketShopping from './components/SupermarketShopping';
import Items from './components/Items';
import CartPage from './components/CartPage';
import Account from './components/Account';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <header className="App-header">
          {/* User Icon */}
          <Link to="/account" className="user-icon">
            <img
              src="https://images.rawpixel.com/image_png_social_square/cHJpdmF0ZS9sci9pbWFnZXMvd2Vic2l0ZS8yMDIzLTAxL3JtNjA5LXNvbGlkaWNvbi13LTAwMi1wLnBuZw.png" // Path to user icon image
              alt="User Account"
              className="user-icon-img"
            />
          </Link>
          <h1>SSH Delivery Service</h1>
        </header>
        <main>
          <Routes>
            <Route path="/" element={<Supermarkets />} />
            <Route path="/supermarketshopping/:supermarketId" element={<SupermarketShopping />} />
            <Route path="/items/:supermarketId/:categoryId" element={<Items />} />
            <Route path="/cart" element={<CartPage />} />
            <Route path="/account" element={<Account />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
