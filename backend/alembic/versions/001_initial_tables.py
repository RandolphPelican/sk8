"""Initial tables: users, matches, clips

Revision ID: 001
Revises: 
Create Date: 2026-01-18

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('hashed_password', sa.String(), nullable=False),
    sa.Column('stance', sa.Enum('REGULAR', 'GOOFY', name='stanceenum'), nullable=False),
    sa.Column('wins', sa.Integer(), nullable=False, server_default='0'),
    sa.Column('losses', sa.Integer(), nullable=False, server_default='0'),
    sa.Column('current_streak', sa.Integer(), nullable=False, server_default='0'),
    sa.Column('display_name', sa.String(length=100), nullable=True),
    sa.Column('bio', sa.String(length=500), nullable=True),
    sa.Column('avatar_url', sa.String(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
    sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('last_active', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # Create matches table
    op.create_table('matches',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('player1_id', sa.String(), nullable=False),
    sa.Column('player2_id', sa.String(), nullable=False),
    sa.Column('mode', sa.Enum('NORMAL', 'LONG', name='matchmodeenum'), nullable=False),
    sa.Column('status', sa.Enum('PENDING', 'ACTIVE', 'COMPLETED', 'ABANDONED', 'DISPUTED', name='matchstatusenum'), nullable=False),
    sa.Column('current_turn_user_id', sa.String(), nullable=True),
    sa.Column('player1_letters', sa.Integer(), nullable=False, server_default='0'),
    sa.Column('player2_letters', sa.Integer(), nullable=False, server_default='0'),
    sa.Column('winner_id', sa.String(), nullable=True),
    sa.Column('gps_anchor_lat', sa.Float(), nullable=True),
    sa.Column('gps_anchor_lng', sa.Float(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('last_activity', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('extra_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.ForeignKeyConstraint(['current_turn_user_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['player1_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['player2_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['winner_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_matches_player1_id'), 'matches', ['player1_id'], unique=False)
    op.create_index(op.f('ix_matches_player2_id'), 'matches', ['player2_id'], unique=False)
    op.create_index(op.f('ix_matches_winner_id'), 'matches', ['winner_id'], unique=False)

    # Create clips table
    op.create_table('clips',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('match_id', sa.String(), nullable=False),
    sa.Column('user_id', sa.String(), nullable=False),
    sa.Column('clip_type', sa.Enum('TRICK_SET', 'TRICK_MATCH', name='cliptypeenum'), nullable=False),
    sa.Column('status', sa.Enum('PENDING', 'APPROVED', 'REJECTED', 'DISPUTED', name='clipstatusenum'), nullable=False),
    sa.Column('video_url', sa.String(), nullable=False),
    sa.Column('thumbnail_url', sa.String(), nullable=True),
    sa.Column('duration_seconds', sa.Float(), nullable=False),
    sa.Column('file_size_bytes', sa.Integer(), nullable=False),
    sa.Column('trick_name', sa.String(length=200), nullable=True),
    sa.Column('trick_description', sa.String(length=500), nullable=True),
    sa.Column('gps_lat', sa.Float(), nullable=False),
    sa.Column('gps_lng', sa.Float(), nullable=False),
    sa.Column('gps_distance_from_anchor_miles', sa.Float(), nullable=True),
    sa.Column('gps_verified', sa.Boolean(), nullable=True, server_default='false'),
    sa.Column('watermark_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('judged_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('extra_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.ForeignKeyConstraint(['match_id'], ['matches.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_clips_match_id'), 'clips', ['match_id'], unique=False)
    op.create_index(op.f('ix_clips_user_id'), 'clips', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_clips_user_id'), table_name='clips')
    op.drop_index(op.f('ix_clips_match_id'), table_name='clips')
    op.drop_table('clips')
    op.drop_index(op.f('ix_matches_winner_id'), table_name='matches')
    op.drop_index(op.f('ix_matches_player2_id'), table_name='matches')
    op.drop_index(op.f('ix_matches_player1_id'), table_name='matches')
    op.drop_table('matches')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.execute('DROP TYPE IF EXISTS clipstatusenum')
    op.execute('DROP TYPE IF EXISTS cliptypeenum')
    op.execute('DROP TYPE IF EXISTS matchstatusenum')
    op.execute('DROP TYPE IF EXISTS matchmodeenum')
    op.execute('DROP TYPE IF EXISTS stanceenum')
