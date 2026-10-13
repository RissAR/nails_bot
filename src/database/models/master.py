from typing import TYPE_CHECKING
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models.base import Base

if TYPE_CHECKING:
    from src.database.models.appointment import Appointment


class Master(Base):
    __tablename__ = "masters"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1", nullable=False)

    appointments: Mapped[list["Appointment"]] = relationship(
        "Appointment",
        back_populates="master",
    )

    def __repr__(self) -> str:
        return f"<Master id={self.id} name={self.name}>"
