import pytest
from httpx import AsyncClient
from server.app import app  # Replace with the correct path to your FastAPI app

BASE_URL = "http://localhost:5200"  # Adjust to match your app's base URL

@pytest.mark.asyncio
async def test_integration_workflow():
    async with AsyncClient(base_url=BASE_URL) as client:
        # Step 1: Create a New Cart
        create_cart_payload = {"supermarket_id": 1, "user_id": 1}
        response = await client.post("/carts/create", json=create_cart_payload)
        assert response.status_code == 200
        cart_id = response.json()["cart_id"]

        # Step 2: Add Items to the Cart
        add_item_payload = {"item_id": 1, "quantity": 2}
        response = await client.post(f"/carts/{cart_id}/add-item", json=add_item_payload)
        assert response.status_code == 200

        # Step 3: View Cart
        response = await client.get(f"/carts/{cart_id}")
        assert response.status_code == 200
        cart_items = response.json()["items"]
        assert len(cart_items) > 0

        # Step 4: Order Now
        order_payload = {"order_time": "now", "address_id": 1, "payment_method": "credit_card"}
        response = await client.post(f"/carts/{cart_id}/submit-delivery", json=order_payload)
        assert response.status_code == 200

        # Step 5: Create Another Cart
        response = await client.post("/carts/create", json=create_cart_payload)
        assert response.status_code == 200
        new_cart_id = response.json()["cart_id"]

        # Add Items to the New Cart
        response = await client.post(f"/carts/{new_cart_id}/add-item", json=add_item_payload)
        assert response.status_code == 200

        # View the New Cart
        response = await client.get(f"/carts/{new_cart_id}")
        assert response.status_code == 200

        # Schedule an Order
        scheduled_order_payload = {"order_time": "schedule", "address_id": 1, "delivery_date": "2023-12-12"}
        response = await client.post(f"/carts/{new_cart_id}/submit-delivery", json=scheduled_order_payload)
        assert response.status_code == 200

        # Step 6: View My Orders
        response = await client.get("/orders?user_id=1")
        assert response.status_code == 200
        orders = response.json()
        assert len(orders) > 0

        # Step 7: View Order Details
        order_id = orders[0]["order_id"]
        response = await client.get(f"/order/details?order_id={order_id}")
        assert response.status_code == 200

        # Step 8: View Shared Orders Test
        response = await client.get("/shared-orders-test?user_id=1")
        assert response.status_code == 200
