"""Create the complete DIP-bot schema.

Revision ID: 20260917_0001
Revises:
Create Date: 2026-09-17

This is intentionally an initial migration: the legacy ``database/init.sql`` plus
incremental migrations have been retired so ``alembic upgrade head`` provisions an
empty database by itself.
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260917_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the schema used by the SQLAlchemy models."""
    op.create_table(
        "bot_permissions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=32), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_bot_permissions")),
        sa.UniqueConstraint("name", name=op.f("uq_bot_permissions_name")),
    )
    op.bulk_insert(
        sa.table("bot_permissions", sa.column("id", sa.Integer()), sa.column("name", sa.String())),
        [{"id": 1, "name": "none"}, {"id": 2, "name": "guild"}, {"id": 3, "name": "private"}],
    )
    op.create_table(
        "guilds",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("reset_generation", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_guilds")),
    )
    op.create_table(
        "channels",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("guild_id", sa.BigInteger(), nullable=False),
        sa.Column("post_amount", sa.SmallInteger(), server_default="1", nullable=False),
        sa.Column("post_frequency", sa.SmallInteger(), server_default="1", nullable=False),
        sa.Column("last_post", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(
            ["guild_id"], ["guilds.id"], name=op.f("fk_channels_guild_id_guilds"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_channels")),
    )
    op.create_index(op.f("ix_channels_guild_id"), "channels", ["guild_id"])
    op.create_table(
        "images",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("byte_size", sa.BigInteger(), nullable=False),
        sa.Column("created", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_images")),
        sa.UniqueConstraint("filename", name=op.f("uq_images_filename")),
    )
    op.create_index(op.f("ix_images_sha256"), "images", ["sha256"])
    op.create_table(
        "sent_images",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("guild_id", sa.BigInteger(), nullable=False),
        sa.Column("image_id", sa.Integer(), nullable=False),
        sa.Column("generation", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(
            ["guild_id"], ["guilds.id"], name=op.f("fk_sent_images_guild_id_guilds"), ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["image_id"], ["images.id"], name=op.f("fk_sent_images_image_id_images"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sent_images")),
        sa.UniqueConstraint("guild_id", "image_id", "generation", name="uq_sent_images_guild_image_gen"),
    )
    op.create_index("ix_sent_images_guild_generation", "sent_images", ["guild_id", "generation"])
    for table_name, unique_name in (
        ("liked_images", "uq_liked_images_image_guild_channel"),
        ("reported_images", "uq_reported_images_image_guild_channel"),
    ):
        op.create_table(
            table_name,
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("image_id", sa.Integer(), nullable=False),
            sa.Column("guild_id", sa.BigInteger(), nullable=False),
            sa.Column("channel_id", sa.BigInteger(), nullable=False),
            sa.Column("counter", sa.Integer(), server_default="0", nullable=False),
            sa.Column("created", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.Column("updated", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.ForeignKeyConstraint(
                ["guild_id"], ["guilds.id"], name=op.f(f"fk_{table_name}_guild_id_guilds"), ondelete="CASCADE"
            ),
            sa.ForeignKeyConstraint(
                ["image_id"], ["images.id"], name=op.f(f"fk_{table_name}_image_id_images"), ondelete="CASCADE"
            ),
            sa.PrimaryKeyConstraint("id", name=op.f(f"pk_{table_name}")),
            sa.UniqueConstraint("image_id", "guild_id", "channel_id", name=unique_name),
        )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("user_name", sa.String(length=255), nullable=False),
        sa.Column("guild_id", sa.BigInteger(), server_default="0", nullable=False),
        sa.Column("permission", sa.Integer(), server_default="1", nullable=False),
        sa.Column("created", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(
            ["permission"], ["bot_permissions.id"], name=op.f("fk_users_permission_bot_permissions")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("user_id", "guild_id", name="uq_users_user_id_guild_id"),
    )
    op.create_index(op.f("ix_users_user_id"), "users", ["user_id"])


def downgrade() -> None:
    """Drop the schema in dependency order."""
    op.drop_index(op.f("ix_users_user_id"), table_name="users")
    op.drop_table("users")
    op.drop_table("reported_images")
    op.drop_table("liked_images")
    op.drop_index("ix_sent_images_guild_generation", table_name="sent_images")
    op.drop_table("sent_images")
    op.drop_index(op.f("ix_images_sha256"), table_name="images")
    op.drop_table("images")
    op.drop_index(op.f("ix_channels_guild_id"), table_name="channels")
    op.drop_table("channels")
    op.drop_table("guilds")
    op.drop_table("bot_permissions")
