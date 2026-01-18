from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum
import uuid


class ClipTypeEnum(str, enum.Enum):
    TRICK_SET = "trick_set"
    TRICK_MATCH = "trick_match"


class ClipStatusEnum(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DISPUTED = "disputed"


class Clip(Base):
    __tablename__ = "clips"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Relationships
    match_id = Column(String, ForeignKey("matches.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Clip Info
    clip_type = Column(Enum(ClipTypeEnum), nullable=False)
    status = Column(Enum(ClipStatusEnum), nullable=False, default=ClipStatusEnum.PENDING)
    
    # Video Storage
    video_url = Column(String, nullable=False)
    thumbnail_url = Column(String)
    duration_seconds = Column(Float, nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    
    # Trick Description
    trick_name = Column(String(200))
    trick_description = Column(String(500))
    
    # GPS Verification
    gps_lat = Column(Float, nullable=False)
    gps_lng = Column(Float, nullable=False)
    gps_distance_from_anchor_miles = Column(Float)
    gps_verified = Column(Boolean, default=False)
    
    # Watermark Data
    watermark_data = Column(JSON)
    
    # Timestamps
    recorded_at = Column(DateTime(timezone=True), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    judged_at = Column(DateTime(timezone=True))
    
    # Extra data (renamed from 'metadata' to avoid SQLAlchemy conflict)
    extra_data = Column(JSON)
    
    # Relationships
    match = relationship("Match", back_populates="clips")
    user = relationship("User", back_populates="clips")

    def __repr__(self):
        return f"<Clip {self.id[:8]} - {self.trick_name} - {self.status.value}>"
