from sqlalchemy import Column, String, Float, DateTime, UUID, func
from sqlalchemy.orm import relationship
from config.database import Base
import uuid

class Machine(Base):
    __tablename__ = "machines"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, index=True)
    location = Column(String, index=True)
    hours = Column(Float)
    degrade = Column(Float)
    fault_threshold = Column(Float)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    sensor_data = relationship("SensorData", back_populates="machine")

    def __repr__(self):
        return f"Machine(id={self.id}, name={self.name}, location={self.location}, hours={self.hours}, degrade={self.degrade}, fault_threshold={self.fault_threshold})"