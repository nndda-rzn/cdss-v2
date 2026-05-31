"""MRN auto-generator: MRN-{facility_code}-{6-digit zero-padded}.

Sequence is per facility. The next number is derived from the current maximum
suffix among that facility's existing MRNs, so it stays correct even if rows
are deleted (numbers are not reused, since MAX is monotonic for live rows).
"""
from sqlalchemy import Integer, func, select
from sqlalchemy.orm import Session

from app.db.models.patient import Patient

_SEQ_WIDTH = 6
_MAX_SEQ = 10**_SEQ_WIDTH - 1

MRN_GENERATION_EXHAUSTED = "MRN_GENERATION_EXHAUSTED"


def generate_mrn(session: Session, *, facility_id: int, facility_code: str) -> str:
    """Return the next MRN for a facility.

    The numeric suffix is the last 6 characters of the MRN. We take the max of
    the cast suffix among the facility's patients and add one.
    """
    suffix = func.cast(func.substr(Patient.mrn, -_SEQ_WIDTH), Integer)
    current_max = session.scalar(
        select(func.max(suffix)).where(Patient.facility_id == facility_id)
    )
    next_seq = (current_max or 0) + 1
    if next_seq > _MAX_SEQ:
        raise RuntimeError(MRN_GENERATION_EXHAUSTED)
    return f"MRN-{facility_code}-{next_seq:0{_SEQ_WIDTH}d}"
