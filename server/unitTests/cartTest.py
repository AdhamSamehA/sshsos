import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from server.app import app  # Replace 'server.main' with your FastAPI entrypoint file
from server.models import User, Supermarket, Cart
from server.schemas import CreateCartRequest
from server.models.carts import CartStatus


# Fixture for mocking the database session dependency
@pytest.fixture
def mock_db_session():
    return AsyncMock(spec=AsyncSession)


# Test client for async FastAPI app
@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


# Test for creating a cart successfully
@pytest.mark.asyncio
async def test_create_cart_success(mock_db_session, async_client):
    # Mock User and Supermarket existence
    mock_user = User(id=1, name="Test User")
    mock_supermarket = Supermarket(id=1, name="Test Supermarket")
    mock_cart = Cart(id=1, user_id=1, supermarket_id=1)

    async def mock_execute(stmt):
        if "User" in str(stmt):  # Mock user lookup
            return AsyncMock(scalar_one_or_none=lambda: mock_user)
        elif "Supermarket" in str(stmt):  # Mock supermarket lookup
            return AsyncMock(scalar_one_or_none=lambda: mock_supermarket)
        elif "Cart" in str(stmt):  # Mock existing cart lookup
            return AsyncMock(scalar_one_or_none=lambda: None)  # No existing cart
        return AsyncMock(scalar_one_or_none=lambda: None)

    mock_db_session.execute.side_effect = mock_execute

    # Patch the get_db dependency
    with patch("server.dependencies.get_db", return_value=mock_db_session):
        payload = {"user_id": 1, "supermarket_id": 1}
        response = await async_client.post("/carts/create", json=payload)

    assert response.status_code == 200
    assert response.json() == {
        "cart_id": mock_cart.id,
        "user_id": 1,
        "supermarket_id": 1,
        "message": "New cart created successfully."
    }


# Test for missing user
@pytest.mark.asyncio
async def test_create_cart_user_not_found(mock_db_session, async_client):
    async def mock_execute(stmt):
        return AsyncMock(scalar_one_or_none=lambda: None)  # User not found

    mock_db_session.execute.side_effect = mock_execute

    with patch("server.dependencies.get_db", return_value=mock_db_session):
        payload = {"user_id": 99, "supermarket_id": 1}
        response = await async_client.post("/carts/create", json=payload)

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found."


# Test for missing supermarket
@pytest.mark.asyncio
async def test_create_cart_supermarket_not_found(mock_db_session, async_client):
    mock_user = User(id=1, name="Test User")

    async def mock_execute(stmt):
        if "User" in str(stmt):  # Mock user exists
            return AsyncMock(scalar_one_or_none=lambda: mock_user)
        return AsyncMock(scalar_one_or_none=lambda: None)  # Supermarket not found

    mock_db_session.execute.side_effect = mock_execute

    with patch("server.dependencies.get_db", return_value=mock_db_session):
        payload = {"user_id": 1, "supermarket_id": 99}
        response = await async_client.post("/carts/create", json=payload)

    assert response.status_code == 404
    assert response.json()["detail"] == "Supermarket not found."


@pytest.mark.asyncio
async def test_create_cart_reuse_existing_cart(mock_db_session, async_client):
    mock_user = User(id=1, name="Test User")
    mock_supermarket = Supermarket(id=1, name="Test Supermarket")
    existing_cart = Cart(id=1, user_id=1, supermarket_id=1, status=CartStatus.ACTIVE)

    async def mock_execute(stmt):
        if "User" in str(stmt):
            return AsyncMock(scalar_one_or_none=lambda: mock_user)
        elif "Supermarket" in str(stmt):
            return AsyncMock(scalar_one_or_none=lambda: mock_supermarket)
        elif "Cart" in str(stmt):
            return AsyncMock(scalar_one_or_none=lambda: existing_cart)
        return AsyncMock(scalar_one_or_none=lambda: None)

    mock_db_session.execute.side_effect = mock_execute
    
    with patch("server.dependencies.get_db", return_value=mock_db_session):
        payload = {"user_id": 1, "supermarket_id": 1}
        response = await async_client.post("/carts/create", json=payload)

    assert response.status_code == 200
    assert response.json()["message"] == "Existing cart reused successfully."