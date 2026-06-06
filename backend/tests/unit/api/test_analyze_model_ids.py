"""Tests for POST /analyze — model_ids parameter acceptance."""
import uuid
from datetime import date
from unittest.mock import patch

from app.core.security.jwt import make_access_token
from app.db.models.ecg_study import ECGStudy
from app.db.models.encounter import Encounter
from app.db.models.patient import Patient


def _clinician_token():
    return make_access_token(user_id=1, role="clinical", facility_id=1)


def _seed_encounter_and_study(session):
    """Seed minimal records so the endpoint reaches analyze_study."""
    patient = Patient(
        id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        facility_id=1,
        mrn="MRN-001",
        name_encrypted="Pt",
        dob=date(2000, 1, 1),
        gender="male",
    )
    session.add(patient)
    session.flush()

    encounter = Encounter(
        id=1,
        patient_id=patient.id,
        facility_id=1,
        attending_user_id=1,
    )
    session.add(encounter)
    session.flush()

    study = ECGStudy(
        id=1,
        encounter_id=1,
        patient_id=patient.id,
        study_uid="uid-1",
        image_original_path="img.png",
        image_quality_status="good",
        image_quality_score=0.9,
        recorded_by_user_id=1,
    )
    session.add(study)
    session.commit()
    return study


class TestAnalyzeModelIds:
    def test_no_body_backward_compatible(self, client, seeded_admin, session):
        """Omitting body still works — model_ids defaults to None."""
        _seed_encounter_and_study(session)
        with patch("app.api.ai_analysis.analyze_study", return_value=[]):
            resp = client.post(
                "/api/encounters/1/ecg-studies/1/analyze",
                headers={"Authorization": f"Bearer {_clinician_token()}"},
            )
        assert resp.status_code == 201

    def test_empty_body_backward_compatible(self, client, seeded_admin, session):
        """Empty JSON body also works."""
        _seed_encounter_and_study(session)
        with patch("app.api.ai_analysis.analyze_study", return_value=[]):
            resp = client.post(
                "/api/encounters/1/ecg-studies/1/analyze",
                json={},
                headers={"Authorization": f"Bearer {_clinician_token()}"},
            )
        assert resp.status_code == 201

    def test_with_model_ids_list(self, client, seeded_admin, session):
        """Passing model_ids list forwards it to analyze_study."""
        _seed_encounter_and_study(session)
        with patch("app.api.ai_analysis.analyze_study") as mock_analyze:
            mock_analyze.return_value = []
            resp = client.post(
                "/api/encounters/1/ecg-studies/1/analyze",
                json={"model_ids": [3, 7]},
                headers={"Authorization": f"Bearer {_clinician_token()}"},
            )
        assert resp.status_code == 201
        # Verify model_ids was forwarded
        _, kwargs = mock_analyze.call_args
        assert kwargs["model_ids"] == [3, 7]

    def test_invalid_model_ids_type_returns_400(self, client, seeded_admin):
        """Non-list model_ids should be rejected with 400."""
        resp = client.post(
            "/api/encounters/1/ecg-studies/1/analyze",
            json={"model_ids": "not-a-list"},
            headers={"Authorization": f"Bearer {_clinician_token()}"},
        )
        assert resp.status_code == 400
        data = resp.get_json()
        assert "model_ids" in data["error"]

    def test_empty_model_ids_list_falls_back_to_all(
        self, client, seeded_admin, session
    ):
        """Empty list should be forwarded as-is (fallback handled in query layer)."""
        _seed_encounter_and_study(session)
        with patch("app.api.ai_analysis.analyze_study") as mock_analyze:
            mock_analyze.return_value = []
            resp = client.post(
                "/api/encounters/1/ecg-studies/1/analyze",
                json={"model_ids": []},
                headers={"Authorization": f"Bearer {_clinician_token()}"},
            )
        assert resp.status_code == 201
        _, kwargs = mock_analyze.call_args
        assert kwargs["model_ids"] == []
