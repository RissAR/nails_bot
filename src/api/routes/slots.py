from datetime import date, datetime, time, timedelta
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select

from src.database.models import Appointment, Master, Schedule, Service
from src.database.session import async_session_maker

router = APIRouter(prefix="/slots", tags=["Slots"])


@router.get("", response_model=list[str])
async def get_free_slots(
    master_id: int = Query(..., description="Master ID"),
    date_str: str = Query(..., alias="date", description="Date YYYY-MM-DD"),
    service_id: int = Query(..., description="Service ID"),
) -> list[str]:
    """Calculate and return free booking slots for a given master, date, and service."""
    try:
        booking_date = date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    async with async_session_maker() as session:
        # Check master exists and is active
        master = await session.get(Master, master_id)
        if not master or not master.is_active:
            return []

        # 1. Fetch service to get duration
        svc_stmt = select(Service).where(Service.id == service_id, Service.is_active == True)  # noqa: E712
        svc_res = await session.execute(svc_stmt)
        service = svc_res.scalar_one_or_none()
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")

        duration_min = service.duration_minutes
        service_delta = timedelta(minutes=duration_min)
        buffer_delta = timedelta(minutes=15)

        # 2. Fetch master schedule for day_of_week
        day_of_week = booking_date.weekday()  # 0: Mon ... 6: Sun
        sch_stmt = select(Schedule).where(
            Schedule.master_id == master_id,
            Schedule.day_of_week == day_of_week,
        )
        sch_res = await session.execute(sch_stmt)
        schedule = sch_res.scalar_one_or_none()

        if not schedule or schedule.is_day_off:
            return []

        # 3. Fetch existing appointments on this date
        apt_stmt = select(Appointment).where(
            Appointment.master_id == master_id,
            Appointment.booking_date == booking_date,
            Appointment.status.in_(["pending", "confirmed"]),
        )
        apt_res = await session.execute(apt_stmt)
        appointments = apt_res.scalars().all()

        # Build busy intervals
        busy_intervals: list[tuple[datetime, datetime]] = []
        for apt in appointments:
            apt_start_dt = datetime.combine(booking_date, apt.start_time)
            apt_end_dt = datetime.combine(booking_date, apt.end_time) + buffer_delta
            busy_intervals.append((apt_start_dt, apt_end_dt))

        # 4. Generate candidate slots
        work_start_dt = datetime.combine(booking_date, schedule.start_time)
        work_end_dt = datetime.combine(booking_date, schedule.end_time)

        now = datetime.now()
        free_slots: list[str] = []

        # Step by 30 minutes
        curr_dt = work_start_dt
        step = timedelta(minutes=30)

        while curr_dt + service_delta <= work_end_dt:
            slot_end_dt = curr_dt + service_delta

            # If booking is for today, skip past times
            if booking_date == date.today() and curr_dt <= now:
                curr_dt += step
                continue

            # Check for conflict with existing bookings
            conflict = False
            for b_start, b_end in busy_intervals:
                # Two intervals [curr_dt, slot_end_dt] and [b_start, b_end] overlap if:
                if max(curr_dt, b_start) < min(slot_end_dt, b_end):
                    conflict = True
                    break

            if not conflict:
                free_slots.append(curr_dt.strftime("%H:%M"))

            curr_dt += step

        return free_slots
