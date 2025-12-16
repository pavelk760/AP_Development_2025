import pytest
from unittest.mock import Mock, AsyncMock
from uuid import uuid4

from app.services.user_service import UserService
from app.schemas.schemas import UserCreate, UserUpdate


class TestUserService:
    @pytest.mark.asyncio
    async def test_create_user_success(self):
        """Тест успешного создания пользователя через сервис"""
        # Мокаем репозиторий
        mock_repo = AsyncMock()

        # Настраиваем мок
        user_id = uuid4()
        mock_user = Mock(
            id=user_id,
            email="test@example.com",
            username="test_user",
            description="Test user"
        )
        mock_repo.create.return_value = mock_user

        # Создаем сервис
        user_service = UserService(mock_repo)

        # Тестируем
        user_data = UserCreate(
            email="test@example.com",
            username="test_user",
            description="Test user"
        )

        result = await user_service.create(user_data)

        assert result is not None
        assert result.id == user_id
        assert result.email == "test@example.com"
        mock_repo.create.assert_called_once_with(user_data)

    @pytest.mark.asyncio
    async def test_get_user_by_id_found(self):
        """Тест получения пользователя по ID (найден)"""
        mock_repo = AsyncMock()
        user_id = uuid4()
        mock_user = Mock(id=user_id, email="test@example.com")
        mock_repo.get_by_id.return_value = mock_user

        user_service = UserService(mock_repo)
        result = await user_service.get_by_id(user_id)

        assert result is not None
        assert result.id == user_id
        mock_repo.get_by_id.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self):
        """Тест получения пользователя по ID (не найден)"""
        mock_repo = AsyncMock()
        user_id = uuid4()
        mock_repo.get_by_id.return_value = None

        user_service = UserService(mock_repo)
        result = await user_service.get_by_id(user_id)

        assert result is None
        mock_repo.get_by_id.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_update_user(self):
        """Тест обновления пользователя"""
        mock_repo = AsyncMock()
        user_id = uuid4()

        updated_user = Mock(
            id=user_id,
            email="updated@example.com",
            username="updated_user",
            description="Updated description"
        )
        mock_repo.update.return_value = updated_user

        user_service = UserService(mock_repo)
        update_data = UserUpdate(description="Updated description")

        result = await user_service.update(user_id, update_data)

        assert result is not None
        assert result.description == "Updated description"
        mock_repo.update.assert_called_once_with(user_id, update_data)

    @pytest.mark.asyncio
    async def test_delete_user(self):
        """Тест удаления пользователя"""
        mock_repo = AsyncMock()
        user_id = uuid4()

        user_service = UserService(mock_repo)
        await user_service.delete(user_id)

        mock_repo.delete.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_get_total_count(self):
        """Тест получения общего количества пользователей"""
        mock_repo = AsyncMock()
        mock_repo.count.return_value = 5

        user_service = UserService(mock_repo)
        count = await user_service.get_total_count()

        assert count == 5
        mock_repo.count.assert_called_once()