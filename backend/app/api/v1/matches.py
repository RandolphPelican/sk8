from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, func
from typing import List
import secrets
from datetime import datetime

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.match import Match, MatchStatusEnum
from app.schemas.match import (
    MatchCreate,
    MatchResponse,
    MatchListResponse
)
from app.services.game_service import GameService

router = APIRouter()


@router.post("/challenge/create", response_model=dict)
async def create_challenge(
    match_data: MatchCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a challenge invite code that another player can accept
    Returns a challenge code that can be shared via QR/link
    """
    # Generate unique challenge code
    challenge_code = secrets.token_urlsafe(8)
    
    # Store challenge in match with pending status
    match = Match(
        player1_id=current_user.id,
        player2_id=None,  # Will be filled when someone accepts
        mode=match_data.mode,
        status=MatchStatusEnum.PENDING,
        gps_anchor_lat=match_data.gps_lat,
        gps_anchor_lng=match_data.gps_lng,
        extra_data={"challenge_code": challenge_code}
    )
    
    db.add(match)
    await db.commit()
    await db.refresh(match)
    
    return {
        "match_id": match.id,
        "challenge_code": challenge_code,
        "share_url": f"sk8://challenge/{challenge_code}",
        "mode": match.mode.value
    }


@router.post("/challenge/accept/{challenge_code}", response_model=MatchResponse)
async def accept_challenge(
    challenge_code: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Accept a challenge using the challenge code
    Activates the match and returns full match details
    """
    # Find pending matches
    result = await db.execute(
        select(Match).where(Match.status == MatchStatusEnum.PENDING)
    )
    matches = result.scalars().all()
    
    # Find the one with matching challenge code
    match = None
    for m in matches:
        if m.extra_data and m.extra_data.get('challenge_code') == challenge_code:
            match = m
            break
    
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found or already accepted"
        )
    
    if match.player1_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot accept your own challenge"
        )
    
    # Accept the challenge
    match.player2_id = current_user.id
    match.status = MatchStatusEnum.ACTIVE
    match.current_turn_user_id = match.player1_id  # P1 sets first trick
    match.started_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(match)
    
    return match


@router.get("/active", response_model=MatchListResponse)
async def get_active_matches(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all active matches for current user"""
    result = await db.execute(
        select(Match).where(
            and_(
                or_(
                    Match.player1_id == current_user.id,
                    Match.player2_id == current_user.id
                ),
                Match.status == MatchStatusEnum.ACTIVE
            )
        ).order_by(Match.last_activity.desc())
    )
    matches = result.scalars().all()
    
    return MatchListResponse(
        matches=matches,
        total=len(matches)
    )


@router.get("/history", response_model=MatchListResponse)
async def get_match_history(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get match history for current user"""
    result = await db.execute(
        select(Match).where(
            and_(
                or_(
                    Match.player1_id == current_user.id,
                    Match.player2_id == current_user.id
                ),
                Match.status == MatchStatusEnum.COMPLETED
            )
        ).order_by(Match.completed_at.desc())
        .limit(limit)
        .offset(offset)
    )
    matches = result.scalars().all()
    
    # Get total count
    count_result = await db.execute(
        select(Match).where(
            and_(
                or_(
                    Match.player1_id == current_user.id,
                    Match.player2_id == current_user.id
                ),
                Match.status == MatchStatusEnum.COMPLETED
            )
        )
    )
    total = len(count_result.scalars().all())
    
    return MatchListResponse(
        matches=matches,
        total=total
    )


@router.get("/{match_id}", response_model=MatchResponse)
async def get_match(
    match_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific match details"""
    match = await db.get(Match, match_id)
    
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    
    # Verify user is part of this match
    if current_user.id not in [match.player1_id, match.player2_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a player in this match"
        )
    
    # Check for timeout
    await GameService.validate_timeout(match, db)
    
    return match


@router.post("/{match_id}/forfeit", response_model=MatchResponse)
async def forfeit_match(
    match_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Forfeit an active match"""
    match = await db.get(Match, match_id)
    
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    
    match = await GameService.forfeit_match(db, match, current_user.id)
    
    return match
