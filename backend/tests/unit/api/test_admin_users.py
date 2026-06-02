"""Tests for admin user management endpoints."""
from app.core.security.jwt import make_access_token
from app.db.models.user import User


def _admin_token():
    return make_access_token(user_id=1, role="admin", facility_id=1)


def _nurse_token():
    return make_access_token(user_id=2, role="nurse", facility_id=1)


class TestAdminUsersList:
    def test_list_users_returns_all(self, client, seeded_admin):
        resp = client.get("/api/admin/users",
                          headers={"Authorization": f"Bearer {_admin_token()}"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert "items" in data
        assert len(data["items"]) >= 1

    def test_list_users_rejects_non_admin(self, client, seeded_admin):
        resp = client.get("/api/admin/users",
                          headers={"Authorization": f"Bearer {_nurse_token()}"})
        assert resp.status_code == 403


class TestAdminUsersCreate:
    def test_create_user(self, client, seeded_admin):
        resp = client.post("/api/admin/users",
                           headers={"Authorization": f"Bearer {_admin_token()}"},
                           json={
                               "name": "New Doc",
                               "email": "new@doc.local",
                               "password": "Secret123!",
                               "role": "clinician",
                               "facility_id": 1,
                           })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["email"] == "new@doc.local"
        assert data["role"] == "clinician"

    def test_create_user_rejects_duplicate_email(self, client, seeded_admin):
        resp = client.post("/api/admin/users",
                           headers={"Authorization": f"Bearer {_admin_token()}"},
                           json={
                               "name": "Dup",
                               "email": "admin@x.id",
                               "password": "Secret123!",
                               "role": "clinician",
                               "facility_id": 1,
                           })
        assert resp.status_code == 409


class TestAdminUsersUpdate:
    def test_update_user_role(self, client, seeded_admin, session):
        # Create a nurse to update
        nurse = User(
            name="Nurse", email="nurse@x.id",
            password_hash="hash", role="nurse",  # noqa: S106
            facility_id=1, is_active=True,
        )
        session.add(nurse)
        session.commit()

        resp = client.put(f"/api/admin/users/{nurse.id}",
                          headers={"Authorization": f"Bearer {_admin_token()}"},
                          json={"role": "clinician"})
        assert resp.status_code == 200
        assert resp.get_json()["role"] == "clinician"

    def test_toggle_user_active(self, client, seeded_admin, session):
        nurse = User(
            name="Nurse2", email="nurse2@x.id",
            password_hash="hash", role="nurse",  # noqa: S106
            facility_id=1, is_active=True,
        )
        session.add(nurse)
        session.commit()

        resp = client.put(f"/api/admin/users/{nurse.id}",
                          headers={"Authorization": f"Bearer {_admin_token()}"},
                          json={"is_active": False})
        assert resp.status_code == 200
        assert resp.get_json()["is_active"] is False
