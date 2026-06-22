from sqlalchemy import create_engine
from core.config import settings
from sqlalchemy.engine import make_url

database_url = str(settings.DATABASE_URL)
url = make_url(database_url)
engine_kwargs = {"future": True}
if url.drivername.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs.update(
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
        pool_pre_ping=True,
    )

engine = create_engine(database_url, **engine_kwargs)