import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple
import bcrypt
from jose import JWTError, jwt

from app.core.config import settings


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    # Truncate password if > 72 bytes to avoid bcrypt limit
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    pwd_bytes = plain_password.encode("utf-8")[:72]
    hashed_bytes = hashed_password.encode("utf-8")
    try:
        return bcrypt.checkpw(pwd_bytes, hashed_bytes)
    except Exception:
        return False


def create_access_token(
    subject: str,
    role: str,
    extra_claims: Optional[Dict[str, Any]] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a signed JWT access token."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode: Dict[str, Any] = {
        "sub": str(subject),
        "role": str(role),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "type": "access",
    }
    if extra_claims:
        to_encode.update(extra_claims)

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: str) -> Tuple[str, str, datetime]:
    """
    Create a refresh token and return (raw_token, token_hash, expires_at).
    Stores only the SHA-256 hash in the database to prevent token leakage.
    """
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
        "type": "refresh",
        # Random salt in payload
        "jti": hashlib.sha256(f"{subject}:{now.isoformat()}:{settings.SECRET_KEY}".encode()).hexdigest(),
    }
    raw_token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    return raw_token, token_hash, expires_at


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        raise ValueError(f"Invalid or expired token: {str(e)}")


def hash_token_string(token: str) -> str:
    """Calculate SHA-256 of raw token for lookup."""
    return hashlib.sha256(token.encode()).hexdigest()


def compute_sha256(data: str) -> str:
    """Compute standard SHA-256 hash."""
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def compute_audit_hash(
    prev_hash: str,
    actor_id: Optional[str],
    action: str,
    entity_type: str,
    entity_id: str,
    timestamp_iso: str,
    metadata: Any,
) -> str:
    """
    Compute cryptographic SHA-256 hash for an audit log entry in the chain.
    Chain links: prev_hash -> current_hash
    """
    meta_str = json.dumps(metadata, sort_keys=True, default=str) if metadata is not None else "{}"
    raw = f"{prev_hash}|{actor_id or 'SYSTEM'}|{action}|{entity_type}|{entity_id}|{timestamp_iso}|{meta_str}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
