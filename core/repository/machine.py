from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from core.models.machine import Machine
from core.schemas.machine import (
    MachineListInput,
    MachineListOutput,
    MachineSummary,
    MachineGetInput,
    MachineGetOutput,
    MachineCreateInput,
    MachineCreateOutput,
    MachineUpdateInput,
    MachineUpdateOutput,
    MachineDeleteInput,
    MachineDeleteOutput,
)

_SORTABLE_FIELDS = set(Machine.__table__.columns.keys())


class MachineRepository:
    """Repository for the Machine model"""

    def __init__(self, db: Session):
        self.db = db

    def list(self, filters: Optional[MachineListInput] = None) -> MachineListOutput:
        """List machines"""
        if filters is None:
            filters = MachineListInput()

        query = self.db.query(Machine)

        if filters.name is not None:
            query = query.filter(Machine.name == filters.name)

        if filters.location is not None:
            query = query.filter(Machine.location == filters.location)

        if filters.min_degrade is not None:
            query = query.filter(Machine.degrade >= filters.min_degrade)

        if filters.max_degrade is not None:
            query = query.filter(Machine.degrade <= filters.max_degrade)

        total = query.count()

        sort_field = filters.sort_by if filters.sort_by in _SORTABLE_FIELDS else "name"
        sort_column = getattr(Machine, sort_field)
        query = query.order_by(sort_column.asc() if filters.sort_order == "asc" else sort_column.desc())

        query = query.offset(filters.offset).limit(filters.limit)

        machines = query.all()

        return MachineListOutput(
            machines=[MachineSummary.model_validate(machine) for machine in machines],
            total=total,
            limit=filters.limit,
            offset=filters.offset,
        )

    def get(self, input: MachineGetInput) -> MachineGetOutput:
        """Get a machine by id"""
        machine = self.db.query(Machine).filter(Machine.id == input.id).first()
        if not machine:
            raise ValueError(f"Machine with id {input.id} not found")
        return MachineGetOutput.model_validate(machine)

    def create(self, input: MachineCreateInput) -> MachineCreateOutput:
        """Create a new machine"""
        existing = self.db.query(Machine).filter(Machine.name == input.name).first()
        if existing:
            raise ValueError(f"Machine with name {input.name} already exists")

        machine = Machine(
            name=input.name,
            location=input.location,
            hours=input.hours,
            degrade=input.degrade,
            fault_threshold=input.fault_threshold,
        )

        self.db.add(machine)
        self.db.commit()

        return MachineCreateOutput.model_validate(machine)

    def update(self, id: UUID, input: MachineUpdateInput) -> MachineUpdateOutput:
        """Update a machine (partial update: only the fields provided are changed)"""
        machine = self.db.query(Machine).filter(Machine.id == id).first()
        if not machine:
            raise ValueError(f"Machine with id {id} not found")

        # MachineUpdateInput.model_dump() already drops unset/None fields, so this
        # only touches the attributes the caller actually asked to change.
        # updated_at is refreshed automatically by the column's onupdate=func.now().
        for field, value in input.model_dump().items():
            setattr(machine, field, value)

        self.db.commit()

        return MachineUpdateOutput.model_validate(machine)

    def delete(self, input: MachineDeleteInput) -> MachineDeleteOutput:
        """Delete a machine"""
        machine = self.db.query(Machine).filter(Machine.id == input.id).first()
        if not machine:
            raise ValueError(f"Machine with id {input.id} not found")

        self.db.delete(machine)
        self.db.commit()

        return MachineDeleteOutput()
