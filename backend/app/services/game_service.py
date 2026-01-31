from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from typing import Optional, Tuple
import math

from app.models.match import Match, MatchStatusEnum, MatchModeEnum
from app.models.clip import Clip, ClipTypeEnum, ClipStatusEnum
from app.models.user import User
from app.core.config import settings


class GameService:
    """Core game logic for SKATE matches"""
    
    LETTERS = ["S", "K", "A", "T", "E"]
    MAX_LETTERS = 5  # Spell SKATE = you lose
    
    @staticmethod
    def calculate_gps_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two GPS coordinates in miles using Haversine formula"""
        R = 3959  # Earth's radius in miles
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    @staticmethod
    async def create_match(
        db: AsyncSession,
        player1_id: str,
        player2_id: str,
        mode: MatchModeEnum,
        gps_lat: float,
        gps_lng: float
    ) -> Match:
        """Create a new match between two players"""
        
        if player1_id == player2_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot create match with yourself"
            )
        
        # Create match with P1 starting first
        match = Match(
            player1_id=player1_id,
            player2_id=player2_id,
            mode=mode,
            status=MatchStatusEnum.ACTIVE,
            current_turn_user_id=player1_id,  # P1 sets first trick
            gps_anchor_lat=gps_lat,
            gps_anchor_lng=gps_lng,
            started_at=datetime.utcnow()
        )
        
        db.add(match)
        await db.commit()
        await db.refresh(match)
        
        return match
    
    @staticmethod
    async def validate_turn(match: Match, user_id: str) -> None:
        """Validate it's this user's turn"""
        if match.status != MatchStatusEnum.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Match is {match.status.value}, cannot submit clips"
            )
        
        if match.current_turn_user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not your turn"
            )
    
    @staticmethod
    async def validate_gps(match: Match, clip_lat: float, clip_lng: float) -> Tuple[bool, float]:
        """
        Validate GPS coordinates against match anchor
        Returns (is_valid, distance_in_miles)
        """
        distance = GameService.calculate_gps_distance(
            match.gps_anchor_lat,
            match.gps_anchor_lng,
            clip_lat,
            clip_lng
        )
        
        # Quick mode enforces 1 mile radius, long mode is lenient
        if match.mode == MatchModeEnum.NORMAL:
            is_valid = distance <= settings.GPS_RADIUS_MILES
        else:
            is_valid = True  # Long mode has no GPS restriction
        
        return is_valid, distance
    
    @staticmethod
    async def validate_timeout(match: Match, db: AsyncSession) -> None:
        """Check if current player exceeded turn timeout"""
        if match.status != MatchStatusEnum.ACTIVE:
            return
        
        if not match.last_activity:
            return
        
        # Calculate timeout based on mode
        if match.mode == MatchModeEnum.NORMAL:
            timeout_delta = timedelta(minutes=settings.NORMAL_MODE_TIMEOUT_MINUTES)
        else:
            timeout_delta = timedelta(hours=settings.LONG_MODE_TIMEOUT_HOURS)
        
        if datetime.utcnow() > match.last_activity + timeout_delta:
            # Current player timed out - they auto-forfeit
            await GameService.forfeit_match(db, match, match.current_turn_user_id)
    
    @staticmethod
    async def submit_trick_set(
        db: AsyncSession,
        match: Match,
        user_id: str,
        clip: Clip
    ) -> Match:
        """
        Player sets a trick (starts their turn)
        This means they're challenging opponent to match it
        """
        await GameService.validate_turn(match, user_id)
        
        # Validate GPS
        gps_valid, distance = await GameService.validate_gps(match, clip.gps_lat, clip.gps_lng)
        clip.gps_distance_from_anchor_miles = distance
        clip.gps_verified = gps_valid
        
        if not gps_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"GPS too far from anchor: {distance:.2f} miles (max: {settings.GPS_RADIUS_MILES})"
            )
        
        # Auto-approve their set clip
        clip.status = ClipStatusEnum.APPROVED
        clip.judged_at = datetime.utcnow()
        
        # Switch turn to opponent
        opponent_id = match.player2_id if user_id == match.player1_id else match.player1_id
        match.current_turn_user_id = opponent_id
        match.last_activity = datetime.utcnow()
        
        await db.commit()
        await db.refresh(match)
        
        return match
    
    @staticmethod
    async def submit_trick_attempt(
        db: AsyncSession,
        match: Match,
        user_id: str,
        clip: Clip
    ) -> Match:
        """
        Player attempts to match opponent's trick
        Clip gets marked as pending - opponent must judge it
        """
        await GameService.validate_turn(match, user_id)
        
        # Validate GPS
        gps_valid, distance = await GameService.validate_gps(match, clip.gps_lat, clip.gps_lng)
        clip.gps_distance_from_anchor_miles = distance
        clip.gps_verified = gps_valid
        
        if not gps_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"GPS too far from anchor: {distance:.2f} miles (max: {settings.GPS_RADIUS_MILES})"
            )
        
        # Leave as pending - opponent needs to judge
        clip.status = ClipStatusEnum.PENDING
        match.last_activity = datetime.utcnow()
        
        await db.commit()
        await db.refresh(match)
        
        return match
    
    @staticmethod
    async def judge_clip(
        db: AsyncSession,
        match: Match,
        clip: Clip,
        judge_user_id: str,
        approved: bool
    ) -> Match:
        """
        Judge opponent's trick attempt
        If rejected → they get a letter
        If approved → they get to set next trick
        """
        # Validate judge is in this match and is NOT the clip owner
        if judge_user_id not in [match.player1_id, match.player2_id]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not a player in this match"
            )
        
        if judge_user_id == clip.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot judge your own clip"
            )
        
        if clip.status != ClipStatusEnum.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Clip already judged: {clip.status.value}"
            )
        
        # Mark clip as approved or rejected
        clip.status = ClipStatusEnum.APPROVED if approved else ClipStatusEnum.REJECTED
        clip.judged_at = datetime.utcnow()
        
        if approved:
            # They landed it! Now it's their turn to set a trick
            match.current_turn_user_id = clip.user_id
        else:
            # They failed - give them a letter
            if clip.user_id == match.player1_id:
                match.player1_letters += 1
            else:
                match.player2_letters += 1
            
            # Judge (opponent) gets to set next trick
            match.current_turn_user_id = judge_user_id
        
        match.last_activity = datetime.utcnow()
        
        # Check for winner
        if match.player1_letters >= GameService.MAX_LETTERS:
            match.status = MatchStatusEnum.COMPLETED
            match.winner_id = match.player2_id
            match.completed_at = datetime.utcnow()
            await GameService.update_player_stats(db, match)
        elif match.player2_letters >= GameService.MAX_LETTERS:
            match.status = MatchStatusEnum.COMPLETED
            match.winner_id = match.player1_id
            match.completed_at = datetime.utcnow()
            await GameService.update_player_stats(db, match)
        
        await db.commit()
        await db.refresh(match)
        
        return match
    
    @staticmethod
    async def forfeit_match(
        db: AsyncSession,
        match: Match,
        forfeiting_user_id: str
    ) -> Match:
        """Forfeit a match (timeout or manual forfeit)"""
        if match.status != MatchStatusEnum.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Match already {match.status.value}"
            )
        
        if forfeiting_user_id not in [match.player1_id, match.player2_id]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not a player in this match"
            )
        
        # Opponent wins
        match.status = MatchStatusEnum.COMPLETED
        match.winner_id = match.player2_id if forfeiting_user_id == match.player1_id else match.player1_id
        match.completed_at = datetime.utcnow()
        
        await GameService.update_player_stats(db, match)
        await db.commit()
        await db.refresh(match)
        
        return match
    
    @staticmethod
    async def update_player_stats(db: AsyncSession, match: Match) -> None:
        """Update win/loss records and streaks after match completion"""
        if not match.winner_id:
            return
        
        winner = await db.get(User, match.winner_id)
        loser_id = match.player1_id if match.winner_id == match.player2_id else match.player2_id
        loser = await db.get(User, loser_id)
        
        if winner:
            winner.wins += 1
            winner.current_streak += 1
        
        if loser:
            loser.losses += 1
            loser.current_streak = 0
        
        await db.commit()
