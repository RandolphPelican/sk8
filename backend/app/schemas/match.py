from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.match import MatchModeEnum, MatchStatusEnum


class MatchCreate(BaseModel):
    """Schema for creating a new match"""
    mode: MatchModeEnum = MatchModeEnum.NORMAL
    gps_lat: float = Field(..., ge=-90, le=90)
    gps_lng: float = Field(..., ge=-180, le=180)


class MatchJoin(BaseModel):
    """Schema for joining matchmaking queue"""
    mode: MatchModeEnum = MatchModeEnum.NORMAL
    gps_lat: float = Field(..., ge=-90, le=90)
    gps_lng: float = Field(..., ge=-180, le=180)


class MatchResponse(BaseModel):
    """Schema for match data response"""
    id: str
    player1_id: str
    player2_id: str
    mode: MatchModeEnum
    status: MatchStatusEnum
    current_turn_user_id: Optional[str] = None
    player1_letters: int
    player2_letters: int
    winner_id: Optional[str] = None
    gps_anchor_lat: Optional[float] = None
    gps_anchor_lng: Optional[float] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    last_activity: datetime

    class Config:
        from_attributes = True


class MatchUpdate(BaseModel):
    """Schema for updating match state"""
    status: Optional[MatchStatusEnum] = None
    current_turn_user_id: Optional[str] = None
    player1_letters: Optional[int] = None
    player2_letters: Optional[int] = None
    winner_id: Optional[str] = None


class MatchListResponse(BaseModel):
    """Schema for list of matches"""
    matches: list[MatchResponse]
    total: int
