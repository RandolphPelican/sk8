from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.clip import ClipTypeEnum, ClipStatusEnum


class ClipUploadRequest(BaseModel):
    """Schema for initiating clip upload"""
    match_id: str
    clip_type: ClipTypeEnum
    gps_lat: float = Field(..., ge=-90, le=90)
    gps_lng: float = Field(..., ge=-180, le=180)
    duration_seconds: float = Field(..., gt=0, le=180)
    file_size_bytes: int = Field(..., gt=0)
    trick_name: Optional[str] = Field(None, max_length=200)
    trick_description: Optional[str] = Field(None, max_length=500)


class ClipUploadResponse(BaseModel):
    """Schema for upload URL response"""
    clip_id: str
    upload_url: str
    expires_in: int


class ClipResponse(BaseModel):
    """Schema for clip data response"""
    id: str
    match_id: str
    user_id: str
    clip_type: ClipTypeEnum
    status: ClipStatusEnum
    video_url: str
    thumbnail_url: Optional[str] = None
    duration_seconds: float
    file_size_bytes: int
    trick_name: Optional[str] = None
    trick_description: Optional[str] = None
    gps_lat: float
    gps_lng: float
    gps_distance_from_anchor_miles: Optional[float] = None
    gps_verified: bool
    recorded_at: datetime
    uploaded_at: datetime
    judged_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ClipJudgement(BaseModel):
    """Schema for judging a clip"""
    clip_id: str
    approved: bool
    reason: Optional[str] = Field(None, max_length=500)


class ClipListResponse(BaseModel):
    """Schema for list of clips"""
    clips: list[ClipResponse]
    total: int
