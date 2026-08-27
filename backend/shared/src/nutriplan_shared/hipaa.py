"""
HIPAA Compliance Stubs for NutriPlan
=====================================

This module provides encryption and de-identification utilities for
Protected Health Information (PHI) fields stored in Postgres and MongoDB.

HIPAA Safe Harbor method (45 CFR §164.514(b)) requires removal or
generalisation of 18 specific identifier categories before data can be
considered de-identified for research or export purposes.

Production deployment requirements:
  - Use AWS KMS, GCP Cloud KMS, or Azure Key Vault for the encryption key
  - Rotate keys annually and log all access in an audit trail
  - Never log PHI — use the `redact_phi` helper before any logging call
  - Enable column-level encryption in Postgres via pgcrypto extension

Usage:
    from nutriplan_shared.hipaa import encrypt_phi, decrypt_phi, redact_phi, DeidentifiedRecord

    # Encrypting PHI before DB write
    encrypted_name = encrypt_phi(user.full_name)

    # Decrypting PHI after DB read (authorised access only)
    plain_name = decrypt_phi(db_row.full_name_encrypted)

    # Safe logging
    logger.info("Processing record: %s", redact_phi({"email": user.email, "calories": 2000}))
"""

import base64
import hashlib
import os
import re
from typing import Any, Optional
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Encryption key management
# ---------------------------------------------------------------------------
# In production, replace this with a KMS call:
#   import boto3
#   kms = boto3.client('kms', region_name='us-east-1')
#   key_data = kms.generate_data_key(KeyId=KMS_KEY_ARN, KeySpec='AES_256')
#   FIELD_ENCRYPTION_KEY = key_data['Plaintext']
# ---------------------------------------------------------------------------
_RAW_KEY = os.getenv("HIPAA_FIELD_ENCRYPTION_KEY", "")
if not _RAW_KEY:
    # Development fallback — deterministic, NOT secure for production
    _RAW_KEY = "dev-only-nutriplan-hipaa-stub-key-change-in-prod"

FIELD_ENCRYPTION_KEY = hashlib.sha256(_RAW_KEY.encode()).digest()  # 32-byte AES-256 key


def _get_cipher():
    """Return an AES-GCM cipher instance (requires `cryptography` package)."""
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        return AESGCM(FIELD_ENCRYPTION_KEY)
    except ImportError:
        return None


def encrypt_phi(plaintext: str) -> str:
    """
    Encrypt a PHI string field using AES-256-GCM.
    Returns a base64-encoded string: nonce || ciphertext.

    Falls back to a reversible base64 stub if `cryptography` is not installed
    (acceptable only in local dev; raises a warning).
    """
    if not plaintext:
        return ""

    cipher = _get_cipher()
    if cipher is None:
        # Stub fallback for dev environments without the cryptography package
        import warnings
        warnings.warn(
            "cryptography package not installed — PHI is base64-encoded only (NOT encrypted). "
            "Install it for real encryption: pip install cryptography",
            RuntimeWarning,
            stacklevel=2,
        )
        return "stub:" + base64.b64encode(plaintext.encode()).decode()

    nonce = os.urandom(12)  # 96-bit nonce for GCM
    ciphertext = cipher.encrypt(nonce, plaintext.encode("utf-8"), None)
    return base64.b64encode(nonce + ciphertext).decode("utf-8")


def decrypt_phi(encrypted: str) -> str:
    """
    Decrypt a PHI string field encrypted by `encrypt_phi`.
    Returns the original plaintext.
    """
    if not encrypted:
        return ""

    # Handle stub fallback
    if encrypted.startswith("stub:"):
        return base64.b64decode(encrypted[5:]).decode("utf-8")

    cipher = _get_cipher()
    if cipher is None:
        raise RuntimeError("Cannot decrypt: cryptography package not installed")

    raw = base64.b64decode(encrypted.encode("utf-8"))
    nonce, ciphertext = raw[:12], raw[12:]
    return cipher.decrypt(nonce, ciphertext, None).decode("utf-8")


