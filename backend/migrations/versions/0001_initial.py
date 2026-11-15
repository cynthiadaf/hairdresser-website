"""Create core studio tables."""

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None


def upgrade():
    op.create_table(
        "admin_users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("phone_number", sa.String(32), unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column(
            "must_change_password", sa.Boolean, nullable=False, server_default=sa.true()
        ),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_table(
        "pricelist_categories",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("sort_order", sa.Integer, nullable=False),
        sa.Column("is_published", sa.Boolean, nullable=False),
    )
    op.create_table(
        "pricelist_items",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "category_id",
            sa.Integer,
            sa.ForeignKey("pricelist_categories.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("duration_minutes", sa.Integer),
        sa.Column("price_minor", sa.Integer, nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("sort_order", sa.Integer, nullable=False),
        sa.Column("is_published", sa.Boolean, nullable=False),
    )
    op.create_table(
        "site_settings",
        sa.Column("key", sa.String(80), primary_key=True),
        sa.Column("value", sa.Text, nullable=False),
    )
    op.create_table(
        "gallery_items",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("instagram_media_id", sa.String(160), unique=True),
        sa.Column("media_type", sa.String(20), nullable=False),
        sa.Column("media_path", sa.String(500), nullable=False),
        sa.Column("thumbnail_path", sa.String(500)),
        sa.Column("width", sa.Integer),
        sa.Column("height", sa.Integer),
        sa.Column("is_visible", sa.Boolean, nullable=False),
    )
    op.create_table(
        "scrape_runs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("items_seen", sa.Integer, nullable=False),
        sa.Column("error_summary", sa.Text),
        sa.Column("started_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_table(
        "sessions",
        sa.Column("token_hash", sa.String(128), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("admin_users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime, nullable=False),
    )


def downgrade():
    for table in (
        "sessions",
        "scrape_runs",
        "gallery_items",
        "site_settings",
        "pricelist_items",
        "pricelist_categories",
        "admin_users",
    ):
        op.drop_table(table)
