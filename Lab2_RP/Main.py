from sqlalchemy.orm import DeclarativeBase, sessionmaker, Mapped, mapped_column, relationship, selectinload
from sqlalchemy import String, ForeignKey, create_engine, select, Text
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import engine_from_config
from sqlalchemy import pool
#from alembic import context
#http://localhost:8080

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    description: Mapped[str] = mapped_column(nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now)

    addresses = relationship("Address", back_populates="user")
    orders = relationship("Order", back_populates="user")


class Address(Base):
    __tablename__ = 'addresses'

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id'), nullable=False)
    street: Mapped[str] = mapped_column(nullable=False)
    city: Mapped[str] = mapped_column(nullable=False)
    state: Mapped[str] = mapped_column()
    zip_code: Mapped[str] = mapped_column()
    country: Mapped[str] = mapped_column(nullable=False)
    is_primary: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now)

    user = relationship("User", back_populates="addresses")
    orders = relationship("Order", back_populates="address")


class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id'), nullable=False)
    address_id: Mapped[UUID] = mapped_column(ForeignKey('addresses.id'), nullable=False)

    # ИНФОРМАЦИЯ О ПРОДУКЦИИ (в одной таблице)
    product_name: Mapped[str] = mapped_column(String(100), nullable=False)
    product_description: Mapped[str] = mapped_column(Text)
    product_price: Mapped[float] = mapped_column(nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False, default=1)

    total_amount: Mapped[float] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now)

    user = relationship("User", back_populates="orders")
    address = relationship("Address", back_populates="orders")


engine = create_engine(
    'postgresql+psycopg2://postgres:postgres@localhost/test_db',
    echo=True
)

# Пересоздаем таблицы с новой структурой
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

session_factory = sessionmaker(engine)


def add_test_data():
    with session_factory() as session:
        # 1. Создаем пользователей с описанием
        users = [
            User(username="John Doe", email="jdoe@example.com", description="Постоянный клиент"),
            User(username="Alice Smith", email="alice@example.com", description="Новый клиент"),
            User(username="Bob Johnson", email="bob@example.com", description="VIP клиент"),
            User(username="Carol Davis", email="carol@example.com", description="Корпоративный клиент"),
            User(username="David Wilson", email="david@example.com", description="Частый покупатель")
        ]
        session.add_all(users)
        session.commit()

        # 2. Добавляем адреса
        addresses = []
        for user in users:
            address = Address(
                user_id=user.id,
                street=f"123 {user.username.split()[0]} Street",
                city="New York",
                state="NY",
                zip_code="10001",
                country="USA",
                is_primary=True
            )
            addresses.append(address)
        session.add_all(addresses)
        session.commit()

        # 3. СОЗДАЕМ 5 ЗАКАЗОВ С ИНФОРМАЦИЕЙ О ПРОДУКЦИИ
        products_data = [
            {"name": "Ноутбук", "description": "Мощный игровой ноутбук", "price": 999.99},
            {"name": "Смартфон", "description": "Флагманский смартфон", "price": 799.99},
            {"name": "Наушники", "description": "Беспроводные наушники", "price": 199.99},
            {"name": "Планшет", "description": "Графический планшет", "price": 499.99},
            {"name": "Часы", "description": "Умные часы", "price": 299.99}
        ]

        orders = []
        for i, user in enumerate(users):
            product = products_data[i]
            order = Order(
                user_id=user.id,
                address_id=addresses[i].id,
                product_name=product["name"],
                product_description=product["description"],
                product_price=product["price"],
                quantity=i + 1,
                total_amount=product["price"] * (i + 1),
                status=["pending", "completed", "shipped", "processing", "delivered"][i]
            )
            orders.append(order)

        session.add_all(orders)
        session.commit()
        print("5 заказов с информацией о продукции добавлены!")


