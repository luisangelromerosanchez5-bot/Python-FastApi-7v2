"""Agrega ciudad a usuarios

Revision ID: 20260602_0001
Revises:
Create Date: 2026-06-02
"""

from alembic import op
import sqlalchemy as sa


revision = "20260602_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("usuarios", sa.Column("ciudad", sa.String(length=100), nullable=True))
    op.execute("UPDATE usuarios SET ciudad = 'MEDELLIN' WHERE rol = 'ADMIN' AND ciudad IS NULL")


def downgrade() -> None:
    op.drop_column("usuarios", "ciudad")
