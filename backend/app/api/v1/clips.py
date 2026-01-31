from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
import uuid

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.match import Match
from app.models.clip import Clip, ClipTypeEnum
from app.schemas.clip import (
    ClipUploadRequest,
    ClipUploadResponse,
    ClipResponse,
    ClipJudgement,
    ClipListResponse
)
from app.schemas.match import MatchResponse
from app.services.game_service import GameService
from app.services.storage_service import StorageService

router = APIRouter()


@router.post("/upload/init", response_model=ClipUploadResponse)
async def init_clip_upload(
    upload_request: ClipUploadRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Initialize clip upload - returns presigned S3 URL
    Frontend uploads video directly to S3, then calls /upload/complete
    """
    # Get match
    match = await db.get(Match, upload_request.match_id)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    
    # Validate user is in match and it's their turn
    await GameService.validate_turn(match, current_user.id)
    
    # Create clip record
    clip = Clip(
        match_id=match.id,
        user_id=current_user.id,
        clip_type=upload_request.clip_type,
        gps_lat=upload_request.gps_lat,
        gps_lng=upload_request.gps_lng,
        duration_seconds=upload_request.duration_seconds,
        file_size_bytes=upload_request.file_size_bytes,
        trick_name=upload_request.trick_name,
        trick_description=upload_request.trick_description,
        recorded_at=datetime.utcnow(),
        video_url="",
    )
    
    db.add(clip)
    await db.commit()
    await db.refresh(clip)
    
    # Generate presigned upload URL
    upload_url = await StorageService.generate_upload_url(
        clip_id=clip.id,
        file_size=upload_request.file_size_bytes
    )
    
    return ClipUploadResponse(
        clip_id=clip.id,
        upload_url=upload_url,
        expires_in=300
    )


@router.post("/upload/complete/{clip_id}", response_model=ClipResponse)
async def complete_clip_upload(
    clip_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark clip upload as complete and process based on type"""
    clip = await db.get(Clip, clip_id)
    
    if not clip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clip not found"
        )
    
    if clip.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not your clip"
        )
    
    # Update video URL
    clip.video_url = await StorageService.get_clip_url(clip.id)
    
    # Get match
    match = await db.get(Match, clip.match_id)
    
    # Process based on clip type
    if clip.clip_type == ClipTypeEnum.TRICK_SET:
        await GameService.submit_trick_set(db, match, current_user.id, clip)
    else:
        await GameService.submit_trick_attempt(db, match, current_user.id, clip)
    
    await db.commit()
    await db.refresh(clip)
    
    return clip


@router.post("/judge", response_model=MatchResponse)
async def judge_clip(
    judgement: ClipJudgement,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Judge opponent's trick attempt"""
    clip = await db.get(Clip, judgement.clip_id)
    
    if not clip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clip not found"
        )
    
    match = await db.get(Match, clip.match_id)
    
    match = await GameService.judge_clip(
        db=db,
        match=match,
        clip=clip,
        judge_user_id=current_user.id,
        approved=judgement.approved
    )
    
    return match


@router.get("/match/{match_id}", response_model=ClipListResponse)
async def get_match_clips(
    match_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all clips for a match"""
    match = await db.get(Match, match_id)
    
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    
    if current_user.id not in [match.player1_id, match.player2_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a player in this match"
        )
    
    result = await db.execute(
        select(Clip).where(Clip.match_id == match_id)
        .order_by(Clip.uploaded_at.asc())
    )
    clips = result.scalars().all()
    
    return ClipListResponse(
        clips=clips,
        total=len(clips)
    )
