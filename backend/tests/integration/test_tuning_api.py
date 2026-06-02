"""Integration tests for tuning API endpoints."""
from app import create_app


def app():
    app = create_app()
    app.config["TESTING"] = True
    return app


def client(app):
    return app.test_client()


class TestTuningGrid:
    def test_get_grid_returns_items(self, client):
        resp = client.get("/api/tuning/grid")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "items" in data
        assert isinstance(data["items"], list)

    def test_get_grid_has_required_fields(self, client):
        resp = client.get("/api/tuning/grid")
        data = resp.get_json()
        if data["items"]:
            item = data["items"][0]
            assert "config_index" in item
            assert "input_size" in item
            assert "target_layer" in item
            assert "focus_metric" in item
            assert "explanation_status" in item


class TestTuningConfig:
    def test_get_config_returns_metadata(self, client):
        resp = client.get("/api/tuning/grid/1")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "config_index" in data
        assert data["config_index"] == 1

    def test_get_config_not_found(self, client):
        resp = client.get("/api/tuning/grid/99999")
        assert resp.status_code == 404


class TestTuningImage:
    def test_serves_image(self, client):
        resp = client.get("/api/tuning/grid/1/images/overlay.png")
        assert resp.status_code == 200
        assert resp.content_type == "image/png"

    def test_image_not_found(self, client):
        resp = client.get("/api/tuning/grid/1/images/nonexistent.png")
        assert resp.status_code == 404

    def test_config_not_found(self, client):
        resp = client.get("/api/tuning/grid/99999/images/overlay.png")
        assert resp.status_code == 404

    def test_path_traversal_blocked(self, client):
        resp = client.get("/api/tuning/grid/1/images/../../etc/passwd")
        assert resp.status_code in (400, 404)
