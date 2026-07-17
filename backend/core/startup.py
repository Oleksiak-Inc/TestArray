from db.session import SessionLocal
from db.models.user_types import UserTypes
from db.models.users import Users
from db.models.permissions import Permissions
from core.permissions import PERMISSIONS
from core.config import settings
from core.security import PasswordHasher


def init_db() -> None:
    """Initialize required reference data.

    Called on application startup.
    """
    db = SessionLocal()
    try:
        print("Initializing database with required reference data...")

        user_types: dict[str, UserTypes] = {}
        for name, description in [("admin", "Admin user"), ("regular", "Regular user")]:
            existing = db.query(UserTypes).filter(UserTypes.name == name).first()
            if not existing:
                existing = UserTypes(name=name, description=description)
                db.add(existing)
            user_types[name] = existing

        db.flush()

        existing_admin = db.query(Users).filter(Users.email == settings.SUPERUSER_LOGIN).first()
        # Always ensure a superuser exists with credentials from settings.
        # If the user exists, update password and user_type if required.
        hashed_pw = PasswordHasher.hash(settings.SUPERUSER_PASSWORD)
        if not existing_admin:
            db.add(
                Users(
                    first_name="Super",
                    last_name="User",
                    email=settings.SUPERUSER_LOGIN,
                    password=hashed_pw,
                    user_type_id=user_types["admin"].id,
                )
            )
        else:
            updated = False
            # ensure user is admin type
            try:
                admin_type_id = user_types["admin"].id
            except Exception:
                admin_type_id = None

            if admin_type_id is not None and existing_admin.user_type_id != admin_type_id:
                existing_admin.user_type_id = admin_type_id
                updated = True

            # update password if it doesn't match the configured one
            if not PasswordHasher.verify(settings.SUPERUSER_PASSWORD, existing_admin.password):
                existing_admin.password = hashed_pw
                updated = True

            if updated:
                db.add(existing_admin)

        print("Adding required permissions...")
        for code, description in PERMISSIONS:
            existing = db.query(Permissions).filter(Permissions.code == code).first()
            if not existing:
                db.add(Permissions(code=code, description=description))

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        print("Database initialization complete.")
        db.close()
