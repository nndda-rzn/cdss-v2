"""Tests for GET /api/models endpoint."""
from app.core.security.jwt import make_access_token
from app.db.models.model_metadata import ModelMetadata


def _admin_token():
    return make_access_token(user_id=1, role="admin", facility_id=1)


def _seed_model(session):
    m = ModelMetadata(
        model_name="resnet50",
        model_version="1.0",
        architecture="ResNet50",
        task_type="classification",
        input_size=224,
        model_file_path="models/resnet50.pt",
        model_checksum="abc123",
        model_size_mb=45.0,
        class_names_json=["normal", "abnormal"],
        threshold_config_json={"abnormal": 0.5},
        is_active=True,
    )
    session.add(m)
    session.commit()
    return m


class TestListModels:
    def test_returns_active_models(self, client, seeded_admin, session):
        _seed_model(session)
        resp = client.get(
            "/api/models",
            headers={"Authorization": f"Bearer {_admin_token()}"},
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert "items" in data
        assert len(data["items"]) >= 1
        assert data["items"][0]["model_name"] == "resnet50"
        assert data["items"][0]["architecture"] == "ResNet50"

    def test_empty_when_no_models(self, client, seeded_admin):
        resp = client.get(
            "/api/models",
            headers={"Authorization": f"Bearer {_admin_token()}"},
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert "items" in data
        assert len(data["items"]) == 0

    def test_rejects_unauthenticated(self, client, seeded_admin):
        resp = client.get("/api/models")
        assert resp.status_code in (401, 422)
