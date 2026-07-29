"""Workflow / integration-style tests extracted from the original suite."""

from uuid import uuid4

from helpers import _uid


def test_client_with_multiple_projects(db_session, make_client, make_project):
    # create a client and two projects for it
    c = make_client(name=f"C-{_uid()}")
    p1 = make_project(client=c, name=f"P1-{_uid()}")
    p2 = make_project(client=c, name=f"P2-{_uid()}")

    from app.services.client import ClientService

    svc = ClientService(db_session)
    fetched = svc.get_client_with_projects(c.id)
    project_ids = {p.id for p in fetched.projects}
    assert p1.id in project_ids and p2.id in project_ids


def test_test_case_version_lifecycle(db_session, make_scenario, make_status_set, current_user):
    from app.services.test_case import TestCaseService

    s = make_scenario()
    ss = make_status_set()
    svc = TestCaseService(db_session)

    tc, v1 = svc.create_test_case_and_version(
        {"scenario_id": s.id, "status_set_id": ss.id},
        {
            "name": "v1",
            "version": 1,
            "description": "first",
            "steps": "step",
            "expected_result": "ok",
            "release_ready": False,
            "created_by": current_user.id,
        },
    )

    # create a second version via the service helper
    from db.models.test_case_versions import TestCaseVersions

    v2 = svc.add_and_flush(TestCaseVersions(
        test_case_id=tc.id,
        name="v2",
        version=2,
        description="second",
        steps="step2",
        expected_result="ok2",
        release_ready=False,
        created_by=current_user.id,
    ))
    svc.commit()
    svc.refresh(v2)

    versions = svc.get_test_case_with_all_versions(tc.id).versions
    assert any(v.id == v1.id for v in versions)
    assert any(v.id == v2.id for v in versions)

    # update v2 by setting attribute and committing
    v2.description = "updated"
    svc.commit()
    svc.refresh(v2)
    assert v2.description == "updated"

    # delete v1 using service.delete
    svc.delete(v1)
    remaining = svc.get_test_case_with_all_versions(tc.id).versions
    assert all(v.id != v1.id for v in remaining)


def test_full_test_management_workflow(db_session, make_scenario, make_status_set, make_test_suite, current_user):
    from app.services.test_case import TestCaseService
    from app.services.suitcase import SuitcaseService

    s = make_scenario()
    ss = make_status_set()
    ts = make_test_suite()

    tc, v = TestCaseService(db_session).create_test_case_and_version(
        {"scenario_id": s.id, "status_set_id": ss.id},
        {
            "name": "flow",
            "version": 1,
            "description": "flow",
            "steps": "do",
            "expected_result": "ok",
            "release_ready": False,
            "created_by": current_user.id,
        },
    )

    # add to suite via suitcase
    SuitcaseService(db_session).create_suitcase({"test_case_id": tc.id, "test_suite_id": ts.id})

    # verify suite contains the test case
    svc = SuitcaseService(db_session)
    items = svc.get_suitcases_by_test_suite_id(ts.id)
    assert any(i.test_case_id == tc.id for i in items)
