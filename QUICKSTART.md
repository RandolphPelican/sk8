# SK8 Backend - Quick Reference

## Start Development

```bash
cd sk8/backend
source venv/bin/activate
uvicorn app.main:app --reload
Server: http://localhost:8000
Docs: http://localhost:8000/api/docs
Test the API
# Health check
curl http://localhost:8000/api/v1/health

# Register user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"skater","email":"skater@sk8.com","password":"test123","stance":"regular"}'

# Run tests
pytest -v
Common Tasks
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1

# Run specific test
pytest tests/test_auth.py -v

# Format code
black app/
Project Structure
app/
├── api/v1/          # Endpoints
├── core/            # Config, DB, security
├── models/          # Database models
├── schemas/         # Validation
└── services/        # Business logic
Key Files
app/main.py - FastAPI app
app/core/config.py - Settings
app/services/game_service.py - Game logic
.env - Configuration
sk8.db - SQLite database
Status: ✅ COMPLETE
Ready for frontend development!
