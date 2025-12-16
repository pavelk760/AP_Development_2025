import pytest
from uuid import uuid4
from app.models.models import User
from app.repositories.user_repository import UserRepository
from app.schemas.schemas import UserCreate, UserUpdate


class TestUserRepository:
    @pytest.mark.asyncio
    async def test_create_user(self, user_repository: UserRepository):
        """Тест создания пользователя в репозитории"""
        user_data = UserCreate(
            email="test@example.com",
            username="john_doe",
            description="Test user"
        )

        user = await user_repository.create(user_data)

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.username == "john_doe"
        assert user.description == "Test user"

    @pytest.mark.asyncio
    async def test_get_user_by_email(self, user_repository: UserRepository):
        """Тест получения пользователя по email"""
        # Сначала создаем пользователя
        user_data = UserCreate(
            email="unique@example.com",
            username="user_test",
            description="Test user"
        )
        user = await user_repository.create(user_data)

        # Затем ищем по email
        found_user = await user_repository.get_by_email("unique@example.com")

        assert found_user is not None
        assert found_user.id == user.id
        assert found_user.email == "unique@example.com"

    @pytest.mark.asyncio
    async def test_update_user(self, user_repository: UserRepository):
        """Тест обновления пользователя"""
        user_data = UserCreate(
            email="update@example.com",
            username="test",
            description="Original description"
        )
        user = await user_repository.create(user_data)

        update_data = UserUpdate(description="Updated description")
        updated_user = await user_repository.update(user.id, update_data)

        assert updated_user.username == "test"
        assert updated_user.description == "Updated description"
        assert updated_user.email == "update@example.com"

    @pytest.mark.asyncio
    async def test_delete_user(self, user_repository: UserRepository):
        """Тест удаления пользователя"""
        user_data = UserCreate(
            email="delete@example.com",
            username="delete_user",
            description="To be deleted"
        )
        user = await user_repository.create(user_data)

        # Проверяем, что пользователь создан
        found_user = await user_repository.get_by_id(user.id)
        assert found_user is not None

        # Удаляем пользователя
        await user_repository.delete(user.id)

        # Проверяем, что пользователь удален
        deleted_user = await user_repository.get_by_id(user.id)
        assert deleted_user is None

    @pytest.mark.asyncio
    async def test_get_by_filter(self, user_repository: UserRepository):
        """Тест получения пользователей с фильтрацией"""
        # Очищаем базу перед тестом
        users = await user_repository.get_by_filter()
        for user in users:
            await user_repository.delete(user.id)

        # Создаем несколько пользователей
        for i in range(5):
            user_data = UserCreate(
                email=f"user{i}@example.com",
                username=f"user{i}",
                description=f"User {i}"
            )
            await user_repository.create(user_data)

        # Получаем пользователей с пагинацией
        users = await user_repository.get_by_filter(count=2, page=1)

        assert len(users) == 2
        # Проверяем что имена соответствуют ожидаемым
        user_names = [user.username for user in users]
        assert all(name in ["user0", "user1", "user2", "user3", "user4"] for name in user_names)
        assert user_names[0] != user_names[1]  # Убеждаемся что это разные пользователи

    @pytest.mark.asyncio
    async def test_get_by_filter_with_email_filter(self, user_repository: UserRepository):
        """Тест получения пользователей с фильтром по email"""
        # Очищаем базу перед тестом
        users = await user_repository.get_by_filter()
        for user in users:
            await user_repository.delete(user.id)

        # Создаем тестовых пользователей
        user1 = await user_repository.create(UserCreate(
            email="filter1@example.com",
            username="filter1",
            description="Test 1"
        ))

        user2 = await user_repository.create(UserCreate(
            email="filter2@example.com",
            username="filter2",
            description="Test 2"
        ))

        # Фильтруем по email
        users = await user_repository.get_by_filter(email="filter1@example.com")

        assert len(users) == 1
        assert users[0].email == "filter1@example.com"
        assert users[0].username == "filter1"

    @pytest.mark.asyncio
    async def test_count(self, user_repository: UserRepository):
        """Тест подсчета пользователей"""
        # Очищаем базу
        users = await user_repository.get_by_filter()
        for user in users:
            await user_repository.delete(user.id)

        # Создаем 3 пользователя
        for i in range(3):
            user_data = UserCreate(
                email=f"count{i}@example.com",
                username=f"count{i}",
                description=f"Count user {i}"
            )
            await user_repository.create(user_data)

        count = await user_repository.count()
        assert count == 3

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, user_repository: UserRepository):
        """Тест получения несуществующего пользователя по ID"""
        non_existent_id = uuid4()
        user = await user_repository.get_by_id(non_existent_id)

        assert user is None

    @pytest.mark.asyncio
    async def test_get_by_email_not_found(self, user_repository: UserRepository):
        """Тест получения несуществующего пользователя по email"""
        user = await user_repository.get_by_email("nonexistent@example.com")

        assert user is None

    @pytest.mark.asyncio
    async def test_update_user_not_found(self, user_repository: UserRepository):
        """Тест обновления несуществующего пользователя"""
        non_existent_id = uuid4()
        update_data = UserUpdate(description="Updated")

        with pytest.raises(ValueError, match=f"User with id {non_existent_id} not found"):
            await user_repository.update(non_existent_id, update_data)