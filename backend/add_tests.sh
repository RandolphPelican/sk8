#!/bin/bash

echo "Setting up tests..."

# Create test config
cat > tests/__init__.py << 'EOF'
EOF

cat > tests/conftest.py << 'EOF'
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.core.database import Base, get_db
from app.models import user, match, clip

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=NullPool,
)

TestSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def override_get_db():
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
async def client():
    """Create test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="function")
async def db_session():
    """Create test database session"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
EOF

echo "✅ Created test fixtures"

# Create auth tests
cat > tests/test_auth.py << 'EOF'
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
EOF

echo "✅ Created auth tests"

# Create health tests
cat > tests/test_health.py << 'EOF'
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health endpoint"""
    response = await client.get("/api/v1/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "checks" in data
    assert data["checks"]["database"] == "ok"


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Test root endpoint"""
    response = await client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "SK8"
    assert "version" in data
EOF

echo "✅ Created health tests"

# Add pytest-asyncio to requirements if not present
if ! grep -q "pytest-asyncio" requirements.txt; then
    echo "pytest==7.4.4" >> requirements.txt
    echo "pytest-asyncio==0.23.3" >> requirements.txt
    echo "httpx==0.26.0" >> requirements.txt
    echo "✅ Added test dependencies to requirements.txt"
fi

echo ""
echo "🎉 Tests created!"
echo ""
echo "Run tests with:"
echo "  pytest -v"
echo ""
echo "Or run specific test file:"
echo "  pytest tests/test_auth.py -v"
