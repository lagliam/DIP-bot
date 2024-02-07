"""add delete column to guilds table

Revision ID: d4f9747da532
Revises: 
Create Date: 2024-02-05 19:25:01.213234

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4f9747da532'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('guilds', sa.Column('deleted', sa.Boolean(), server_default=sa.false()))


def downgrade() -> None:
    op.drop_column('guilds', 'deleted')
