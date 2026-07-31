"""
tests/test_workbench_routes.py

Flask test-client tests for the Workbench blueprint (server_api/workbench/routes.py).
Operations are pure Python (no subprocess), so these hit the real registry —
only the app-level execute_command/singleton patches from conftest.py apply.
"""

import pytest

from nyxstrike_server import app


@pytest.fixture(scope="module")
def client():
    app.config["TESTING"] = True
    app.config["NYXSTRIKE_API_TOKEN"] = None
    with app.test_client() as c:
        yield c


class TestOperationsEndpoint:
    def test_returns_success_with_categories_and_operations(self, client):
        r = client.get("/api/workbench/operations")
        assert r.status_code == 200
        body = r.get_json()
        assert body["success"] is True
        assert "encoding" in body["categories"]
        assert any(op["id"] == "base64" for op in body["operations"])

    def test_operations_do_not_leak_run_callable(self, client):
        r = client.get("/api/workbench/operations")
        body = r.get_json()
        for op in body["operations"]:
            assert "run" not in op


class TestRunEndpoint:
    def test_success_returns_200_with_output(self, client):
        r = client.post("/api/workbench/run/base64", json={"input": "hello", "mode": "encode"})
        assert r.status_code == 200
        body = r.get_json()
        assert body["success"] is True
        assert body["output"] == "aGVsbG8="

    def test_unknown_operation_returns_200_not_404(self, client):
        # Regression: business-logic failures must stay HTTP 200 with
        # success:false — the frontend's request() helper throws a raw Error
        # for any non-2xx status, bypassing normal success-check handling.
        r = client.post("/api/workbench/run/does_not_exist", json={"input": "x"})
        assert r.status_code == 200
        body = r.get_json()
        assert body["success"] is False
        assert "does_not_exist" in body["error"]

    def test_invalid_input_returns_200_not_400(self, client):
        r = client.post("/api/workbench/run/base64", json={"input": "!!!not valid!!!", "mode": "decode"})
        assert r.status_code == 200
        body = r.get_json()
        assert body["success"] is False
        assert "error" in body

    def test_missing_body_does_not_crash(self, client):
        # No JSON body -> params defaults to {} -> operations treat a missing
        # "input" as an empty string rather than raising, and fall back to
        # their default mode.
        r = client.post("/api/workbench/run/base64")
        assert r.status_code == 200
        body = r.get_json()
        assert body["success"] is True
        assert body["output"] == ""


class TestRunRecipeEndpoint:
    def test_chains_output_into_next_step_input(self, client):
        r = client.post(
            "/api/workbench/run-recipe",
            json={
                "input": "hello",
                "steps": [
                    {"operation_id": "base64", "params": {"mode": "encode"}},
                    {"operation_id": "base64", "params": {"mode": "decode"}},
                ],
            },
        )
        assert r.status_code == 200
        body = r.get_json()
        assert body["success"] is True
        assert body["output"] == "hello"
        assert len(body["steps"]) == 2

    def test_empty_steps_returns_original_input(self, client):
        r = client.post("/api/workbench/run-recipe", json={"input": "unchanged", "steps": []})
        body = r.get_json()
        assert body["success"] is True
        assert body["output"] == "unchanged"

    def test_unknown_operation_mid_recipe_stops_and_reports_200(self, client):
        r = client.post(
            "/api/workbench/run-recipe",
            json={
                "input": "hello",
                "steps": [
                    {"operation_id": "base64", "params": {"mode": "encode"}},
                    {"operation_id": "does_not_exist", "params": {}},
                ],
            },
        )
        assert r.status_code == 200
        body = r.get_json()
        assert body["success"] is False
        assert len(body["steps"]) == 2
        assert body["steps"][0]["output"] == "aGVsbG8="
        assert "error" in body["steps"][1]

    def test_invalid_input_mid_recipe_reports_which_step_failed(self, client):
        r = client.post(
            "/api/workbench/run-recipe",
            json={
                "input": "not valid base64 at all!!!",
                "steps": [{"operation_id": "base64", "params": {"mode": "decode"}}],
            },
        )
        assert r.status_code == 200
        body = r.get_json()
        assert body["success"] is False
        assert body["steps"][0]["operation_id"] == "base64"
        assert "error" in body["steps"][0]
