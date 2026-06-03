"""Query the model registry: list active models that run on analyze."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.model_metadata import ModelMetadata


def list_active_models(session: Session) -> list[ModelMetadata]:
    return list(
        session.scalars(
            select(ModelMetadata)
            .where(ModelMetadata.is_active.is_(True))
            .order_by(ModelMetadata.id)
        ).all()
    )


def list_models_by_ids(session: Session, model_ids: list[int]) -> list[ModelMetadata]:
    """Return active models whose IDs are in *model_ids*.

    If *model_ids* is empty, fall back to all active models (backward compat).
    """
    if not model_ids:
        return list_active_models(session)
    return list(
        session.scalars(
            select(ModelMetadata)
            .where(ModelMetadata.is_active.is_(True), ModelMetadata.id.in_(model_ids))
            .order_by(ModelMetadata.id)
        ).all()
    )
