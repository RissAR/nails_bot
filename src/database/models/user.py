from typing import TYPE_CHECKING
from sqlalchemy import BigInteger, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.database.models.appointment import Appointment


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(32), default="client", server_default="client", nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)

    completed_visits: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
    total_spent: Mapped[float] = mapped_column(Float, default=0.0, server_default="0.0", nullable=False)
    discount_percent: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)

    appointments: Mapped[list["Appointment"]] = relationship(
        "Appointment",
        back_populates="client",
        cascade="all, delete-orphan",
    )

    @property
    def loyalty_info(self) -> tuple[str, int]:
        """Return (tier_name, effective_discount_percent)."""
        if self.completed_visits >= 7:
            tier = "VIP-клієнт"
            tier_discount = 10
        elif self.completed_visits >= 3:
            tier = "Постійний клієнт"
            tier_discount = 5
        else:
            tier = "Новий клієнт"
            tier_discount = 0
        return tier, max(tier_discount, self.discount_percent)

    def __repr__(self) -> str:
        return f"<User id={self.id} telegram_id={self.telegram_id} role={self.role}>"
