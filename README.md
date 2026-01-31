# SK8 - Digital SKATE Game

> One take. No edits. No excuses.

A mobile app that brings the classic skate game of SKATE into the digital realm. Challenge anyone, anywhere, anytime to a virtual game of SKATE with real-time video verification.

## 🎯 What is SKATE?

The classic skateboarding game where two players take turns setting and matching tricks:
1. Player 1 sets a trick → Player 2 must land it
2. If P2 fails → they get a letter (S-K-A-T-E)
3. If P2 lands it → they set the next trick
4. First to spell "SKATE" loses

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Git

### Backend Setup

```bash
# Clone repo
cd sk8/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your settings

# Run migrations
python -m alembic upgrade head

# Start server
uvicorn app.main:app --reload
API runs at http://localhost:8000
Docs at http://localhost:8000/api/docs
📁 Project Structure
sk8/
├── backend/              # FastAPI backend ✅
│   ├── app/
│   │   ├── api/         # API routes
│   │   ├── core/        # Config, database, security
│   │   ├── models/      # SQLAlchemy models
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # Business logic
│   │   └── main.py      # FastAPI app
│   ├── alembic/         # Database migrations
│   ├── tests/           # Test suite
│   └── sk8.db          # SQLite database
├── frontend/            # React Native app (TODO)
└── docs/                # Documentation
🔌 API Endpoints
Authentication
POST   /api/v1/auth/register      # Create account
POST   /api/v1/auth/login         # Get JWT token
GET    /api/v1/auth/me            # Get current user
Matches
POST   /api/v1/matches/challenge/create       # Create challenge code
POST   /api/v1/matches/challenge/accept/{code} # Accept challenge
GET    /api/v1/matches/active                 # List active matches
GET    /api/v1/matches/history                # Match history
GET    /api/v1/matches/{id}                   # Match details
POST   /api/v1/matches/{id}/forfeit           # Forfeit match
Clips
POST   /api/v1/clips/upload/init              # Get S3 upload URL
POST   /api/v1/clips/upload/complete/{id}     # Mark upload complete
POST   /api/v1/clips/judge                    # Judge opponent's attempt
GET    /api/v1/clips/match/{id}               # Get match clips
Health
GET    /api/v1/health                         # System health check
🎮 Game Flow
Tony creates challenge: POST /matches/challenge/create → gets code wacEthnzc00
Rodney accepts: POST /matches/challenge/accept/wacEthnzc00 → match starts
Tony (goes first) uploads trick video
Rodney attempts to match the trick
Tony judges Rodney's attempt:
✅ Approved → Rodney sets next trick
❌ Rejected → Rodney gets letter "S", Tony sets next trick
Repeat until someone spells S-K-A-T-E and loses
🧪 Testing
# Run all tests
pytest -v

# Run specific test file
pytest tests/test_auth.py -v

# Run with coverage
pytest --cov=app tests/
Current test coverage:
✅ Auth endpoints (register, login, /me)
✅ Health checks
✅ Match creation & acceptance
⏳ Clip upload/judging (needs S3 mock)
🛠️ Development
Database Migrations
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
Code Quality
# Format code
black app/

# Lint
ruff app/

# Type checking
mypy app/
📊 Database Schema
Users
id, username, email, hashed_password
stance (regular/goofy)
wins, losses, current_streak
Profile: display_name, bio, avatar_url
Matches
id, player1_id, player2_id
mode (normal/long), status (pending/active/completed)
Turn tracking: current_turn_user_id
Letter counts: player1_letters, player2_letters
GPS anchor: gps_anchor_lat, gps_anchor_lng
Challenge system: extra_data → {"challenge_code": "..."}
Clips
id, match_id, user_id
clip_type (trick_set/trick_match)
status (pending/approved/rejected)
Video: video_url, duration_seconds, file_size_bytes
GPS: gps_lat, gps_lng, gps_distance_from_anchor_miles
Trick: trick_name, trick_description
⚙️ Configuration
Key environment variables (.env):
# Database
DATABASE_URL=sqlite+aiosqlite:///./sk8.db

# Security
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Storage (S3)
S3_BUCKET_NAME=sk8-clips
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
S3_REGION=us-east-1

# Game Settings
NORMAL_MODE_TIMEOUT_MINUTES=3     # Quick game timeout
LONG_MODE_TIMEOUT_HOURS=6         # Long game timeout
GPS_RADIUS_MILES=1.0              # Quick mode GPS restriction
MAX_CLIP_DURATION_SECONDS=180     # 3 min max clip length
MAX_CLIP_SIZE_MB=50               # Max video file size
🚢 Production Deployment
Switch to PostgreSQL
# Update .env
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/sk8

# Run migrations
alembic upgrade head
Environment Setup
export ENVIRONMENT=production
export DEBUG=False
export SECRET_KEY=$(openssl rand -hex 32)
Run with Gunicorn
pip install gunicorn
gunicorn app.main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
Docker (Optional)
docker-compose up -d
🏗️ Tech Stack
FastAPI - Modern async Python web framework
SQLAlchemy - ORM with async support
Alembic - Database migrations
Pydantic - Data validation
JWT - Token-based authentication
bcrypt - Password hashing
boto3 - S3 integration
pytest - Testing framework
📈 Current Status
✅ Backend: 95% complete for MVP
✅ Database: Fully set up and tested
✅ Auth: Registration, login, JWT working
✅ Game Logic: Turn management, letter tracking, win detection
✅ Tests: 7 passing tests covering core flows
⏳ Frontend: Not started
⏳ Deployment: Local dev only
🎯 Next Steps
S3 Setup - Configure bucket for video uploads
React Native Frontend - Camera, match UI, challenge flow
Video Watermarking - Burn metadata during recording
Push Notifications - Turn reminders
Background Workers - Timeout enforcement
Public Matchmaking - Redis-based queue (optional)
📝 License
MIT License - See LICENSE file
🤙 Contact
Built with 🛹 by skaters, for skaters
Estimated Work to MVP: ~40-50 hours
Backend: ✅ Done
Frontend: ~25-30 hours
Integration & Polish: ~10-15 hours
