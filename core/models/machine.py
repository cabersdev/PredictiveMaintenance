from sqlalchemy import Column, String, Float, UUID
from sqlalchemy.orm import relationship
from config.database import Base
import uuid

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