import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Supermarkets from './components/supermarkets';
import SupermarketShopping from './components/SupermarketShopping';
import Items from './components/Items';

function App() {
  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <h1>SSH Delivery Service</h1>
        </header>
        <main>
          <Routes>
            <Route path="/" element={<Supermarkets />} />
            <Route path="/supermarketshopping/:supermarketId" element={<SupermarketShopping />} />
            <Route path="/items/:supermarketId/:categoryId" element={<Items />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
