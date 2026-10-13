from typing import TYPE_CHECKING
from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models.base import Base

if TYPE_CHECKING:
    from src.database.models.appointment import Appointment
    from src.database.models.category import Category
    from src.database.models.master import Master


class Service(Base):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1", nullable=False)

    category: Mapped["Category"] = relationship("Category", back_populates="services")
    masters: Mapped[list["Master"]] = relationship(
        "Master",
        secondary="master_services",
        back_populates="services",
    )
    appointments: Mapped[list["Appointment"]] = relationship(
        "Appointment",
        back_populates="service",
    )

    def __repr__(self) -> str:
        return f"<Service id={self.id} name={self.name} price={self.price}>"
