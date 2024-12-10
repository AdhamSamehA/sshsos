import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './CartPage.css'; // Ensure this CSS is applied

const CartPage = () => {
  const [cartItems, setCartItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [totalPrice, setTotalPrice] = useState(0);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  // Fetch cart data from backend (get items, quantities, etc.)
  useEffect(() => {
    const fetchCartItems = async () => {
      try {
        const response = await axios.get(`http://localhost:5200/carts/12345`); // Adjust based on your cartId
        setCartItems(response.data.items);  // Assuming your response includes items with quantity and price
        setTotalPrice(response.data.total_price);  // Assuming the backend returns a total price
      } catch (err) {
        setError("Error fetching cart data");
        console.error(err);
      }
      setLoading(false);
    };

    fetchCartItems();
  }, []);

  // Handle the quantity change (plus/minus)
  const updateQuantity = async (itemId, quantity) => {
    try {
      const response = await axios.put(`http://localhost:5200/carts/12345/update`, {
        itemId,
        quantity,
      });
      setCartItems(response.data.items); // Update the cart with the new item list
      setTotalPrice(response.data.total_price);  // Update the total price
    } catch (err) {
      console.error("Error updating quantity:", err);
    }
  };

  // Handle removing an item from the cart
  const removeItemFromCart = async (itemId) => {
    try {
      const response = await axios.post(`http://localhost:5200/carts/12345/remove-item`, { itemId });
      setCartItems(response.data.items); // Update cart items
      setTotalPrice(response.data.total_price);  // Update total price
    } catch (err) {
      console.error("Error removing item:", err);
    }
  };

  // Handle emptying the cart
  const emptyCart = async () => {
    try {
      const response = await axios.post(`http://localhost:5200/carts/12345/empty`);
      setCartItems([]); // Empty the cart
      setTotalPrice(0);  // Reset total price
    } catch (err) {
      console.error("Error emptying the cart:", err);
    }
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>{error}</div>;
  }

  return (
    <div className="cart-page">
      <h2>Your Shopping Cart</h2>

      {/* Display cart items */}
      {cartItems.length > 0 ? (
        <div className="cart-items">
          {cartItems.map((item) => (
            <div key={item.item_id} className="cart-item">
              <img src={item.photo_url} alt={item.name} className="item-photo" />
              <div className="item-info">
                <h3>{item.name}</h3>
                <p className="item-price">${item.price.toFixed(2)}</p>
              </div>
              <div className="quantity-controls">
                <button
                  className="minus"
                  onClick={() => updateQuantity(item.item_id, item.quantity - 1)}
                >
                  -
                </button>
                <span>{item.quantity}</span>
                <button
                  className="plus"
                  onClick={() => updateQuantity(item.item_id, item.quantity + 1)}
                >
                  +
                </button>
              </div>
              <button className="remove-item" onClick={() => removeItemFromCart(item.item_id)}>
                Remove
              </button>
            </div>
          ))}
        </div>
      ) : (
        <p>Your cart is empty.</p>
      )}

      {/* Display total price */}
      <div className="total-price">
        <h3>Total: ${totalPrice.toFixed(2)}</h3>
      </div>

      {/* Buttons */}
      <div className="cart-buttons">
        <button className="empty-cart" onClick={emptyCart}>Empty Cart</button>
        <button className="checkout" onClick={() => navigate('/checkout')}>Proceed to Checkout</button>
      </div>
    </div>
  );
};

export default CartPage;
