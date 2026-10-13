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


async def seed_initial_data() -> None:
    """Seed initial Sense Nail Studio categories, masters, services, and schedules."""
    async with async_session_maker() as session:
        # Check if already seeded
        categories_count = await session.scalar(select(func.count(Category.id)))
        if categories_count and categories_count > 0:
            logger.info("Database already contains seeded data. Skipping seeding.")
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
        await session.flush()

        # 4. Services
        # Category 1: Комплекси манікюру
        s1 = Service(
            category_id=cat_complexes.id,
            name="Комплекс «Базовий Однотон»",
            description="Зняття старого покриття, комбінований/апаратний манікюр, вирівнювання пластини, покриття гель-лаком в один тон.",
            duration_minutes=90,
            price=550.0,
            is_active=True,
        )
        s2 = Service(
            category_id=cat_complexes.id,
            name="Комплекс «Френч / Градієнт»",
            description="Повний комплекс манікюру з ідеальним френчем або плавним градієнтом на всі нігтики.",
            duration_minutes=105,
            price=650.0,
            is_active=True,
        )
        s3 = Service(
            category_id=cat_complexes.id,
            name="Гігієнічний манікюр",
            description="Чистий комбінований/апаратний манікюр без покриття, полірування або лікувальне зміцнення.",
            duration_minutes=45,
            price=350.0,
            is_active=True,
        )
        s4 = Service(
            category_id=cat_complexes.id,
            name="Японський Еко-манікюр",
            description="Натуральний догляд та втирання мінеральної пасти з перловою пудрою для природного блиску та зміцнення.",
            duration_minutes=60,
            price=450.0,
            is_active=True,
        )

        # Category 2: Моделювання та нарощування
        s5 = Service(
            category_id=cat_extensions.id,
            name="Нарощування нігтів (з нуля)",
            description="Нарощування гелем або полігелем бажаної довжини та форми, манікюр, однотонне покриття.",
            duration_minutes=150,
            price=900.0,
            is_active=True,
        )
        s6 = Service(
            category_id=cat_extensions.id,
            name="Корекція нарощених нігтів",
            description="Відновлення архітектури нарощених нігтів, підняття клюючих нігтів, зміна форми, покриття.",
            duration_minutes=120,
            price=750.0,
            is_active=True,
        )

        # Category 3: Доглядові послуги та Add-ons
        s7 = Service(
            category_id=cat_addons.id,
            name="Ремонт / Донарощування 1 нігтя",
            description="Ремонт тріщини шовком/акрилом або донарощування зламаного нігтя.",
            duration_minutes=15,
            price=70.0,
            is_active=True,
        )
        s8 = Service(
            category_id=cat_addons.id,
            name="Укріплення гелем / акрилом",
            description="Додаткове зміцнення тонких або схильних до ламкості нігтів твердим матеріалом.",
            duration_minutes=20,
            price=150.0,
            is_active=True,
        )
        s9 = Service(
            category_id=cat_addons.id,
            name="SPA-догляд (Парафінотерапія)",
            description="Глибоке живлення та відновлення шкіри рук гарячим парафіном з арома-маслами.",
            duration_minutes=30,
            price=200.0,
            is_active=True,
        )

        services = [s1, s2, s3, s4, s5, s6, s7, s8, s9]
        session.add_all(services)
        await session.flush()

        # 5. Master-Service links:
        # s1: Олена, Вікторія
        # s2: Олена, Вікторія
        # s3: Олена, Вікторія
        # s4: лише Вікторія
        # s5: лише Олена
        # s6: лише Олена
        # s7: Олена, Вікторія
        # s8: Олена, Вікторія
        # s9: Олена, Вікторія
        master_service_links = [
            MasterService(master_id=olena.id, service_id=s1.id),
            MasterService(master_id=viktoria.id, service_id=s1.id),
            MasterService(master_id=olena.id, service_id=s2.id),
            MasterService(master_id=viktoria.id, service_id=s2.id),
            MasterService(master_id=olena.id, service_id=s3.id),
            MasterService(master_id=viktoria.id, service_id=s3.id),
            MasterService(master_id=viktoria.id, service_id=s4.id),
            MasterService(master_id=olena.id, service_id=s5.id),
            MasterService(master_id=olena.id, service_id=s6.id),
            MasterService(master_id=olena.id, service_id=s7.id),
            MasterService(master_id=viktoria.id, service_id=s7.id),
            MasterService(master_id=olena.id, service_id=s8.id),
            MasterService(master_id=viktoria.id, service_id=s8.id),
            MasterService(master_id=olena.id, service_id=s9.id),
            MasterService(master_id=viktoria.id, service_id=s9.id),
        ]
        session.add_all(master_service_links)
        await session.commit()
        logger.info("Successfully seeded Sense Nail Studio initial data.")


async def init_db() -> None:
    """Initialize database tables and seed data."""
    # Ensure models are imported
    import src.database.models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await seed_initial_data()
