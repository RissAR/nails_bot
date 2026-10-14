import logging
from datetime import time
from sqlalchemy import func, select

from src.database.models import (
    Base,
    Category,
    Master,
    MasterService,
    Schedule,
    Service,
)
from src.database.session import async_session_maker, engine

logger = logging.getLogger(__name__)


SERVICES_CATALOG = [
    {
        "category_slug": "manicure-complexes",
        "name": "Комплекс «Базовий Однотон»",
        "description": "Зняття старого покриття, комбінований/апаратний манікюр, вирівнювання пластини, покриття гель-лаком в один тон.",
        "duration_minutes": 90,
        "price": 750.0,
        "masters": ["Олена", "Вікторія"],
    },
    {
        "category_slug": "manicure-complexes",
        "name": "Комплекс «Френч / Градієнт»",
        "description": "Повний комплекс манікюру з ідеальним френчем або плавним градієнтом на всі нігтики.",
        "duration_minutes": 105,
        "price": 900.0,
        "masters": ["Олена", "Вікторія"],
    },
    {
        "category_slug": "manicure-complexes",
        "name": "Комплекс «Укріплення гелем + Однотон»",
        "description": "Зняття + комбі-чистка + армування міцним гелем/акригелем + покриття",
        "duration_minutes": 105,
        "price": 900.0,
        "masters": ["Олена", "Вікторія"],
    },
    {
        "category_slug": "manicure-complexes",
        "name": "Гігієнічний манікюр",
        "description": "Чистий комбінований/апаратний манікюр без покриття, полірування або лікувальне зміцнення.",
        "duration_minutes": 45,
        "price": 350.0,
        "masters": ["Олена", "Вікторія"],
    },
    {
        "category_slug": "manicure-complexes",
        "name": "Чоловічий гігієнічний манікюр",
        "description": "Апаратна/комбінована чистка жорсткої кутикули, шліфування, доглядова олія",
        "duration_minutes": 45,
        "price": 500.0,
        "masters": ["Олена", "Вікторія"],
    },
    {
        "category_slug": "manicure-complexes",
        "name": "Японський Еко-манікюр",
        "description": "Натуральний догляд та втирання мінеральної пасти з перловою пудрою для природного блиску та зміцнення.",
        "duration_minutes": 60,
        "price": 600.0,
        "masters": ["Вікторія"],
    },
    {
        "category_slug": "nail-extensions",
        "name": "Нарощування нігтів (з нуля)",
        "description": "Нарощування гелем або полігелем бажаної довжини та форми, манікюр, однотонне покриття.",
        "duration_minutes": 150,
        "price": 1100.0,
        "masters": ["Олена"],
    },
    {
        "category_slug": "nail-extensions",
        "name": "Корекція нарощених нігтів",
        "description": "Відновлення архітектури нарощених нігтів, підняття клюючих нігтів, зміна форми, покриття.",
        "duration_minutes": 120,
        "price": 800.0,
        "masters": ["Олена"],
    },
    {
        "category_slug": "care-addons",
        "name": "Ремонт / Донарощування 1 нігтя",
        "description": "Ремонт тріщини шовком/акрилом або донарощування зламаного нігтя.",
        "duration_minutes": 15,
        "price": 70.0,
        "masters": ["Олена", "Вікторія"],
    },
    {
        "category_slug": "care-addons",
        "name": "Укріплення гелем / акрилом",
        "description": "Додаткове зміцнення тонких або схильних до ламкості нігтів твердим матеріалом.",
        "duration_minutes": 20,
        "price": 150.0,
        "masters": ["Олена", "Вікторія"],
    },
    {
        "category_slug": "care-addons",
        "name": "SPA-догляд (Парафінотерапія)",
        "description": "Глибоке живлення та відновлення шкіри рук гарячим парафіном з арома-маслами.",
        "duration_minutes": 30,
        "price": 200.0,
        "masters": ["Олена", "Вікторія"],
    },
    {
        "category_slug": "care-addons",
        "name": "Зняття матеріалу (без манікюру)",
        "description": "Безпечне апаратне зняття штучного покриття з наданням форми нігтям",
        "duration_minutes": 30,
        "price": 200.0,
        "masters": ["Олена", "Вікторія"],
    },
]


