"""Add table to store authorized users

Revision ID: 5c13083ca3dc
Revises: ec8fe7b5edff
Create Date: 2024-02-17 19:03:11.623135

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5c13083ca3dc'
down_revision: Union[str, None] = 'ec8fe7b5edff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bp = op.create_table(
        'bot_permissions',
        sa.Column('id', sa.Integer, nullable=False, primary_key=True),
        sa.Column('permission', sa.String(255))
    )
    op.bulk_insert(bp, [
        {
            'id': 1,
            'permission': 'none'
        },
        {
            'id': 2,
            'permission': 'guilds'
        },
        {
            'id': 3,
            'permission': 'private'
        }
    ])
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, autoincrement=True, nullable=False, primary_key=True),
        sa.Column('user_id', sa.BIGINT, nullable=False),
        sa.Column('user_name', sa.String(255), nullable=False),
        sa.Column('guild_id', sa.BIGINT, nullable=True),
        sa.Column('bot_permissions', sa.Integer, sa.ForeignKey('bot_permissions.id'), nullable=False,
                  server_default='1'),
        sa.Column('deleted', sa.Integer, nullable=False, server_default=sa.false()),
        sa.Column('created', sa.DateTime, nullable=False),
        sa.Column('updated', sa.DateTime, nullable=False),
    )


def downgrade() -> None:
    op.drop_table('bot_permissions')
    op.drop_table('users')
