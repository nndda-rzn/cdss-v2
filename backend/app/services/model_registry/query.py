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
