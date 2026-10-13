from datetime import date, time
from typing import TYPE_CHECKING
from sqlalchemy import Date, ForeignKey, Integer, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.database.models.master import Master
    from src.database.models.service import Service
    from src.database.models.user import User


class Appointment(Base, TimestampMixin):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    client_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    master_id: Mapped[int] = mapped_column(Integer, ForeignKey("masters.id", ondelete="CASCADE"), nullable=False)
    service_id: Mapped[int] = mapped_column(Integer, ForeignKey("services.id", ondelete="CASCADE"), nullable=False)
    booking_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    status: Mapped[str] = mapped_column(
        String(32),
        default="pending",
        server_default="pending",
        nullable=False,
    )
    cancellation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    client: Mapped["User"] = relationship("User", back_populates="appointments")
    master: Mapped["Master"] = relationship("Master", back_populates="appointments")
    service: Mapped["Service"] = relationship("Service", back_populates="appointments")

    def __repr__(self) -> str:
        return f"<Appointment id={self.id} date={self.booking_date} status={self.status}>"
