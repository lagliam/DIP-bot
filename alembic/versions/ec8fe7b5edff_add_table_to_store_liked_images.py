"""Add table to store liked images

Revision ID: ec8fe7b5edff
Revises: 3044b9ae9b0b
Create Date: 2024-02-13 00:15:03.043512

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ec8fe7b5edff'
down_revision: Union[str, None] = '3044b9ae9b0b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'liked_images',
        sa.Column('id', sa.Integer, autoincrement=True, nullable=False, primary_key=True),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('guild_id', sa.BIGINT, nullable=False),
        sa.Column('channel_id', sa.BIGINT, nullable=False),
        sa.Column('counter', sa.Integer, nullable=False, server_default='1'),
        sa.Column('updated', sa.DateTime, nullable=False),
    )


def downgrade():
    op.drop_table('liked_images')
