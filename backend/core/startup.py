from db.session import SessionLocal
from db.models.users import Users
from db.models.permissions import Permissions
from db.models.user_groups import UserGroups
from db.models.groups_members import GroupsMembers
from db.models.group_permissions import GroupPermissions
from db.models.project_roles import ProjectRoles
from db.models.project_role_permissions import ProjectRolePermissions
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

        print("Initializing required reference data...")

        print("Adding required permissions...")
        for code, description, scope in PERMISSIONS:
            existing = db.query(Permissions).filter(Permissions.code == code).first()
            if not existing:
                db.add(Permissions(code=code, description=description, scope=scope))

        db.flush()

        LOCAL_ROLE_BUNDLES = {
            'tester': (
                0,
                [
                    'projects.read',
                    'runs.read',
                    'devices.read',
                    'executions.read',
                    'executions.write',
                    'executions.retest',
                    'attachments.read',
                    'attachments.write',
                ],
            ),
            'test_lead': (
                1,
                [
                    'projects.read',
                    'project_members.read',
                    'project_members.write',
                    'runs.read',
                    'runs.write',
                    'devices.read',
                    'devices.write',
                    'executions.read',
                    'executions.write',
                    'executions.create_matrix',
                    'executions.retest',
                    'attachments.read',
                    'attachments.write',
                ],
            ),
            'test_manager': (
                2,
                [
                    'projects.read',
                    'project_members.read',
                    'project_members.write',
                    'runs.read',
                    'runs.write',
                    'devices.read',
                    'devices.write',
                    'executions.read',
                    'executions.write',
                    'executions.create_matrix',
                    'executions.retest',
                    'executions.delete',
                    'attachments.read',
                    'attachments.write',
                ],
            ),
        }

        for name, (rank, perm_codes) in LOCAL_ROLE_BUNDLES.items():
            role = db.query(ProjectRoles).filter(ProjectRoles.name == name).first()
            if not role:
                role = ProjectRoles(name=name, description=f"{name.replace('_', ' ').title()}", rank=rank)
                db.add(role)
                db.flush()
            else:
                role.rank = rank
            existing_perm_ids = {rp.permission_id for rp in role.role_permissions}
            for perm_code in perm_codes:
                perm = db.query(Permissions).filter(Permissions.code == perm_code, Permissions.scope == 'local').first()
                if not perm:
                    raise RuntimeError(f"Missing local permission {perm_code}")
                if perm.id not in existing_perm_ids:
                    db.add(ProjectRolePermissions(role_id=role.id, permission_id=perm.id))

        db.flush()

        superadmin_group = db.query(UserGroups).filter(UserGroups.name == 'superadmin').first()

        existing_system_user = db.query(Users).filter(Users.email == 'system').first()
        
        if not existing_system_user:
            existing_system_user = Users(
                first_name='System',
                last_name='Account',
                email='system',
                password=None,
                active=True,
            )
            db.add(existing_system_user)
            db.flush()

        else:
            if existing_system_user.password is not None:
                existing_system_user.password = None
                db.add(existing_system_user)

        existing_admin = db.query(Users).filter(Users.email == settings.SUPERUSER_LOGIN).first()
        hashed_pw = PasswordHasher.hash(settings.SUPERUSER_PASSWORD)
        if not existing_admin:
            existing_admin = Users(
                first_name='Super',
                last_name='User',
                email=settings.SUPERUSER_LOGIN,
                password=hashed_pw,
                active=True,
            )
            db.add(existing_admin)
            db.flush()
        else:
            updated = False
            if not PasswordHasher.verify(settings.SUPERUSER_PASSWORD, existing_admin.password):
                existing_admin.password = hashed_pw
                updated = True
            if updated:
                db.add(existing_admin)

        if not superadmin_group:
            superadmin_group = UserGroups(
                name='superadmin',
                owner_id=existing_admin.id,
                created_by_id=existing_admin.id,
            )
            db.add(superadmin_group)
            db.flush()

        all_global_perms = db.query(Permissions).filter(Permissions.scope == 'global').all()
        existing_gp_ids = {gp.permission_id for gp in superadmin_group.group_permissions}
        for perm in all_global_perms:
            if perm.id not in existing_gp_ids:
                db.add(GroupPermissions(group_id=superadmin_group.id, permission_id=perm.id))

        membership = db.query(GroupsMembers).filter(
            GroupsMembers.group_id == superadmin_group.id,
            GroupsMembers.user_id == existing_admin.id,
        ).first()
        if not membership:
            db.add(GroupsMembers(group_id=superadmin_group.id, user_id=existing_admin.id))

        system_permissions = db.query(Permissions).filter(
            Permissions.code.in_(['sessions.read', 'sessions.delete'])
        ).all()
        if system_permissions:
            system_group = db.query(UserGroups).filter(UserGroups.name == 'system').first()
            if not system_group:
                system_group = UserGroups(name='system', owner_id=existing_admin.id, created_by_id=existing_admin.id)
                db.add(system_group)
                db.flush()
            for perm in system_permissions:
                existing_gp = db.query(GroupPermissions).filter(
                    GroupPermissions.group_id == system_group.id,
                    GroupPermissions.permission_id == perm.id,
                ).first()
                if not existing_gp:
                    db.add(GroupPermissions(group_id=system_group.id, permission_id=perm.id))
            membership = db.query(GroupsMembers).filter(
                GroupsMembers.group_id == system_group.id,
                GroupsMembers.user_id == existing_system_user.id,
            ).first()
            if not membership:
                db.add(GroupsMembers(group_id=system_group.id, user_id=existing_system_user.id))

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        print("Database initialization complete.")
        db.close()
