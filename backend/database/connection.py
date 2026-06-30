from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./research_assistant.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    Dependency helper that yields a new SQLAlchemy SessionLocal
    and ensures the session is closed after execution.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db() -> None:
    """
    Initializes all database tables mapped to Base models.
    """
    from sqlalchemy import inspect, text
    inspector = inspect(engine)
    if "reports" in inspector.get_table_names():
        columns = [c["name"] for c in inspector.get_columns("reports")]
        if "user_id" in columns:
            print("Migration: reports table has user_id, dropping old tables...")
            with engine.begin() as conn:
                conn.execute(text("DROP TABLE IF EXISTS reports"))
                conn.execute(text("DROP TABLE IF EXISTS users"))
    Base.metadata.create_all(bind=engine)