# ---------------------------------------------------------------------------
# PHI field registry
# ---------------------------------------------------------------------------
# The 18 HIPAA Safe Harbor identifiers (simplified subset relevant to NutriPlan)
PHI_FIELDS = frozenset({
    "full_name", "name", "first_name", "last_name",
    "email", "email_address",
    "phone", "phone_number",
    "address", "city", "state", "zip_code", "postal_code",
    "date_of_birth", "dob", "birth_date",
    "ssn", "social_security_number",
    "health_plan_id", "account_number", "certificate_number",
    "device_id", "device_serial",
    "ip_address",
    "biometric_data",
    "full_face_photo",
    "medical_record_number",
})

_REDACT_PLACEHOLDER = "[REDACTED]"


def redact_phi(data: dict[str, Any]) -> dict[str, Any]:
    """
    Return a copy of `data` with all PHI fields replaced by [REDACTED].
    Safe to pass to any logger.
    """
    return {
        k: _REDACT_PLACEHOLDER if k.lower() in PHI_FIELDS else v
        for k, v in data.items()
    }


def hash_identifier(value: str, salt: Optional[str] = None) -> str:
    """
    One-way SHA-256 hash of a PHI identifier for pseudonymisation.
    Useful for analytics pipelines that need stable cross-record linkage
    without storing the raw value.

    Example: hash_identifier(user.email) → analytics join key
    """
    combined = (salt or "") + value
    return hashlib.sha256(combined.encode()).hexdigest()


# ---------------------------------------------------------------------------
# De-identification helpers
# ---------------------------------------------------------------------------
_DATE_PATTERN = re.compile(r"\b\d{4}-\d{2}-\d{2}\b|\b\d{2}/\d{2}/\d{4}\b")


def generalise_date(date_str: str) -> str:
    """
    Replace a full date with just the year (Safe Harbor date generalisation).
    '1985-04-15' → '1985'
    """
    match = _DATE_PATTERN.search(date_str)
    if match:
        raw = match.group()
        year = raw[:4] if "-" in raw else raw[-4:]
        return year
    return date_str


class DeidentifiedRecord(BaseModel):
    """
    Pydantic model representing a de-identified user record.
    PHI fields are removed; only aggregate / non-identifying fields are kept
    for analytics, research export, or ML training.
    """
    # Demographics (generalised)
    age_group: str            # e.g. "25-34", "35-44"
    gender: str               # "Male", "Female", "Non-binary", "Prefer not to say"
    region: str               # country/state only — no city or zip
    activity_level: str

    # Health metrics (non-identifying)
    bmi_category: str         # "Underweight", "Normal", "Overweight", "Obese"
    clinical_condition: Optional[str] = None
    goal: Optional[str] = None

    # Engagement (aggregate)
    meals_logged_count: int = 0
    diary_streak_days: int = 0
    plan_adherence_pct: float = 0.0

    @classmethod
    def from_user_profile(cls, profile: dict) -> "DeidentifiedRecord":
        """Build a de-identified record from a raw user profile dict."""
        age = profile.get("age", 0)
        if age < 18:
            age_group = "<18"
        elif age < 25:
            age_group = "18-24"
        elif age < 35:
            age_group = "25-34"
        elif age < 45:
            age_group = "35-44"
        elif age < 55:
            age_group = "45-54"
        else:
            age_group = "55+"

        weight = profile.get("weight_kg", 70)
        height_m = profile.get("height_cm", 170) / 100
        bmi = weight / (height_m ** 2) if height_m > 0 else 0
        if bmi < 18.5:
            bmi_category = "Underweight"
        elif bmi < 25:
            bmi_category = "Normal"
        elif bmi < 30:
            bmi_category = "Overweight"
        else:
            bmi_category = "Obese"

        return cls(
            age_group=age_group,
            gender=profile.get("gender", "Unknown"),
            region=profile.get("region", "IN"),
            activity_level=profile.get("activity_level", "Sedentary"),
            bmi_category=bmi_category,
            clinical_condition=profile.get("clinical_condition"),
            goal=profile.get("goal"),
            meals_logged_count=profile.get("meals_logged_count", 0),
            diary_streak_days=profile.get("diary_streak_days", 0),
            plan_adherence_pct=profile.get("plan_adherence_pct", 0.0),
        )
