from db.session import SessionLocal
from db.models.user_types import UserTypes


def init_db() -> None:
    """Initialize required reference data.

    Called on application startup.
    """
    db = SessionLocal()
    try:
        # Ensure there is at least a "regular" user type for registrations.
        # Add other base structs here as needed.
        for name, description in [("admin", "Admin user"),("regular", "Regular user")]:
            existing = db.query(UserTypes).filter(UserTypes.name == name).first()
            if not existing:
                db.add(UserTypes(name=name, description=description))
        db.commit()
    finally:
        db.close()
