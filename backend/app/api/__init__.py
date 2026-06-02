"""Blueprint registration."""
from flask import Flask


def register_blueprints(app: Flask) -> None:
    from app.api.admin import admin_bp
    from app.api.ai_analysis import bp as ai_analysis_bp
    from app.api.auth import bp as auth_bp
    from app.api.clinical_context import bp as clinical_context_bp
    from app.api.dashboard import bp as dashboard_bp
    from app.api.ecg_studies import bp as ecg_studies_bp
    from app.api.encounters import bp as encounters_bp
    from app.api.health import bp as health_bp
    from app.api.hirescam import bp as hirescam_bp
    from app.api.patient_consent import bp as patient_consent_bp
    from app.api.patient_history import bp as patient_history_bp
    from app.api.patients import bp as patients_bp
    from app.api.search import bp as search_bp
    from app.api.tuning import bp as tuning_bp
    from app.api.uploads import bp as uploads_bp
    from app.api.vital_signs import bp as vital_signs_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(patient_consent_bp)
    app.register_blueprint(patient_history_bp)
    app.register_blueprint(encounters_bp)
    app.register_blueprint(clinical_context_bp)
    app.register_blueprint(vital_signs_bp)
    app.register_blueprint(ecg_studies_bp)
    app.register_blueprint(ai_analysis_bp)
    app.register_blueprint(hirescam_bp)
    app.register_blueprint(uploads_bp)
    app.register_blueprint(tuning_bp)
    app.register_blueprint(admin_bp)
