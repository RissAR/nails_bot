from datetime import time
from typing import TYPE_CHECKING
from sqlalchemy import Boolean, ForeignKey, Integer, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models.base import Base

if TYPE_CHECKING:
    from src.database.models.master import Master


class Schedule(Base):
    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    master_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("masters.id", ondelete="CASCADE"),
        nullable=False,
    )
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)  # 0: Mon, 1: Tue, ..., 6: Sun
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    is_day_off: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0", nullable=False)

    master: Mapped["Master"] = relationship("Master", back_populates="schedules")

    def __repr__(self) -> str:
        return f"<Schedule id={self.id} master_id={self.master_id} day={self.day_of_week}>"
