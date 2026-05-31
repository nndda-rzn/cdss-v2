"""YOLO class-index <-> data-model enum mapping (verified at seed time)."""
YOLO_NAME_TO_ENUM = {
    "abnormal_heartbeat": "abnormal",
    "history_myocardial_infarction": "homi",
    "myocardial_infarction": "mi",
    "normal": "normal",
}
ENUM_ORDER = ["abnormal", "homi", "mi", "normal"]  # YOLO index order
