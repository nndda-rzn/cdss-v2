"""Integration tests for tuning API endpoints."""
import csv
import json

from app import create_app
from app.core.security.jwt import make_access_token
from app.services.hirescam.config_store import get_config


def app():
    app = create_app()
    app.config["TESTING"] = True
    return app


def client(app):
    return app.test_client()


def _admin_token():
    return make_access_token(user_id=1, role="admin", facility_id=1)


def _auth():
    return {"Authorization": f"Bearer {_admin_token()}"}


def _write_grid(root):
    grid = root / "outputs" / "hirescam_tuning_grid"
    grid.mkdir(parents=True, exist_ok=True)
    summary = grid / "summary.csv"
    with open(summary, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "image_path", "original_size", "input_size", "target_layer",
                "target_layer_info", "target_class_id", "confidence",
                "letterbox_ratio", "letterbox_padding", "config_index",
                "clip_percentile", "smooth_sigma", "top_percent",
                "colormap", "overlay_alpha", "explanation_status", "focus_metric",
            ],
        )
        writer.writeheader()
        writer.writerow({
            "image_path": "x.jpg", "original_size": "[1572, 2213]", "input_size": 1600,
            "target_layer": "last_conv", "target_layer_info": "Conv2d",
            "target_class_id": 3, "confidence": -1.5,
            "letterbox_ratio": 0.72, "letterbox_padding": "{}",
            "config_index": 1, "clip_percentile": 99.0, "smooth_sigma": 0.0,
            "top_percent": 15.0, "colormap": "inferno", "overlay_alpha": 0.45,
            "explanation_status": "good", "focus_metric": 0.63,
        })
    cfg = grid / "config_001"
    cfg.mkdir()
    (cfg / "metadata.json").write_text(json.dumps({"config_index": 1, "focus_metric": 0.63}))
    (cfg / "overlay.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    return grid


class TestTuningGrid:
    def test_get_grid_returns_items(self, client, tmp_path, monkeypatch):
        grid = _write_grid(tmp_path)
        monkeypatch.setattr(
            "app.api.tuning._grid_dir", lambda: grid
        )
        resp = client.get("/api/tuning/grid", headers=_auth())
        assert resp.status_code == 200
        data = resp.get_json()
        assert "items" in data
        assert isinstance(data["items"], list)

    def test_get_grid_has_required_fields(self, client, tmp_path, monkeypatch):
        grid = _write_grid(tmp_path)
        monkeypatch.setattr(
            "app.api.tuning._grid_dir", lambda: grid
        )
        resp = client.get("/api/tuning/grid", headers=_auth())
        data = resp.get_json()
        if data["items"]:
            item = data["items"][0]
            assert "config_index" in item
            assert "input_size" in item
            assert "target_layer" in item
            assert "focus_metric" in item
            assert "explanation_status" in item


class TestTuningConfig:
    def test_get_config_returns_metadata(self, client, tmp_path, monkeypatch):
        grid = _write_grid(tmp_path)
        monkeypatch.setattr(
            "app.api.tuning._grid_dir", lambda: grid
        )
        resp = client.get("/api/tuning/grid/1", headers=_auth())
        assert resp.status_code == 200
        data = resp.get_json()
        assert "config_index" in data
        assert data["config_index"] == 1

    def test_get_config_not_found(self, client, tmp_path, monkeypatch):
        grid = _write_grid(tmp_path)
        monkeypatch.setattr(
            "app.api.tuning._grid_dir", lambda: grid
        )
        resp = client.get("/api/tuning/grid/99999", headers=_auth())
        assert resp.status_code == 404


class TestTuningImage:
    def test_serves_image(self, client, tmp_path, monkeypatch):
        grid = _write_grid(tmp_path)
        monkeypatch.setattr(
            "app.api.tuning._grid_dir", lambda: grid
        )
        resp = client.get("/api/tuning/grid/1/images/overlay.png")
        assert resp.status_code == 200
        assert resp.content_type == "image/png"

    def test_image_not_found(self, client, tmp_path, monkeypatch):
        grid = _write_grid(tmp_path)
        monkeypatch.setattr(
            "app.api.tuning._grid_dir", lambda: grid
        )
        resp = client.get("/api/tuning/grid/1/images/nonexistent.png")
        assert resp.status_code == 404

    def test_config_not_found(self, client, tmp_path, monkeypatch):
        grid = _write_grid(tmp_path)
        monkeypatch.setattr(
            "app.api.tuning._grid_dir", lambda: grid
        )
        resp = client.get("/api/tuning/grid/99999/images/overlay.png")
        assert resp.status_code == 404

    def test_path_traversal_blocked(self, client, tmp_path, monkeypatch):
        grid = _write_grid(tmp_path)
        monkeypatch.setattr(
            "app.api.tuning._grid_dir", lambda: grid
        )
        resp = client.get("/api/tuning/grid/1/images/../../etc/passwd")
        assert resp.status_code in (400, 404)


class TestTuningActiveConfig:
    def test_get_active_returns_defaults(self, client, app):
        with app.app_context():
            resp = client.get("/api/tuning/active", headers=_auth())
            assert resp.status_code == 200
            data = resp.get_json()
            assert data["colormap"] == "inferno"
            assert data["input_size"] == 1600

    def test_apply_requires_auth(self, client, tmp_path, monkeypatch):
        grid = _write_grid(tmp_path)
        monkeypatch.setattr(
            "app.api.tuning._grid_dir", lambda: grid
        )
        resp = client.post("/api/tuning/apply/1")
        assert resp.status_code in (401, 403)

    def test_apply_not_found(self, client, app, tmp_path, monkeypatch):
        grid = _write_grid(tmp_path)
        monkeypatch.setattr(
            "app.api.tuning._grid_dir", lambda: grid
        )
        with app.app_context():
            from app.core.security.password import hash_password
            from app.db.models.facility import HealthcareFacility
            from app.db.models.user import User
            from app.extensions import db

            db.session.add(HealthcareFacility(id=1, name="P", code="P1", facility_type="puskesmas"))
            db.session.add(User(
                id=1, name="admin", email="admin@x.id",
                password_hash=hash_password("StrongPass1", rounds=4),
                role="admin", facility_id=1,
            ))
            db.session.commit()

            login_payload = {"email": "admin@x.id", "password": "StrongPass1"}
            login_resp = client.post("/api/auth/login", json=login_payload)
            token = login_resp.get_json()["access_token"]
            resp = client.post(
                "/api/tuning/apply/99999",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 404

    def test_apply_saves_config(self, client, app, tmp_path, monkeypatch):
        grid = _write_grid(tmp_path)
        monkeypatch.setattr(
            "app.api.tuning._grid_dir", lambda: grid
        )
        with app.app_context():
            from app.core.security.password import hash_password
            from app.db.models.facility import HealthcareFacility
            from app.db.models.user import User
            from app.extensions import db

            db.session.add(HealthcareFacility(id=1, name="P", code="P1", facility_type="puskesmas"))
            db.session.add(User(
                id=1, name="admin", email="admin@x.id",
                password_hash=hash_password("StrongPass1", rounds=4),
                role="admin", facility_id=1,
            ))
            db.session.commit()

            login_payload = {"email": "admin@x.id", "password": "StrongPass1"}
            login_resp = client.post("/api/auth/login", json=login_payload)
            token = login_resp.get_json()["access_token"]
            resp = client.post(
                "/api/tuning/apply/1",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code == 200
            data = resp.get_json()
            assert data["status"] == "applied"
            assert data["config"]["colormap"] == "inferno"
            assert data["config"]["smooth_sigma"] == 0.0

            # Verify it persists
            cfg = get_config(db.session)
            assert cfg.colormap == "inferno"
            assert cfg.smooth_sigma == 0.0


class TestTuningRBAC:
    def test_grid_requires_admin(self, client, tmp_path, monkeypatch):
        grid = _write_grid(tmp_path)
        monkeypatch.setattr("app.api.tuning._grid_dir", lambda: grid)
        nurse_token = make_access_token(user_id=1, role="nurse", facility_id=1)
        resp = client.get("/api/tuning/grid",
                          headers={"Authorization": f"Bearer {nurse_token}"})
        assert resp.status_code == 403

    def test_grid_allows_admin(self, client, tmp_path, monkeypatch):
        grid = _write_grid(tmp_path)
        monkeypatch.setattr("app.api.tuning._grid_dir", lambda: grid)
        resp = client.get("/api/tuning/grid", headers=_auth())
        assert resp.status_code == 200

    def test_active_requires_admin(self, client, monkeypatch):
        nurse_token = make_access_token(user_id=1, role="nurse", facility_id=1)
        resp = client.get("/api/tuning/active",
                          headers={"Authorization": f"Bearer {nurse_token}"})
        assert resp.status_code == 403
