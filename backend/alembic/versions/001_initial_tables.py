"""initial tables

Revision ID: 001
Revises: 
Create Date: 2025-01-27

"""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Users table
    op.create_table('users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('stance', sa.String(7), nullable=False),
        sa.Column('wins', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('losses', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('current_streak', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('display_name', sa.String(100), nullable=True),
        sa.Column('bio', sa.String(500), nullable=True),
        sa.Column('avatar_url', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('last_active', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # Matches table - NOTE: player2_id is NULLABLE for challenges
    op.create_table('matches',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('player1_id', sa.String(), nullable=False),
        sa.Column('player2_id', sa.String(), nullable=True),  # NULLABLE!
        sa.Column('mode', sa.String(6), nullable=False),
        sa.Column('status', sa.String(9), nullable=False),
        sa.Column('current_turn_user_id', sa.String(), nullable=True),
        sa.Column('player1_letters', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('player2_letters', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('winner_id', sa.String(), nullable=True),
        sa.Column('gps_anchor_lat', sa.Float(), nullable=True),
        sa.Column('gps_anchor_lng', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('last_activity', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('extra_data', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['player1_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['player2_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['current_turn_user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['winner_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_matches_player1_id', 'matches', ['player1_id'])
    op.create_index('ix_matches_player2_id', 'matches', ['player2_id'])
    op.create_index('ix_matches_winner_id', 'matches', ['winner_id'])

    # Clips table
    op.create_table('clips',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('match_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('clip_type', sa.String(11), nullable=False),
        sa.Column('status', sa.String(8), nullable=False),
        sa.Column('video_url', sa.String(), nullable=False),
        sa.Column('thumbnail_url', sa.String(), nullable=True),
        sa.Column('duration_seconds', sa.Float(), nullable=False),
        sa.Column('file_size_bytes', sa.Integer(), nullable=False),
        sa.Column('trick_name', sa.String(200), nullable=True),
        sa.Column('trick_description', sa.String(500), nullable=True),
        sa.Column('gps_lat', sa.Float(), nullable=False),
        sa.Column('gps_lng', sa.Float(), nullable=False),
        sa.Column('gps_distance_from_anchor_miles', sa.Float(), nullable=True),
        sa.Column('gps_verified', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('watermark_data', sa.JSON(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('judged_at', sa.DateTime(), nullable=True),
        sa.Column('extra_data', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_clips_match_id', 'clips', ['match_id'])
    op.create_index('ix_clips_user_id', 'clips', ['user_id'])


def downgrade():
    op.drop_table('clips')
    op.drop_table('matches')
    op.drop_table('users')
