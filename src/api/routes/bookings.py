from datetime import date, datetime, time, timedelta
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from src.database.models import Appointment, Master, Service, User
from src.database.session import async_session_maker

router = APIRouter(tags=["Bookings"])


class BookingCreateRequest(BaseModel):
    service_id: int
    master_id: int
    booking_date: str = Field(..., description="YYYY-MM-DD")
    start_time: str = Field(..., description="HH:MM")
    client_name: str
    client_phone: str
    telegram_id: int | None = None
    notes: str | None = None


class BookingResponse(BaseModel):
    id: int
    status: str
    booking_date: str
    start_time: str
    end_time: str
    service_name: str
    master_name: str
    price: float


class AdminBookingItem(BaseModel):
    id: int
    client_name: str
    client_phone: str | None
    telegram_id: int | None
    service_name: str
    price: float
    duration_minutes: int
    master_name: str
    booking_date: str
    start_time: str
    end_time: str
    status: str
    notes: str | None


class AdminStatsResponse(BaseModel):
    pending_count: int
    today_confirmed_count: int
    total_revenue: float
    total_clients: int


@router.post("/bookings", response_model=BookingResponse)
async def create_booking(payload: BookingCreateRequest) -> BookingResponse:
    """Create a new booking appointment."""
    try:
        b_date = date.fromisoformat(payload.booking_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    try:
        parts = payload.start_time.split(":")
        s_time = time(int(parts[0]), int(parts[1]))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM")

    async with async_session_maker() as session:
        # 1. Fetch service
        svc = await session.get(Service, payload.service_id)
        if not svc:
            raise HTTPException(status_code=404, detail="Service not found")

        # 2. Fetch master
        master = await session.get(Master, payload.master_id)
        if not master:
            raise HTTPException(status_code=404, detail="Master not found")

        # Calculate end_time
        start_dt = datetime.combine(b_date, s_time)
        end_dt = start_dt + timedelta(minutes=svc.duration_minutes)
        e_time = end_dt.time()

        # 3. Handle User
        tg_id = payload.telegram_id
        if tg_id is None:
            # Fallback for web guests: generate unique synthetic id
            import random
            tg_id = -random.randint(1000000, 9999999)

        u_stmt = select(User).where(User.telegram_id == tg_id)
        u_res = await session.execute(u_stmt)
        user = u_res.scalar_one_or_none()

        if not user:
            user = User(
                telegram_id=tg_id,
                full_name=payload.client_name,
                phone=payload.client_phone,
                role="client",
            )
            session.add(user)
            await session.flush()
        else:
            if payload.client_name and user.full_name != payload.client_name:
                user.full_name = payload.client_name
            if payload.client_phone and user.phone != payload.client_phone:
                user.phone = payload.client_phone
            await session.flush()

        # 4. Create Appointment
        appointment = Appointment(
            client_id=user.id,
            master_id=master.id,
            service_id=svc.id,
            booking_date=b_date,
            start_time=s_time,
            end_time=e_time,
            status="pending",
            cancellation_reason=payload.notes,
        )
        session.add(appointment)
        await session.commit()
        await session.refresh(appointment)

        return BookingResponse(
            id=appointment.id,
            status=appointment.status,
            booking_date=appointment.booking_date.isoformat(),
            start_time=appointment.start_time.strftime("%H:%M"),
            end_time=appointment.end_time.strftime("%H:%M"),
            service_name=svc.name,
            master_name=master.name,
            price=svc.price,
        )


@router.get("/admin/bookings", response_model=list[AdminBookingItem])
async def get_admin_bookings() -> list[AdminBookingItem]:
    """Return all appointments with client and service details for admin."""
    async with async_session_maker() as session:
        stmt = (
            select(Appointment)
            .options(
                selectinload(Appointment.client),
                selectinload(Appointment.service),
                selectinload(Appointment.master),
            )
            .order_by(Appointment.booking_date.desc(), Appointment.start_time.desc())
        )
        result = await session.execute(stmt)
        appointments = result.scalars().all()

        return [
            AdminBookingItem(
                id=a.id,
                client_name=a.client.full_name if a.client else "Гість",
                client_phone=a.client.phone if a.client else None,
                telegram_id=a.client.telegram_id if a.client else None,
                service_name=a.service.name if a.service else "Послуга",
                price=a.service.price if a.service else 0.0,
                duration_minutes=a.service.duration_minutes if a.service else 60,
                master_name=a.master.name if a.master else "Майстер",
                booking_date=a.booking_date.isoformat(),
                start_time=a.start_time.strftime("%H:%M"),
                end_time=a.end_time.strftime("%H:%M"),
                status=a.status,
                notes=a.cancellation_reason,
            )
            for a in appointments
        ]


@router.get("/admin/stats", response_model=AdminStatsResponse)
async def get_admin_stats() -> AdminStatsResponse:
    """Return key metrics and counters for admin panel."""
    today = date.today()
    async with async_session_maker() as session:
        pending_count = await session.scalar(
            select(func.count(Appointment.id)).where(Appointment.status == "pending")
        ) or 0

        today_confirmed_count = await session.scalar(
            select(func.count(Appointment.id)).where(
                Appointment.booking_date == today,
                Appointment.status == "confirmed",
            )
        ) or 0

        total_clients = await session.scalar(
            select(func.count(User.id)).where(User.role == "client")
        ) or 0

        # Calculate revenue from confirmed/pending
        rev_stmt = (
            select(func.sum(Service.price))
            .select_from(Appointment)
            .join(Service, Appointment.service_id == Service.id)
            .where(Appointment.status.in_(["confirmed", "pending"]))
        )
        total_revenue = await session.scalar(rev_stmt) or 0.0

        return AdminStatsResponse(
            pending_count=pending_count,
            today_confirmed_count=today_confirmed_count,
            total_revenue=float(total_revenue),
            total_clients=total_clients,
        )
