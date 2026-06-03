"""Unit tests for HiResCAM orchestrator."""
import os
import tempfile
import uuid
from datetime import date
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from PIL import Image

from app.db.models.ai_analysis import AIAnalysis
from app.db.models.ecg_study import ECGStudy
from app.db.models.encounter import Encounter
from app.db.models.model_metadata import ModelMetadata
from app.db.models.patient import Patient
from app.services.hirescam.config import HiResCAMConfig
from app.services.hirescam.orchestrate import generate_artifacts


@pytest.fixture
def dummy_image():
    """Create a dummy ECG report image."""
    fd, path = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    arr = np.random.randint(200, 255, (100, 100, 3), dtype=np.uint8)
    # Put some dark lines as simulated ECG signal
    arr[30:70, 10:90, :] = 50
    Image.fromarray(arr, mode="RGB").save(path)
    yield path
    if os.path.exists(path):
        os.unlink(path)


def test_generate_artifacts_with_roi_crop(session, seeded_admin, dummy_image):
    # Setup database records (facility and user id=1 are created by seeded_admin)
    p = Patient(
        id=uuid.uuid4(), facility_id=1, mrn="MRN-P1-000001",
        name_encrypted="Budi", dob=date(1965, 3, 12), gender="male",
    )
    session.add(p)
    session.flush()
    
    e = Encounter(patient_id=p.id, facility_id=1, attending_user_id=1)
    session.add(e)
    session.flush()

    study = ECGStudy(
        encounter_id=e.id,
        patient_id=p.id,
        study_uid="test-uid-1",
        image_original_path=os.path.basename(dummy_image),
        image_quality_status="good",
        image_quality_score=0.9,
        image_quality_metrics_json={},
        recorded_by_user_id=1,
    )
    session.add(study)
    
    model = ModelMetadata(
        model_name="yolov8n-cls",
        model_version="v1.0",
        architecture="YOLOv8n",
        task_type="classification",
        input_size=1600,
        model_file_path="yolov8n_cls/best.pt",
        model_checksum="checksum",
        model_size_mb=2.0,
        class_names_json=["abnormal", "homi", "mi", "normal"],
        is_active=True,
    )
    session.add(model)
    session.flush()

    analysis = AIAnalysis(
        ecg_study_id=study.id,
        model_metadata_id=model.id,
        predicted_class="mi",
        confidence_score=0.85,
        probability_json={},
        inference_time_ms=10,
        device_used="cpu",
        status="success",
    )
    session.add(analysis)
    session.flush()

    config = HiResCAMConfig(
        use_roi_crop=True,
        roi_x1=0.1,
        roi_y1=0.2,
        roi_x2=0.9,
        roi_y2=0.8,
        use_signal_mask=True,
    )

    # Mock generator_v2 and load_model
    dummy_heatmap = np.random.rand(60, 80).astype(np.float32)
    fake_lb_params = MagicMock()
    fake_lb_params.orig_h = 60
    fake_lb_params.orig_w = 80
    fake_lb_params.ratio = 1.0
    fake_lb_params.pad_top = 0
    fake_lb_params.pad_bottom = 0
    fake_lb_params.pad_left = 0
    fake_lb_params.pad_right = 0

    with patch("app.services.hirescam.orchestrate.load_model") as mock_load, \
         patch("app.services.hirescam.orchestrate.generate_hirescam_v2") as mock_gen:
        
        mock_load.return_value = MagicMock()
        mock_gen.return_value = (dummy_heatmap, fake_lb_params, {})

        artifact = generate_artifacts(
            session,
            analysis=analysis,
            storage_root=Path(os.path.dirname(dummy_image)),
            model_dir=Path("/dummy/model/dir"),
            config=config,
        )

        assert artifact is not None
        assert artifact.ai_analysis_id == analysis.id
        assert artifact.explanation_status in ("good", "diffuse", "off-target", "low-confidence")

        # Verify that generate_hirescam_v2 was called with a cropped temporary path
        called_args = mock_gen.call_args[0]
        called_image_path = called_args[1]
        assert called_image_path != dummy_image
        assert "ecg_crop_" in called_image_path
        # Verify the temp crop file is deleted by the orchestrator
        assert not os.path.exists(called_image_path)
