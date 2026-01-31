import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Test user registration"""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "test_user",
            "email": "test@example.com",
            "password": "testpass123",
            "stance": "regular"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_duplicate_username(client: AsyncClient):
    """Test registering with duplicate username"""
    user_data = {
        "username": "duplicate",
        "email": "test1@example.com",
        "password": "testpass123",
        "stance": "regular"
    }
    
    # Register first time
    await client.post("/api/v1/auth/register", json=user_data)
    
    # Try to register again with same username
    user_data["email"] = "test2@example.com"
    response = await client.post("/api/v1/auth/register", json=user_data)
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    """Test user login"""
    # Register user
    await client.post(
        "/api/v1/auth/register",
        json={
            "username": "login_test",
            "email": "login@example.com",
            "password": "testpass123",
            "stance": "goofy"
        }
    )
    
    # Login
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "username": "login_test",
            "password": "testpass123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Test login with wrong password"""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "username": "nonexistent",
            "password": "wrongpass"
        }
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient):
    """Test getting current user info"""
    # Register and get token
    reg_response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "me_test",
            "email": "me@example.com",
            "password": "testpass123",
            "stance": "regular"
        }
    )
    token = reg_response.json()["access_token"]
    
    # Get current user
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "me_test"
    assert data["stance"] == "regular"
    assert data["wins"] == 0
    assert data["losses"] == 0
