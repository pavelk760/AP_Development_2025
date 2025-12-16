import pytest
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND
from uuid import uuid4
from app.schemas.schemas import UserCreate, UserUpdate


class TestUserRoutes:
    @pytest.mark.asyncio
    async def test_get_all_users(self, client):
        """Тест получения списка пользователей"""
        response = client.get("/users")
        print(f"GET /users - Status: {response.status_code}, Body: {response.text}")  # DEBUG
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert "total" in data
        assert "users" in data

    @pytest.mark.asyncio
    async def test_create_user(self, client):
        """Тест создания пользователя"""
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "description": "New user description"
        }

        response = client.post("/users", json=user_data)
        print(f"POST /users - Status: {response.status_code}, Body: {response.text}")  # DEBUG
        assert response.status_code == HTTP_201_CREATED

        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert "id" in data

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, client):
        """Тест получения несуществующего пользователя"""
        non_existent_id = uuid4()
        response = client.get(f"/users/{non_existent_id}")
        print(f"GET /users/{{id}} - Status: {response.status_code}, Body: {response.text}")  # DEBUG
        assert response.status_code == HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_create_and_get_user(self, client):
        """Тест создания и получения пользователя"""
        # Создаем пользователя
        create_data = {
            "email": "testget@example.com",
            "username": "testget",
            "description": "Test get user"
        }

        create_response = client.post("/users", json=create_data)
        print(f"POST /users - Status: {create_response.status_code}, Body: {create_response.text}")  # DEBUG
        assert create_response.status_code == HTTP_201_CREATED

        created_user = create_response.json()
        user_id = created_user["id"]

        # Получаем пользователя
        get_response = client.get(f"/users/{user_id}")
        print(f"GET /users/{{id}} - Status: {get_response.status_code}, Body: {get_response.text}")  # DEBUG
        assert get_response.status_code == HTTP_200_OK

        fetched_user = get_response.json()
        assert fetched_user["id"] == user_id
        assert fetched_user["email"] == create_data["email"]
        assert fetched_user["username"] == create_data["username"]

    @pytest.mark.asyncio
    async def test_update_user(self, client):
        """Тест обновления пользователя"""
        # Сначала создаем пользователя
        create_data = {
            "email": "toupdate@example.com",
            "username": "toupdate",
            "description": "Original description"
        }

        create_response = client.post("/users", json=create_data)
        print(f"POST /users - Status: {create_response.status_code}, Body: {create_response.text}")  # DEBUG
        assert create_response.status_code == HTTP_201_CREATED

        created_user = create_response.json()
        user_id = created_user["id"]

        # Обновляем пользователя
        update_data = {
            "description": "Updated description"
        }

        update_response = client.put(f"/users/{user_id}", json=update_data)
        print(f"PUT /users/{{id}} - Status: {update_response.status_code}, Body: {update_response.text}")  # DEBUG
        assert update_response.status_code == HTTP_200_OK

        updated_user = update_response.json()
        assert updated_user["description"] == "Updated description"
        assert updated_user["email"] == "toupdate@example.com"

    @pytest.mark.asyncio
    async def test_delete_user(self, client):
        """Тест удаления пользователя"""
        # Создаем пользователя
        create_data = {
            "email": "todelete@example.com",
            "username": "todelete",
            "description": "To be deleted"
        }

        create_response = client.post("/users", json=create_data)
        print(f"POST /users - Status: {create_response.status_code}, Body: {create_response.text}")  # DEBUG
        assert create_response.status_code == HTTP_201_CREATED

        created_user = create_response.json()
        user_id = created_user["id"]

        # Удаляем пользователя
        delete_response = client.delete(f"/users/{user_id}")
        print(f"DELETE /users/{{id}} - Status: {delete_response.status_code}")  # DEBUG
        assert delete_response.status_code == HTTP_204_NO_CONTENT

        # Проверяем, что пользователь удален
        get_response = client.get(f"/users/{user_id}")
        print(f"GET /users/{{id}} after delete - Status: {get_response.status_code}, Body: {get_response.text}")  # DEBUG
        assert get_response.status_code == HTTP_404_NOT_FOUND