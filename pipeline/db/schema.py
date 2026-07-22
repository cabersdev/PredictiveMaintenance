import datetime
from sqlalchemy import Column, ForeignKey, Float, PrimaryKeyConstraint, String, DateTime, Boolean, UUID
from sqlalchemy.orm import relationship
from pipeline.db.base import Base
import uuid

class SensorData(Base):
    __tablename__ = "sensor_data"

    __table_args__ = (
        PrimaryKeyConstraint("machine_id", "timestamp"),
        {
            "timescaledb_hypertable": {
                "time_column_name": "timestamp",
            },
        }        
    )
    
    machine_id = Column(UUID, ForeignKey("machines.id"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), index=True)
    temperature = Column(Float)
    vibration = Column(Float)
    pressure = Column(Float)
    current = Column(Float)
    hours = Column(Float)
    is_fault = Column(Boolean)

    machine = relationship("Machine", back_populates="sensor_data")

    def __repr__(self):
        return f"SensorData(machine_id={self.machine_id}, timestamp={self.timestamp}, temperature={self.temperature}, vibration={self.vibration}, pressure={self.pressure}, current={self.current}, hours={self.hours}, is_fault={self.is_fault})"

class Machine(Base):
    __tablename__ = "machines"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True)
    location = Column(String, index=True)
    hours = Column(Float)
    degrade = Column(Float)
    fault_threshold = Column(Float)

    sensor_data = relationship("SensorData", back_populates="machine")

    def __repr__(self):
        return f"Machine(id={self.id}, name={self.name}, location={self.location}, hours={self.hours}, degrade={self.degrade}, fault_threshold={self.fault_threshold})"