import React from 'react';
import Supermarkets from './components/supermarkets';  // Import the Supermarkets component

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Supermarket Delivery Service</h1>
      </header>
      <main>
        <Supermarkets />  {/* Use the Supermarkets component here */}
      </main>
    </div>
  );
}

export default App;
