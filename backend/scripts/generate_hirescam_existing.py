"""Generate HiResCAM artifacts for existing AIAnalysis rows missing them.

Run after the generator bug fix to backfill HiResCAM for studies analyzed
before the fix was deployed.
"""
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.ai_analysis import AIAnalysis
from app.paths import MODEL_DIR, STORAGE_DIR, default_database_url
from app.services.hirescam.orchestrate import generate_for_study


def main() -> None:
    from app.db.engine import create_db_engine

    engine = create_db_engine(default_database_url())
    with Session(engine) as s:
        # Find studies with success analyses
        studies_with_success = list(
            s.scalars(
                select(AIAnalysis.ecg_study_id)
                .where(AIAnalysis.status == "success")
                .distinct()
            ).all()
        )

        print(f"Studies with success analyses: {len(studies_with_success)}")

        total_artifacts = 0
        for study_id in studies_with_success:
            artifacts = generate_for_study(
                s,
                study_id=study_id,
                storage_root=Path(STORAGE_DIR),
                model_dir=Path(MODEL_DIR),
            )
            s.commit()
            total_artifacts += len(artifacts)
            print(f"  Study {study_id}: generated {len(artifacts)} artifacts")

        print(
            f"\nTotal: {total_artifacts} artifacts generated across "
            f"{len(studies_with_success)} studies"
        )


if __name__ == "__main__":
    main()
