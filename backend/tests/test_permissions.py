from uuid import uuid4

from core.permissions import PERMISSIONS
from core.startup import init_db
from db.models.group_permissions import GroupPermissions
from db.models.groups_members import GroupsMembers
from db.models.permissions import Permissions
from db.models.user_groups import UserGroups
from db.models.user_types import UserTypes
from db.models.users import Users
from app.api.utils.auth_dependencies import PermissionChecker


def test_init_db_seeds_permissions_table(db_session):
    init_db()

    seeded_codes = {
        permission.code
        for permission in db_session.query(Permissions).all()
    }

    expected_codes = {code for code, _ in PERMISSIONS}

    assert expected_codes.issubset(seeded_codes)
    assert len(seeded_codes) >= len(expected_codes)


def test_init_db_is_idempotent_on_repeated_runs(db_session):
    init_db()
    first_count = db_session.query(Permissions).count()

    init_db()
    second_count = db_session.query(Permissions).count()

    assert second_count == first_count


def test_self_service_update_is_allowed_without_group_permission(client):
    email = f"self-update-{uuid4().hex}@example.com"
    password = "password123"

    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "first_name": "Self",
            "last_name": "Service",
            "email": email,
            "password": password,
        },
    )
    assert register_response.status_code == 200

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200
    client.cookies.update(login_response.cookies)

    update_response = client.patch(
        "/api/v1/users/me",
        json={"first_name": "Updated"},
    )

    assert update_response.status_code == 200
    assert update_response.json()["first_name"] == "Updated"


def test_regular_user_without_permission_is_forbidden_on_protected_endpoint(client):
    email = f"blocked-{uuid4().hex}@example.com"
    password = "password123"

    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "first_name": "Blocked",
            "last_name": "User",
            "email": email,
            "password": password,
        },
    )
    assert register_response.status_code == 200

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200
    client.cookies.update(login_response.cookies)

    response = client.post(
        "/api/v1/clients/",
        json={"name": "Blocked Client"},
    )

    assert response.status_code == 403


def test_user_has_permission_respects_groups_and_admin_override(db_session):
    regular_type = db_session.query(UserTypes).filter(UserTypes.name == "regular").first()
    admin_type = db_session.query(UserTypes).filter(UserTypes.name == "admin").first()

    if not regular_type:
        regular_type = UserTypes(name="regular", description="Regular user")
        db_session.add(regular_type)
        db_session.commit()
        db_session.refresh(regular_type)

    if not admin_type:
        admin_type = UserTypes(name="admin", description="Admin user")
        db_session.add(admin_type)
        db_session.commit()
        db_session.refresh(admin_type)

    regular_user = Users(
        first_name="Regular",
        last_name="User",
        email="regular-perms@example.com",
        password="secret",
        user_type_id=regular_type.id,
    )
    admin_user = Users(
        first_name="Admin",
        last_name="User",
        email="admin-perms@example.com",
        password="secret",
        user_type_id=admin_type.id,
    )
    db_session.add_all([regular_user, admin_user])
    db_session.commit()
    db_session.refresh(regular_user)
    db_session.refresh(admin_user)

    permission = db_session.query(Permissions).filter(Permissions.code == "clients.read").first()
    assert permission is not None

    group = UserGroups(name="Test Group", created_by_id=regular_user.id, owner_id=regular_user.id)
    db_session.add(group)
    db_session.commit()
    db_session.refresh(group)

    db_session.add(GroupsMembers(group_id=group.id, user_id=regular_user.id))
    db_session.commit()

    assert PermissionChecker(db_session).has_permission(regular_user, "clients.read") is False

    db_session.add(GroupPermissions(group_id=group.id, permission_id=permission.id))
    db_session.commit()

    assert PermissionChecker(db_session).has_permission(regular_user, "clients.read") is True
    assert PermissionChecker(db_session).has_permission(admin_user, "clients.read") is True
