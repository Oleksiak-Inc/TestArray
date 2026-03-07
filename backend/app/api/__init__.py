from fastapi import APIRouter
from .v1 import (
    attachment,
    auth,
    client,
    device,
    execution,
    project,
    resolution,
    run,
    scenario,
    status_set,
    status,
    suitcase,
    test_case_version,
    test_case,
    test_suite,
    user_group,
    user_type,
    users,
)

api_router = APIRouter()

api_router.include_router(attachment.router)
api_router.include_router(auth.router)
api_router.include_router(client.router)
api_router.include_router(device.router)
api_router.include_router(execution.router)
api_router.include_router(project.router)
api_router.include_router(resolution.router)
api_router.include_router(run.router)
api_router.include_router(scenario.router)
api_router.include_router(status_set.router)
api_router.include_router(status.router)
api_router.include_router(suitcase.router)
api_router.include_router(test_case_version.router)
api_router.include_router(test_case.router)
api_router.include_router(test_suite.router)
api_router.include_router(user_group.router)
api_router.include_router(user_type.router)
api_router.include_router(users.router)