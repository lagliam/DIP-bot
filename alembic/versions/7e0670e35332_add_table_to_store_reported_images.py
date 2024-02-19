"""Add table to store reported images

Revision ID: 7e0670e35332
Revises: 5c13083ca3dc
Create Date: 2024-02-18 23:56:49.529855

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7e0670e35332'
down_revision: Union[str, None] = '5c13083ca3dc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'reported_images',
        sa.Column('id', sa.Integer, autoincrement=True, nullable=False, primary_key=True),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('guild_id', sa.BIGINT, nullable=True),
        sa.Column('channel_id', sa.BIGINT, nullable=False),
        sa.Column('counter', sa.Integer, server_default='1'),
        sa.Column('created', sa.DateTime, nullable=False),
        sa.Column('updated', sa.DateTime, nullable=False),
    )


def downgrade() -> None:
    op.drop_table('reported_images')
