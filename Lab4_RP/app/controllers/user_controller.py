from litestar import Controller, get, post, delete, put
from litestar.di import Provide
from litestar.exceptions import NotFoundException
from app.services.user_service import UserService
from app.schemas.schemas import UserCreate, UserUpdate, UserResponse, UserListResponse
from uuid import UUID


class UserController(Controller):
    path = "/users"

    @get("/{user_id:uuid}")
    async def get_user_by_id(
        self,
        user_id: UUID,
        user_service: UserService,
    ) -> UserResponse:  # <-- ИЗМЕНИТЬ НА UserResponse
        user = await user_service.get_by_id(user_id)
        if not user:
            raise NotFoundException(detail=f"User with ID {user_id} не найден")
        return UserResponse.model_validate(user)  # <-- ИЗМЕНИТЬ НА UserResponse

    @get()
    async def get_all_users(
        self,
        user_service: UserService,
        count: int = 100,
        page: int = 1,
    ) -> UserListResponse:
        users = await user_service.get_by_filter(count=count, page=page)
        total = await user_service.get_total_count()
        return UserListResponse(
            total=total,
            users=[UserResponse.model_validate(user) for user in users]  # <-- ИЗМЕНИТЬ НА UserResponse
        )

    @post()
    async def create_user(
        self,
        user_service: UserService,
        data: UserCreate,  # <-- ИЗМЕНИТЬ ПАРАМЕТР НА data (не user_data)
    ) -> UserResponse:  # <-- ИЗМЕНИТЬ НА UserResponse
        user = await user_service.create(data)
        return UserResponse.model_validate(user)  # <-- ИЗМЕНИТЬ НА UserResponse

    @delete("/{user_id:uuid}")
    async def delete_user(
        self,
        user_id: UUID,
        user_service: UserService,
    ) -> None:
        await user_service.delete(user_id)

    @put("/{user_id:uuid}")
    async def update_user(
        self,
        user_id: UUID,
        user_service: UserService,
        data: UserUpdate,  # <-- ИЗМЕНИТЬ ПАРАМЕТР НА data
    ) -> UserResponse:  # <-- ИЗМЕНИТЬ НА UserResponse
        user = await user_service.update(user_id, data)
        return UserResponse.model_validate(user)  # <-- ИЗМЕНИТЬ НА UserResponse