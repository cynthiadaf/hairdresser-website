"""Remove database-backed settings, prices, and staff authentication."""

from alembic import op

revision = "0002_remove_obsolete_studio_data"
down_revision = "0001_initial"


def upgrade():
    op.drop_table("sessions")
    op.drop_table("site_settings")
    op.drop_table("pricelist_items")
    op.drop_table("pricelist_categories")
    op.drop_table("admin_users")


def downgrade():
    raise NotImplementedError("The removed studio data is not recoverable")
