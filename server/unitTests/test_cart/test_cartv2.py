import pytest
import httpx
import asyncio

# Base URL for the API
BASE_URL = "http://app:5200"  # Adjust this to match your Docker setup

@pytest.mark.asyncio
async def test_create_cart():
    """
    Test creating a new cart
    """
    async with httpx.AsyncClient() as client:
        # Assuming you have test data for user_id and supermarket_id
        payload = {
            "user_id": 1,  # Replace with an actual user ID from your test data
            "supermarket_id": 1  # Replace with an actual supermarket ID from your test data
        }
        
        response = await client.post(f"{BASE_URL}/carts/create", json=payload)
        
        assert response.status_code == 200, f"Failed to create cart. Response: {response.text}"
        
        # Validate response structure
        result = response.json()
        assert "cart_id" in result
        assert "user_id" in result
        assert "supermarket_id" in result
        assert "message" in result

@pytest.mark.asyncio
async def test_add_item_to_cart():
    """
    Test adding an item to an existing cart
    """
    async with httpx.AsyncClient() as client:
        # First, create a cart
        create_payload = {
            "user_id": 1,
            "supermarket_id": 1
        }
        create_response = await client.post(f"{BASE_URL}/carts/create", json=create_payload)
        create_result = create_response.json()
        cart_id = create_result["cart_id"]

        # Then add an item to the cart
        add_item_payload = {
            "item_id": 1,  # Replace with an actual item ID from your test data
            "quantity": 2
        }
        
        response = await client.post(f"{BASE_URL}/carts/{cart_id}/add-item", json=add_item_payload)
        
        assert response.status_code == 200, f"Failed to add item to cart. Response: {response.text}"
        
        # Validate response structure
        result = response.json()
        assert "cart_id" in result
        assert "supermarket_id" in result
        assert "message" in result

@pytest.mark.asyncio
async def test_view_cart():
    """
    Test viewing cart contents
    """
    async with httpx.AsyncClient() as client:
        # First, create a cart and add an item
        create_payload = {
            "user_id": 1,
            "supermarket_id": 1
        }
        create_response = await client.post(f"{BASE_URL}/carts/create", json=create_payload)
        create_result = create_response.json()
        cart_id = create_result["cart_id"]

        # Add an item to the cart
        add_item_payload = {
            "item_id": 1,
            "quantity": 2
        }
        await client.post(f"{BASE_URL}/carts/{cart_id}/add-item", json=add_item_payload)

        # View the cart
        response = await client.get(f"{BASE_URL}/carts/{cart_id}")
        
        assert response.status_code == 200, f"Failed to view cart. Response: {response.text}"
        
        # Validate response structure
        result = response.json()
        assert "cart_id" in result
        assert "items" in result
        assert "total_price" in result
        assert "wallet_balance" in result

@pytest.mark.asyncio
async def test_remove_item_from_cart():
    """
    Test removing an item from the cart
    """
    async with httpx.AsyncClient() as client:
        # First, create a cart and add an item
        create_payload = {
            "user_id": 1,
            "supermarket_id": 1
        }
        create_response = await client.post(f"{BASE_URL}/carts/create", json=create_payload)
        create_result = create_response.json()
        cart_id = create_result["cart_id"]

        # Add an item to the cart
        add_item_payload = {
            "item_id": 1,
            "quantity": 2
        }
        await client.post(f"{BASE_URL}/carts/{cart_id}/add-item", json=add_item_payload)

        # Remove the item from the cart
        remove_item_payload = {
            "item_id": 1
        }
        response = await client.delete(f"{BASE_URL}/carts/{cart_id}/remove-item", json=remove_item_payload)
        
        assert response.status_code == 200, f"Failed to remove item from cart. Response: {response.text}"
        
        # Validate response structure
        result = response.json()
        assert "cart_id" in result
        assert "supermarket_id" in result
        assert "message" in result

@pytest.mark.asyncio
async def test_empty_cart():
    """
    Test emptying the entire cart
    """
    async with httpx.AsyncClient() as client:
        # First, create a cart and add items
        create_payload = {
            "user_id": 1,
            "supermarket_id": 1
        }
        create_response = await client.post(f"{BASE_URL}/carts/create", json=create_payload)
        create_result = create_response.json()
        cart_id = create_result["cart_id"]

        # Add multiple items to the cart
        for item_id in [1, 2, 3]:  # Replace with actual item IDs
            add_item_payload = {
                "item_id": item_id,
                "quantity": 1
            }
            await client.post(f"{BASE_URL}/carts/{cart_id}/add-item", json=add_item_payload)

        # Empty the cart
        response = await client.delete(f"{BASE_URL}/carts/{cart_id}/empty")
        
        assert response.status_code == 200, f"Failed to empty cart. Response: {response.text}"
        
        # Validate response structure
        result = response.json()
        assert "cart_id" in result
        assert "supermarket_id" in result
        assert "message" in result