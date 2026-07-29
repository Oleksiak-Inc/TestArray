from datetime import datetime, timezone
from typing import Optional

from fastapi import Cookie, Depends, Path
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.utils.http_errors import HttpError
from app.services.session import SessionService
from app.services.users import UserService
from db.models.devices import Devices
from db.models.executions import Executions
from db.models.group_permissions import GroupPermissions
from db.models.groups_members import GroupsMembers
from db.models.permissions import Permissions
from db.models.project_members import ProjectMembers
from db.models.project_role_permissions import ProjectRolePermissions
from db.models.project_roles import ProjectRoles
from db.models.runs import Runs
from db.models.users import Users
from db.session import get_db


class GlobalPermissionChecker:
    def __init__(self, db: Session):
        self.db = db

    def has_permission(self, user: Users, permission_code: str) -> bool:
        if not user:
            return False
        group_ids = select(GroupsMembers.group_id).where(GroupsMembers.user_id == user.id)
        return self.db.query(GroupPermissions).join(
            Permissions,
            GroupPermissions.permission_id == Permissions.id,
        ).filter(
            GroupPermissions.group_id.in_(group_ids),
            Permissions.code == permission_code,
        ).first() is not None

    def require_permission(self, user: Users, permission_code: str) -> None:
        if not self.has_permission(user, permission_code):
            HttpError.forbidden()


class LocalPermissionChecker:
    def __init__(self, db: Session):
        self.db = db

    def has_permission(self, user: Users, project_id: int, permission_code: str) -> bool:
        if not user:
            return False
        member = self.db.query(ProjectMembers).filter(
            ProjectMembers.project_id == project_id,
            ProjectMembers.user_id == user.id,
        ).first()
        if not member or member.role_id is None:
            return False
        return self.db.query(ProjectRolePermissions).join(
            Permissions,
            ProjectRolePermissions.permission_id == Permissions.id,
        ).filter(
            ProjectRolePermissions.role_id == member.role_id,
            Permissions.code == permission_code,
            Permissions.scope == 'local',
        ).first() is not None

    def require_permission(self, user: Users, project_id: int, permission_code: str) -> None:
        if not self.has_permission(user, project_id, permission_code):
            HttpError.forbidden()


class SessionAuthenticator:
    def __init__(self, db: Session):
        self.db = db

    def resolve_user(self, session_secret: str) -> Users:
        session = SessionService(self.db).get_session(session_secret)
        if not session:
            HttpError.unauthorized()

        ended_at = session.ended_at
        if ended_at.tzinfo is None:
            ended_at = ended_at.replace(tzinfo=timezone.utc)
        if ended_at <= datetime.now(timezone.utc):
            HttpError.unauthorized('Session expired')

        user = UserService(self.db).get_user_by_id(session.user_id)
        if not user or not user.active or not user.password:
            HttpError.unauthorized()
        return user


def get_current_user(session: str | None = Cookie(None), db: Session = Depends(get_db)) -> Users:
    if not session:
        HttpError.unauthorized()
    return SessionAuthenticator(db).resolve_user(session)


def permission_required(permission_code: str):
    def dependency(current_user: Users = Depends(get_current_user), db: Session = Depends(get_db)) -> Users:
        GlobalPermissionChecker(db).require_permission(current_user, permission_code)
        return current_user
    return dependency


def local_permission_required(permission_code: str, project_id_param: str = 'project_id'):
    def dependency(
        current_user: Users = Depends(get_current_user),
        db: Session = Depends(get_db),
        project_id: int = Path(..., alias=project_id_param),
    ) -> Users:
        LocalPermissionChecker(db).require_permission(current_user, project_id, permission_code)
        return current_user
    return dependency


def resolve_project_id_from_execution(execution_id: int, db: Session = Depends(get_db)) -> int:
    execution = db.query(Executions).join(Runs, Executions.run_id == Runs.id).filter(
        Executions.id == execution_id
    ).first()
    if not execution:
        HttpError.not_found('Execution not found')
    return execution.run.project_id


def resolve_project_id_from_run(run_id: int, db: Session = Depends(get_db)) -> int:
    run = db.query(Runs).filter(Runs.id == run_id).first()
    if not run:
        HttpError.not_found('Run not found')
    return run.project_id


def resolve_project_id_from_device(device_id: int, db: Session = Depends(get_db)) -> int:
    device = db.query(Devices).filter(Devices.id == device_id).first()
    if not device:
        HttpError.not_found('Device not found')
    return device.project_id


def local_permission_required_via_execution(permission_code: str):
    def dependency(
        current_user: Users = Depends(get_current_user),
        db: Session = Depends(get_db),
        project_id: int = Depends(resolve_project_id_from_execution),
    ) -> Users:
        LocalPermissionChecker(db).require_permission(current_user, project_id, permission_code)
        return current_user
    return dependency


def local_permission_required_via_run(permission_code: str):
    def dependency(
        current_user: Users = Depends(get_current_user),
        db: Session = Depends(get_db),
        project_id: int = Depends(resolve_project_id_from_run),
    ) -> Users:
        LocalPermissionChecker(db).require_permission(current_user, project_id, permission_code)
        return current_user
    return dependency


def local_permission_required_via_device(permission_code: str):
    def dependency(
        current_user: Users = Depends(get_current_user),
        db: Session = Depends(get_db),
        project_id: int = Depends(resolve_project_id_from_device),
    ) -> Users:
        LocalPermissionChecker(db).require_permission(current_user, project_id, permission_code)
        return current_user
    return dependency


def assert_can_assign_role(db: Session, assigner: Users, project_id: int, target_role_id: int) -> None:
    assigner_membership = db.query(ProjectMembers).filter(
        ProjectMembers.project_id == project_id,
        ProjectMembers.user_id == assigner.id,
    ).first()
    if not assigner_membership or assigner_membership.role_id is None:
        HttpError.forbidden('You have no role on this project')
    assigner_role = db.query(ProjectRoles).filter(ProjectRoles.id == assigner_membership.role_id).first()
    target_role = db.query(ProjectRoles).filter(ProjectRoles.id == target_role_id).first()
    if not target_role or not assigner_role or target_role.rank >= assigner_role.rank:
        HttpError.forbidden('Cannot assign a role at or above your own rank')