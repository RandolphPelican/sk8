# SK8 API Endpoints

## Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current user

## Matches
- `POST /api/v1/matches/challenge/create` - Create challenge invite code
- `POST /api/v1/matches/challenge/accept/{challenge_code}` - Accept challenge
- `GET /api/v1/matches/active` - Get your active matches
- `GET /api/v1/matches/history` - Get match history
- `GET /api/v1/matches/{match_id}` - Get match details
- `POST /api/v1/matches/{match_id}/forfeit` - Forfeit match

## Clips
- `POST /api/v1/clips/upload/init` - Get S3 upload URL
- `POST /api/v1/clips/upload/complete/{clip_id}` - Mark upload complete
- `POST /api/v1/clips/judge` - Judge opponent's attempt
- `GET /api/v1/clips/match/{match_id}` - Get all clips for match

## Game Flow

### Setting a Trick
1. P1 calls `/clips/upload/init` with `clip_type: "trick_set"`
2. Frontend uploads video to S3 URL
3. P1 calls `/clips/upload/complete/{clip_id}`
4. Backend auto-approves and switches turn to P2

### Attempting a Trick
1. P2 calls `/clips/upload/init` with `clip_type: "trick_match"`
2. Frontend uploads video to S3 URL
3. P2 calls `/clips/upload/complete/{clip_id}`
4. Clip marked as PENDING, waiting for P1 to judge

### Judging
1. P1 calls `/clips/judge` with `approved: true/false`
2. If approved: P2 gets to set next trick
3. If rejected: P2 gets a letter, P1 sets next trick
4. If someone reaches 5 letters: Match ends, winner declared

## What's Built
✅ Full auth system with JWT
✅ Match challenge system (invite codes)
✅ Turn-based game logic
✅ Letter tracking (S-K-A-T-E)
✅ GPS validation (1 mile radius for quick mode)
✅ S3 video upload flow
✅ Win/loss stat tracking

## What's NOT Built Yet
❌ Public matchmaking queue (only direct challenges work)
❌ Redis integration for real-time matchmaking
❌ WebSocket for live match updates
❌ Push notifications
❌ Frontend (literally nothing lol)
❌ Video watermarking (that's frontend's job)
❌ Timeout enforcement (service exists but no background worker)

## Next Steps
1. Test the endpoints with Postman/curl
2. Set up database migrations (alembic)
3. Build frontend with React Native
4. Add WebSocket for real-time updates
5. Set up S3 bucket
6. Deploy backend
