import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from litestar.testing import TestClient
from litestar import Litestar
from litestar.di import Provide

# Импорты для тестового приложения
from app.models.models import Base
from app.controllers.user_controller import UserController
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService

# Тестовая база данных (SQLite in-memory)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def engine():
    """Движок для тестовой базы данных"""
    return create_async_engine(TEST_DATABASE_URL, echo=False, future=True)


@pytest.fixture(scope="session")
async def tables(engine):
    """Создание и удаление таблиц для тестов"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def session(engine, tables) -> AsyncGenerator[AsyncSession, None]:
    """Сессия базы данных для тестов"""
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
    )
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest.fixture
def user_repository(session):
    """Репозиторий пользователей для тестов"""
    return UserRepository(session)


# Создаем тестовое приложение с тестовой БД
@pytest.fixture
def test_app(engine):
    """Тестовое приложение Litestar с тестовой БД"""

    async_session_factory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async def provide_db_session() -> AsyncSession:
        async with async_session_factory() as session:
            try:
                yield session
            finally:
                await session.close()

    async def provide_user_repository(db_session: AsyncSession) -> UserRepository:
        return UserRepository(db_session)

    async def provide_user_service(user_repository: UserRepository) -> UserService:
        return UserService(user_repository)

    return Litestar(
        route_handlers=[UserController],
        dependencies={
            "db_session": Provide(provide_db_session),
            "user_repository": Provide(provide_user_repository),
            "user_service": Provide(provide_user_service),
        },
        debug=True  # Включаем режим отладки для тестов
    )


@pytest.fixture
def client(test_app):
    """Тестовый клиент для API тестов"""
    return TestClient(app=test_app)