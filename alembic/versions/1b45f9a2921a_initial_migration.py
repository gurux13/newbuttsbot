"""Initial migration

Revision ID: 1b45f9a2921a
Revises: 
Create Date: 2025-02-17 00:00:00.639137

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1b45f9a2921a'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('chat_subscriptions',
    sa.Column('broadcaster_id', sa.String(), nullable=False),
    sa.Column('is_subscribed', sa.Boolean(), nullable=False),
    sa.Column('butt_word', sa.String(), nullable=True),
    sa.Column('frequency', sa.Integer(), nullable=False),
    sa.Column('rate', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('last_modified_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.PrimaryKeyConstraint('broadcaster_id')
    )
    op.create_table('chatters',
    sa.Column('twitch_id', sa.String(), nullable=False),
    sa.Column('ignore', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('last_modified_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.PrimaryKeyConstraint('twitch_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('chatters')
    op.drop_table('chat_subscriptions')
    # ### end Alembic commands ###
