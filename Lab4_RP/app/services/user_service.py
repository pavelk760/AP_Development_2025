from app.repositories.user_repository import UserRepository
from app.schemas.schemas import UserCreate, UserUpdate
from app.models.models import User
from uuid import UUID
from typing import List, Optional

class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def get_by_id(self, user_id: UUID) -> User | None:
        return await self.user_repository.get_by_id(user_id)

    async def get_by_email(self, email: str) -> User | None:
        return await self.user_repository.get_by_email(email)

    async def get_by_filter(self, count: int = 100, page: int = 1, **kwargs) -> List[User]:
        return await self.user_repository.get_by_filter(count, page, **kwargs)

    async def create(self, user_data: UserCreate) -> User:
        return await self.user_repository.create(user_data)

    async def update(self, user_id: UUID, user_data: UserUpdate) -> User:
        return await self.user_repository.update(user_id, user_data)

    async def delete(self, user_id: UUID) -> None:
        await self.user_repository.delete(user_id)

    async def get_total_count(self) -> int:
        return await self.user_repository.count()