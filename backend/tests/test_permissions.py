from uuid import uuid4

import pytest

from core.permissions import PERMISSIONS
from core.startup import init_db
from db.models.group_permissions import GroupPermissions
from db.models.groups_members import GroupsMembers
from db.models.permissions import Permissions
from db.models.user_groups import UserGroups
from db.models.users import Users
from app.api.utils.auth_dependencies import GlobalPermissionChecker
from app.services.group_permission import GroupPermissionService


def test_init_db_seeds_permissions_table(db_session):
    init_db()

    seeded_codes = {
        permission.code
        for permission in db_session.query(Permissions).all()
    }

    expected_codes = {code for code, _, _ in PERMISSIONS}

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
    # Create two users: regular and admin. Admin will be added to a superadmin group.
    regular_user = Users(first_name="Regular", last_name="User", email=f"regular-{uuid4().hex}@example.com", password="secret")
    admin_user = Users(first_name="Admin", last_name="User", email=f"admin-{uuid4().hex}@example.com", password="secret")
    db_session.add_all([regular_user, admin_user])
    db_session.commit()
    db_session.refresh(regular_user)
    db_session.refresh(admin_user)

    permission = db_session.query(Permissions).filter(Permissions.code == "clients.read").first()
    assert permission is not None

    # Create a test group for the regular user and grant the permission
    group = UserGroups(name=f"Test Group {uuid4().hex}", created_by_id=regular_user.id, owner_id=regular_user.id)
    db_session.add(group)
    db_session.commit()
    db_session.refresh(group)

    db_session.add(GroupsMembers(group_id=group.id, user_id=regular_user.id))
    db_session.commit()

    assert GlobalPermissionChecker(db_session).has_permission(regular_user, "clients.read") is False

    db_session.add(GroupPermissions(group_id=group.id, permission_id=permission.id))
    db_session.commit()

    assert GlobalPermissionChecker(db_session).has_permission(regular_user, "clients.read") is True

    # Now create a superadmin group, give it all global perms, and add admin_user
    super_group = db_session.query(UserGroups).filter(UserGroups.name == "superadmin").first()
    if not super_group:
        super_group = UserGroups(name="superadmin", created_by_id=admin_user.id, owner_id=admin_user.id)
        db_session.add(super_group)
        db_session.commit()
        db_session.refresh(super_group)

    all_global_perms = db_session.query(Permissions).filter(Permissions.scope == "global").all()
    existing_gp_ids = {gp.permission_id for gp in super_group.group_permissions}
    for perm in all_global_perms:
        if perm.id not in existing_gp_ids:
            db_session.add(GroupPermissions(group_id=super_group.id, permission_id=perm.id))
    db_session.commit()

    db_session.add(GroupsMembers(group_id=super_group.id, user_id=admin_user.id))
    db_session.commit()

    assert GlobalPermissionChecker(db_session).has_permission(admin_user, "clients.read") is True


def test_assign_multiple_permissions_assigns_all_requested_permissions(db_session):
    user = Users(
        first_name="Bulk",
        last_name="Permissions",
        email=f"bulk-permissions-{uuid4().hex}@example.com",
        password="secret",
    )
    db_session.add(user)
    db_session.commit()

    group = UserGroups(name=f"Bulk group {uuid4().hex}", created_by_id=user.id, owner_id=user.id)
    permissions = [
        Permissions(code=f"bulk.permission.{uuid4().hex}", description="Test permission", scope="global")
        for _ in range(2)
    ]
    db_session.add_all([group, *permissions])
    db_session.commit()

    assignments = GroupPermissionService(db_session).assign_multiple_permissions(
        group.id, [permission.id for permission in permissions]
    )

    assert [assignment.permission_id for assignment in assignments] == [
        permission.id for permission in permissions
    ]
    assert db_session.query(GroupPermissions).filter(
        GroupPermissions.group_id == group.id
    ).count() == 2


def test_assign_multiple_permissions_is_atomic_when_assignment_exists(db_session):
    user = Users(
        first_name="Atomic",
        last_name="Permissions",
        email=f"atomic-permissions-{uuid4().hex}@example.com",
        password="secret",
    )
    db_session.add(user)
    db_session.commit()

    group = UserGroups(name=f"Atomic group {uuid4().hex}", created_by_id=user.id, owner_id=user.id)
    permissions = [
        Permissions(code=f"atomic.permission.{uuid4().hex}", description="Test permission", scope="global")
        for _ in range(2)
    ]
    db_session.add_all([group, *permissions])
    db_session.commit()
    db_session.add(GroupPermissions(group_id=group.id, permission_id=permissions[0].id))
    db_session.commit()

    with pytest.raises(ValueError, match="already assigned"):
        GroupPermissionService(db_session).assign_multiple_permissions(
            group.id, [permission.id for permission in permissions]
        )

    assert db_session.query(GroupPermissions).filter(
        GroupPermissions.group_id == group.id
    ).count() == 1
