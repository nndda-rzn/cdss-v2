"""Patient dedup: find likely-duplicate patients before registering a new one.

Names are Fernet-encrypted with a random IV, so the same plaintext yields
different ciphertext and cannot be matched by an equality query (ADR-0015).
Strategy: narrow by the indexed (dob, gender) pair, decrypt the small candidate
set in memory, then fuzzy-match the name with a bounded edit distance.
"""
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.patient import Patient

_MAX_EDIT_DISTANCE = 2


def _levenshtein(a: str, b: str) -> int:
    a, b = a.lower(), b.lower()
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        current = [i]
        for j, cb in enumerate(b, start=1):
            cost = 0 if ca == cb else 1
            current.append(
                min(previous[j] + 1, current[j - 1] + 1, previous[j - 1] + cost)
            )
        previous = current
    return previous[-1]


def find_potential_duplicates(
    session: Session,
    *,
    facility_id: int,
    name: str,
    dob: date,
    gender: str,
) -> list[Patient]:
    """Return live patients at the facility whose name closely matches.

    Candidates are restricted to the same dob and gender (indexed), then the
    decrypted name is compared with a Levenshtein distance threshold.
    """
    candidates = session.scalars(
        select(Patient).where(
            Patient.facility_id == facility_id,
            Patient.dob == dob,
            Patient.gender == gender,
            Patient.deleted_at.is_(None),
        )
    ).all()
    return [
        p
        for p in candidates
        if _levenshtein(p.name_encrypted, name) <= _MAX_EDIT_DISTANCE
    ]
