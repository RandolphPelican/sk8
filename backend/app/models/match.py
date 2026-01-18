from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum
import uuid


class MatchModeEnum(str, enum.Enum):
    NORMAL = "normal"
    LONG = "long"


class MatchStatusEnum(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    DISPUTED = "disputed"


class Match(Base):
    __tablename__ = "matches"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Players
    player1_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    player2_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Match Config
    mode = Column(Enum(MatchModeEnum), nullable=False, default=MatchModeEnum.NORMAL)
    status = Column(Enum(MatchStatusEnum), nullable=False, default=MatchStatusEnum.PENDING)
    
    # Game State
    current_turn_user_id = Column(String, ForeignKey("users.id"))
    player1_letters = Column(Integer, default=0, nullable=False)
    player2_letters = Column(Integer, default=0, nullable=False)
    
    # Winner
    winner_id = Column(String, ForeignKey("users.id"), index=True)
    
    # GPS Anchor
    gps_anchor_lat = Column(Float)
    gps_anchor_lng = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Extra data (renamed from 'metadata' to avoid SQLAlchemy conflict)
    extra_data = Column(JSON)
    
    # Relationships
    player1 = relationship("User", foreign_keys=[player1_id], back_populates="matches_as_p1")
    player2 = relationship("User", foreign_keys=[player2_id], back_populates="matches_as_p2")
    current_turn_user = relationship("User", foreign_keys=[current_turn_user_id])
    winner = relationship("User", foreign_keys=[winner_id])
    clips = relationship("Clip", back_populates="match", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Match {self.id[:8]} - {self.mode.value} - {self.status.value}>"
