"""Security primitives.

Two distinct keys with distinct lifecycles:
- JWT signing key: from env JWT_SECRET_KEY. Rotatable. Leak = session forgery.
- Encryption master key: from secrets/master.key. NEVER rotate without a
  re-encrypt batch. Leak = full PHI compromise.

Never read the master key for JWT signing or vice versa.
"""