async def sync_services_and_prices() -> None:
    """Synchronize service prices, durations and ensure all 12 services exist."""
    async with async_session_maker() as session:
        categories = (await session.scalars(select(Category))).all()
        cat_map = {c.slug: c.id for c in categories}
        masters = (await session.scalars(select(Master))).all()
        master_map = {m.name: m.id for m in masters}

        existing_services = (await session.scalars(select(Service))).all()
        existing_map = {s.name: s for s in existing_services}

        for item in SERVICES_CATALOG:
            cat_id = cat_map.get(item["category_slug"])
            if not cat_id:
                continue

            svc = existing_map.get(item["name"])
            if svc:
                svc.price = item["price"]
                svc.duration_minutes = item["duration_minutes"]
                svc.category_id = cat_id
                if item.get("description"):
                    svc.description = item["description"]
            else:
                svc = Service(
                    category_id=cat_id,
                    name=item["name"],
                    description=item.get("description", ""),
                    duration_minutes=item["duration_minutes"],
                    price=item["price"],
                    is_active=True,
                )
                session.add(svc)
                await session.flush()
                existing_map[item["name"]] = svc

            for m_name in item["masters"]:
                m_id = master_map.get(m_name)
                if m_id:
                    link_exists = await session.scalar(
                        select(MasterService).where(
                            MasterService.master_id == m_id,
                            MasterService.service_id == svc.id,
                        )
                    )
                    if not link_exists:
                        session.add(MasterService(master_id=m_id, service_id=svc.id))

        await session.commit()
        logger.info("Successfully synced service catalog, prices and master links.")


async def seed_initial_data() -> None:
    """Seed initial Sense Nail Studio categories, masters, services, and schedules."""
    async with async_session_maker() as session:
        # Check if already seeded
        categories_count = await session.scalar(select(func.count(Category.id)))
        if categories_count and categories_count > 0:
            logger.info("Database already contains seeded categories. Proceeding to sync.")
            return

        logger.info("Seeding initial Sense Nail Studio data...")

        # 1. Masters
        olena = Master(
            name="Олена",
            title="Top Master",
            bio=(
                "Досвід: 4 роки. Спеціалізація: Складні техніки, моделювання нігтів, "
                "френч, ремонт та відновлення архітектури."
            ),
            is_active=True,
        )
        viktoria = Master(
            name="Вікторія",
            title="Master",
            bio=(
                "Досвід: 2 роки. Спеціалізація: Апаратний та комбі-манікюр, нюдові покриття, "
                "японський еко-манікюр, SPA-догляд."
            ),
            is_active=True,
        )
        session.add_all([olena, viktoria])
        await session.flush()

        # 2. Schedules
        # Олена: Пн (0), Ср (2), Пт (4), Нд (6) (09:00 – 19:00)
        olena_days = [0, 2, 4, 6]
        for day in olena_days:
            session.add(
                Schedule(
                    master_id=olena.id,
                    day_of_week=day,
                    start_time=time(9, 0),
                    end_time=time(19, 0),
                    is_day_off=False,
                )
            )

        # Вікторія: Вт (1), Чт (3), Сб (5) (10:00 – 20:00)
        viktoria_days = [1, 3, 5]
        for day in viktoria_days:
            session.add(
                Schedule(
                    master_id=viktoria.id,
                    day_of_week=day,
                    start_time=time(10, 0),
                    end_time=time(20, 0),
                    is_day_off=False,
                )
            )

        # 3. Categories
        cat_complexes = Category(
            name="Комплекси манікюру",
            slug="manicure-complexes",
        )
        cat_extensions = Category(
            name="Моделювання та нарощування",
            slug="nail-extensions",
        )
        cat_addons = Category(
            name="Доглядові послуги та Add-ons",
            slug="care-addons",
        )
        session.add_all([cat_complexes, cat_extensions, cat_addons])
        await session.commit()
        logger.info("Successfully seeded Sense Nail Studio categories, masters, and schedules.")


async def init_db() -> None:
    """Initialize database tables, seed data, and sync services."""
    from sqlalchemy import text
    import src.database.models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Safe migration for existing SQLite DB
        for col_def in [
            "completed_visits INTEGER DEFAULT 0 NOT NULL",
            "total_spent REAL DEFAULT 0.0 NOT NULL",
            "discount_percent INTEGER DEFAULT 0 NOT NULL",
        ]:
            col_name = col_def.split()[0]
            try:
                await conn.execute(text(f"ALTER TABLE users ADD COLUMN {col_def}"))
                logger.info("Migrated users table: added column %s", col_name)
            except Exception:
                pass

        for col_def in [
            "reminded_24h INTEGER DEFAULT 0 NOT NULL",
            "reminded_2h INTEGER DEFAULT 0 NOT NULL",
            "admin_alerted INTEGER DEFAULT 0 NOT NULL",
            "feedback_requested INTEGER DEFAULT 0 NOT NULL",
            "rating INTEGER NULL",
            "repeat_reminded INTEGER DEFAULT 0 NOT NULL",
        ]:
            col_name = col_def.split()[0]
            try:
                await conn.execute(text(f"ALTER TABLE appointments ADD COLUMN {col_def}"))
                logger.info("Migrated appointments table: added column %s", col_name)
            except Exception:
                pass

    await seed_initial_data()
    await sync_services_and_prices()
