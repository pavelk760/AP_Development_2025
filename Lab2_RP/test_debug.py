"""
try:
    # Попробуем все возможные способы импорта
    print("=== Тест импорта SQLAlchemy ===")

    import sqlalchemy

    print(f"✅ SQLAlchemy установлен, версия: {sqlalchemy.__version__}")

    # Способ 1 - для версий 2.0+
    try:
        from sqlalchemy.orm import DeclarativeBase

        print("✅ DeclarativeBase доступен (SQLAlchemy 2.0+)")
    except ImportError as e:
        print(f"❌ DeclarativeBase не доступен: {e}")
except ImportError as e:
    print(f"❌ SQLAlchemy не установлен: {e}")
"""

import sqlalchemy
import alembic

print(f"SQLAlchemy version: {sqlalchemy.__version__}")
print(f"Alembic version: {alembic.__version__}")