from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from core.models.sensor_data import SensorData
from core.schemas.sensor_data import (
    SensorDataListInput,
    SensorDataListOutput,
    SensorDataOutput,
    SensorDataCreate,
    SensorDataBatchInput,
    SensorDataBatchOutput,
)

_SORTABLE_FIELDS = set(SensorData.__table__.columns.keys())

class SensorDataRepository:
    """Repository for the SensorData model (a TimescaleDB hypertable)"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, input: SensorDataCreate) -> SensorDataOutput:
        """Insert a single sensor reading"""
        sensor_data = SensorData(**input.model_dump())

        self.db.add(sensor_data)
        self.db.commit()

        return SensorDataOutput.model_validate(sensor_data)

    def create_batch(self, input: SensorDataBatchInput) -> SensorDataBatchOutput:
        """Insert a batch of readings (e.g. coming from the Kafka consumer).

        Each record is inserted in its own savepoint so a single invalid record
        (e.g. an unknown machine_id) fails on its own without discarding the
        rest of the batch.
        """
        inserted = 0
        errors: list[dict] = []

        for index, record in enumerate(input.records):
            try:
                with self.db.begin_nested():
                    self.db.add(SensorData(**record.model_dump()))
                    self.db.flush()
                inserted += 1
            except SQLAlchemyError as exc:
                errors.append({"index": index, "error": str(exc)})

        self.db.commit()

        return SensorDataBatchOutput(inserted=inserted, failed=len(errors), errors=errors)

    def get(self, machine_id: UUID, timestamp: datetime) -> SensorDataOutput:
        """Get a single reading by its natural key (machine_id, timestamp)"""
        sensor_data = (
            self.db.query(SensorData)
            .filter(SensorData.machine_id == machine_id, SensorData.timestamp == timestamp)
            .first()
        )
        if not sensor_data:
            raise ValueError(f"SensorData for machine {machine_id} at {timestamp} not found")
        return SensorDataOutput.model_validate(sensor_data)

    def list(self, filters: Optional[SensorDataListInput] = None) -> SensorDataListOutput:
        """List sensor readings with optional filters"""
        if filters is None:
            filters = SensorDataListInput()

        query = self.db.query(SensorData)

        if filters.machine_id is not None:
            query = query.filter(SensorData.machine_id == filters.machine_id)

        if filters.start_time is not None:
            query = query.filter(SensorData.timestamp >= filters.start_time)

        if filters.end_time is not None:
            query = query.filter(SensorData.timestamp <= filters.end_time)

        if filters.is_fault is not None:
            query = query.filter(SensorData.is_fault == filters.is_fault)

        total = query.count()

        sort_field = filters.sort_by if filters.sort_by in _SORTABLE_FIELDS else "timestamp"
        sort_column = getattr(SensorData, sort_field)
        query = query.order_by(sort_column.asc() if filters.sort_order == "asc" else sort_column.desc())

        query = query.offset(filters.offset).limit(filters.limit)

        records = query.all()

        return SensorDataListOutput(
            records=[SensorDataOutput.model_validate(record) for record in records],
            total=total,
            limit=filters.limit,
            offset=filters.offset,
        )
