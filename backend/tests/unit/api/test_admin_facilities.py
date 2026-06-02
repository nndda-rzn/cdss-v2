"""Tests for admin facility management endpoints."""
from app.core.security.jwt import make_access_token


def _admin_token():
    return make_access_token(user_id=1, role="admin", facility_id=1)


def _nurse_token():
    return make_access_token(user_id=2, role="nurse", facility_id=1)


class TestAdminFacilitiesList:
    def test_list_facilities(self, client, seeded_admin):
        resp = client.get("/api/admin/facilities",
                          headers={"Authorization": f"Bearer {_admin_token()}"})
        assert resp.status_code == 200
        assert len(resp.get_json()["items"]) >= 1

    def test_list_rejects_non_admin(self, client, seeded_admin):
        resp = client.get("/api/admin/facilities",
                          headers={"Authorization": f"Bearer {_nurse_token()}"})
        assert resp.status_code == 403


class TestAdminFacilitiesCreate:
    def test_create_facility(self, client, seeded_admin):
        resp = client.post("/api/admin/facilities",
                           headers={"Authorization": f"Bearer {_admin_token()}"},
                           json={
                               "name": "RS Contoh",
                               "code": "RS-001",
                               "facility_type": "rs_pratama",
                           })
        assert resp.status_code == 201
        assert resp.get_json()["code"] == "RS-001"


class TestAdminFacilitiesUpdate:
    def test_update_facility(self, client, seeded_admin):
        resp = client.put("/api/admin/facilities/1",
                          headers={"Authorization": f"Bearer {_admin_token()}"},
                          json={"name": "Pusk Updated"})
        assert resp.status_code == 200
        assert resp.get_json()["name"] == "Pusk Updated"

    def test_toggle_facility_active(self, client, seeded_admin):
        resp = client.put("/api/admin/facilities/1",
                          headers={"Authorization": f"Bearer {_admin_token()}"},
                          json={"is_active": False})
        assert resp.status_code == 200
        assert resp.get_json()["is_active"] is False
