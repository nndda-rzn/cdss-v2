# ADR-0015: Patient deduplication strategy

- Status: Accepted
- Date: 2026-05-31
- Deciders: Maintainer
- Related: data-model-and-phi-design.md, sprint-2a-clinical-context

## Context

Patient identity fields are protected as PHI. The full NIK is stored only as an
HMAC-SHA256 hash (`nik_hash`, irreversible) and the name is stored Fernet-
encrypted (`name_encrypted`) with a random IV, so the same plaintext produces
different ciphertext on every write. NIK is optional at registration (many
Puskesmas patients arrive without a KTP), so it cannot be the sole dedup key.

This makes the usual "look up an existing patient by name" query impossible:
- `WHERE name_encrypted = encrypt('Budi')` never matches (random IV).
- `WHERE nik_hash = ?` only works when the incoming registration includes a NIK.

We still need to warn a registrar when a similar patient may already exist, to
avoid duplicate medical records.

## Decision

Deduplicate in two stages, narrowing on indexed quasi-identifiers first, then
matching the decrypted name in memory:

1. Query candidates by the indexed `(dob, gender)` pair, excluding soft-deleted
   rows, scoped to the facility.
2. Decrypt `name_encrypted` for that small candidate set in memory.
3. Compare the incoming name with a bounded Levenshtein edit distance (<= 2).

When NIK is present, the partial unique index `uq_patient_facility_nik`
(`UNIQUE WHERE nik_hash IS NOT NULL`) still hard-rejects exact NIK duplicates at
the facility (409 `PATIENT_NIK_DUPLICATE`). The fuzzy stage is an advisory
suggestion the registrar can override with `?confirm_new=true`.

## Options Considered

### Option A - dob+gender index then in-memory fuzzy match (chosen)
- Pros: Keeps Fernet's random-IV security (no frequency analysis leak); candidate
  set is tiny (same dob+gender at one facility), so decrypting in memory is cheap;
  works whether or not NIK is supplied.
- Cons: Misses duplicates when dob or gender was mistyped; not a global search.

### Option B - Deterministic/searchable encryption for name (e.g. AES-SIV)
- Pros: Enables direct equality lookup on the encrypted name.
- Cons: Same plaintext yields same ciphertext, leaking frequency/equality
  information across the dataset - a real weakening of PHI protection for a
  marginal UX gain. Rejected.

### Option C - Blind index (HMAC of normalized name)
- Pros: Allows exact-match lookup without revealing plaintext.
- Cons: Only matches exact normalized names (no typo tolerance), adds another
  stored identifier to manage, and still leaks equality. Deferred; revisit only
  if dataset growth makes the in-memory scan too slow.

## Consequences

- Positive: PHI stays strongly encrypted; dedup needs no extra stored identifier;
  behavior is deterministic and easy to test.
- Negative: Dedup is facility-scoped and cannot catch duplicates hidden behind a
  mistyped dob or gender. Registrars retain MRN and (when present) NIK lookups as
  exact alternatives.
- Risks: If a single (dob, gender) bucket at a facility ever grows very large, the
  in-memory decrypt+compare cost grows with it. Acceptable for primary-care
  volumes; revisit with Option C if needed.

## Notes

Implemented in `backend/app/services/patient/dedup.py`. The Levenshtein helper is
a small inline implementation (no external dependency).
