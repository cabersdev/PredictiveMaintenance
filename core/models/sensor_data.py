from config.database import Base
from sqlalchemy import Column, ForeignKey, Float, PrimaryKeyConstraint, DateTime, Boolean, UUID
from sqlalchemy.orm import relationship

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

