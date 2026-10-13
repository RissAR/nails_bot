from typing import TYPE_CHECKING
from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models.base import Base

if TYPE_CHECKING:
    from src.database.models.appointment import Appointment
    from src.database.models.schedule import Schedule
    from src.database.models.service import Service


class MasterService(Base):
    __tablename__ = "master_services"

    master_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("masters.id", ondelete="CASCADE"),
        primary_key=True,
    )
    service_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("services.id", ondelete="CASCADE"),
        primary_key=True,
    )


class Master(Base):
    __tablename__ = "masters"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(100), default="Master", server_default="Master", nullable=False)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1", nullable=False)

    services: Mapped[list["Service"]] = relationship(
        "Service",
        secondary="master_services",
        back_populates="masters",
    )
    schedules: Mapped[list["Schedule"]] = relationship(
        "Schedule",
        back_populates="master",
        cascade="all, delete-orphan",
    )
    appointments: Mapped[list["Appointment"]] = relationship(
        "Appointment",
        back_populates="master",
    )

    def __repr__(self) -> str:
        return f"<Master id={self.id} name={self.name} title={self.title}>"
