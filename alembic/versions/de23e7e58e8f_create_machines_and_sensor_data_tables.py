"""create machines and sensor_data tables

Revision ID: de23e7e58e8f
Revises:
Create Date: 2026-07-23 21:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "de23e7e58e8f"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "machines",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("location", sa.String(), nullable=True),
        sa.Column("hours", sa.Float(), nullable=True),
        sa.Column("degrade", sa.Float(), nullable=True),
        sa.Column("fault_threshold", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_machines_name"), "machines", ["name"], unique=False)
    op.create_index(op.f("ix_machines_location"), "machines", ["location"], unique=False)

    op.create_table(
        "sensor_data",
        sa.Column("machine_id", sa.UUID(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("temperature", sa.Float(), nullable=True),
        sa.Column("vibration", sa.Float(), nullable=True),
        sa.Column("pressure", sa.Float(), nullable=True),
        sa.Column("current", sa.Float(), nullable=True),
        sa.Column("hours", sa.Float(), nullable=True),
        sa.Column("is_fault", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(["machine_id"], ["machines.id"]),
        sa.PrimaryKeyConstraint("machine_id", "timestamp"),
    )
    op.create_index(op.f("ix_sensor_data_machine_id"), "sensor_data", ["machine_id"], unique=False)
    op.create_index(op.f("ix_sensor_data_timestamp"), "sensor_data", ["timestamp"], unique=False)

    # Convert sensor_data into a TimescaleDB hypertable partitioned on "timestamp".
    # Issued explicitly (rather than relying on the timescaledb_hypertable table
    # kwarg + dialect event) so it always runs regardless of how the migration
    # is invoked.
    op.execute(
        "SELECT create_hypertable('sensor_data', 'timestamp', if_not_exists => TRUE);"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_sensor_data_timestamp"), table_name="sensor_data")
    op.drop_index(op.f("ix_sensor_data_machine_id"), table_name="sensor_data")
    op.drop_table("sensor_data")

    op.drop_index(op.f("ix_machines_location"), table_name="machines")
    op.drop_index(op.f("ix_machines_name"), table_name="machines")
    op.drop_table("machines")
