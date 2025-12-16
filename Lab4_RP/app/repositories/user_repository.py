from app.schemas.schemas import UserCreate, UserUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.models import User
from uuid import UUID
from typing import List, Optional


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_filter(self, count: int = 100, page: int = 1, **kwargs) -> List[User]:
        offset = (page - 1) * count
        query = select(User)

        # Добавляем фильтры
        for key, value in kwargs.items():
            if hasattr(User, key):
                query = query.where(getattr(User, key) == value)

        query = query.offset(offset).limit(count)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, user_data: UserCreate) -> User:
        user = User(**user_data.model_dump())
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update(self, user_id: UUID, user_data: UserUpdate) -> User:
        user = await self.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")

        update_data = user_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)

        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, user_id: UUID) -> None:
        user = await self.get_by_id(user_id)
        if user:
            await self.session.delete(user)
            await self.session.commit()

    async def count(self) -> int:
        result = await self.session.execute(select(func.count(User.id)))
        return result.scalar_one()