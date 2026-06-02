"""Tests for admin dashboard stats endpoint."""
from app.core.security.jwt import make_access_token


def _admin_token():
    return make_access_token(user_id=1, role="admin", facility_id=1)


class TestAdminStats:
    def test_stats_returns_all_sections(self, client, seeded_admin, session):
        resp = client.get("/api/admin/stats",
                          headers={"Authorization": f"Bearer {_admin_token()}"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert "users" in data
        assert "facilities" in data
        assert "ai" in data
        assert "audit" in data

    def test_stats_rejects_non_admin(self, client, seeded_admin):
        nurse_token = make_access_token(user_id=2, role="nurse", facility_id=1)
        resp = client.get("/api/admin/stats",
                          headers={"Authorization": f"Bearer {nurse_token}"})
        assert resp.status_code == 403
