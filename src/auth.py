
import base64
import binascii
import hashlib
import hmac
import json
import re
import secrets
import sqlite3
import time

from contextlib import contextmanager
from uuid import uuid4

import streamlit as st

from src.config import BASE_DIR


# =====================================================
# 1. AUTHENTICATION CONFIGURATION
# =====================================================

AUTH_DB_PATH = BASE_DIR / "users.db"

HASH_NAME = "sha256"
ITERATIONS = 600_000
SALT_SIZE = 16
HASH_SIZE = 32

TOKEN_EXPIRY_SECONDS = 7 * 24 * 60 * 60

MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 1024

EMAIL_PATTERN = re.compile(
    r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
)


# =====================================================
# 2. DATABASE CONNECTION
# =====================================================

def get_auth_connection():
    """Create a connection to the authentication database."""

    connection = sqlite3.connect(
        AUTH_DB_PATH,
        timeout=30,
    )

    connection.execute("PRAGMA foreign_keys = ON")

    return connection


@contextmanager
def managed_auth_connection():
    """
    Manage database transactions and always close connections.
    """

    connection = get_auth_connection()

    try:
        with connection:
            yield connection

    finally:
        connection.close()


def initialize_auth_db():
    """Create the users table if it does not exist."""

    with managed_auth_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


# =====================================================
# 3. INPUT VALIDATION
# =====================================================

def normalize_email(email):
    """Normalize and validate an email address."""

    if not isinstance(email, str):
        return None

    email = email.strip().lower()

    if len(email) > 254:
        return None

    if not EMAIL_PATTERN.fullmatch(email):
        return None

    return email


def validate_password(password):
    """Validate password type and length."""

    if not isinstance(password, str):
        return False

    return (
        MIN_PASSWORD_LENGTH
        <= len(password)
        <= MAX_PASSWORD_LENGTH
    )


# =====================================================
# 4. PASSWORD HASHING
# =====================================================

def hash_password(password):
    """Hash a password using PBKDF2-HMAC-SHA256."""

    if not validate_password(password):
        raise ValueError("Invalid password length.")

    salt = secrets.token_bytes(SALT_SIZE)

    password_hash = hashlib.pbkdf2_hmac(
        HASH_NAME,
        password.encode("utf-8"),
        salt,
        ITERATIONS,
        dklen=HASH_SIZE,
    )

    return password_hash.hex(), salt.hex()


def verify_password(password, stored_hash, stored_salt):
    """Safely verify a password against its stored hash."""

    if not isinstance(password, str):
        return False

    if not isinstance(stored_hash, str):
        return False

    if not isinstance(stored_salt, str):
        return False

    try:
        salt = bytes.fromhex(stored_salt)
        expected_hash = bytes.fromhex(stored_hash)

        if len(salt) != SALT_SIZE:
            return False

        if len(expected_hash) != HASH_SIZE:
            return False

        calculated_hash = hashlib.pbkdf2_hmac(
            HASH_NAME,
            password.encode("utf-8"),
            salt,
            ITERATIONS,
            dklen=HASH_SIZE,
        )

        return hmac.compare_digest(
            calculated_hash,
            expected_hash,
        )

    except (ValueError, TypeError, UnicodeEncodeError):
        return False


# =====================================================
# 5. USER REGISTRATION
# =====================================================

def create_user(email, password):
    """Register a new user."""

    email = normalize_email(email)

    if email is None:
        return {
            "success": False,
            "message": "Please enter a valid email address.",
        }

    if not validate_password(password):
        return {
            "success": False,
            "message": (
                "Password must contain between "
                "8 and 1024 characters."
            ),
        }

    password_hash, salt = hash_password(password)

    user_id = str(uuid4())

    try:
        with managed_auth_connection() as connection:
            connection.execute(
                """
                INSERT INTO users (
                    user_id,
                    email,
                    password_hash,
                    salt
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    user_id,
                    email,
                    password_hash,
                    salt,
                ),
            )

        return {
            "success": True,
            "user_id": user_id,
            "email": email,
            "message": "Account created successfully.",
        }

    except sqlite3.IntegrityError:
        return {
            "success": False,
            "message": "An account with this email already exists.",
        }


# =====================================================
# 6. USER LOGIN
# =====================================================

def authenticate_user(email, password):
    """Authenticate a user using email and password."""

    email = normalize_email(email)

    if email is None or not isinstance(password, str):
        return None

    with managed_auth_connection() as connection:
        user = connection.execute(
            """
            SELECT user_id, email, password_hash, salt
            FROM users
            WHERE email = ?
            """,
            (email,),
        ).fetchone()

    if user is None:
        return None

    user_id, stored_email, stored_hash, stored_salt = user

    if not verify_password(
        password,
        stored_hash,
        stored_salt,
    ):
        return None

    return {
        "user_id": user_id,
        "email": stored_email,
    }


# =====================================================
# 7. TOKEN SECRET VALIDATION
# =====================================================

def get_token_secret():
    """
    Retrieve and validate the authentication signing secret.

    The secret must contain at least 32 UTF-8 bytes.
    """

    try:
        secret = st.secrets["auth_token_secret"]

    except Exception as error:
        raise RuntimeError(
            "Missing auth_token_secret in Streamlit secrets."
        ) from error

    if not isinstance(secret, str):
        raise RuntimeError(
            "auth_token_secret must be a string."
        )

    secret = secret.strip()

    if len(secret.encode("utf-8")) < 32:
        raise RuntimeError(
            "auth_token_secret must contain at least 32 bytes."
        )

    return secret


# =====================================================
# 8. AUTHENTICATION TOKEN CREATION
# =====================================================

def create_auth_token(user_id, email):
    """Create a signed authentication token."""

    if not isinstance(user_id, str) or not user_id.strip():
        raise ValueError("Invalid user ID.")

    email = normalize_email(email)

    if email is None:
        raise ValueError("Invalid email address.")

    payload = {
        "user_id": user_id,
        "email": email,
        "exp": int(time.time()) + TOKEN_EXPIRY_SECONDS,
    }

    payload_json = json.dumps(
        payload,
        separators=(",", ":"),
    ).encode("utf-8")

    payload_encoded = base64.urlsafe_b64encode(
        payload_json
    ).decode("utf-8").rstrip("=")

    secret = get_token_secret()

    signature = hmac.new(
        secret.encode("utf-8"),
        payload_encoded.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    signature_encoded = base64.urlsafe_b64encode(
        signature
    ).decode("utf-8").rstrip("=")

    return f"{payload_encoded}.{signature_encoded}"


# =====================================================
# 9. AUTHENTICATION TOKEN VERIFICATION
# =====================================================

def verify_auth_token(token):
    """Verify token signature, expiry, payload and user account."""

    if not isinstance(token, str) or not token:
        return None

    try:
        parts = token.split(".")

        if len(parts) != 2:
            return None

        payload_encoded, signature_encoded = parts

        if not payload_encoded or not signature_encoded:
            return None

        secret = get_token_secret()

        received_signature = base64.b64decode(
            signature_encoded
            + "=" * (-len(signature_encoded) % 4),
            altchars=b"-_",
            validate=True,
        )

        expected_signature = hmac.new(
            secret.encode("utf-8"),
            payload_encoded.encode("utf-8"),
            hashlib.sha256,
        ).digest()

        if not hmac.compare_digest(
            expected_signature,
            received_signature,
        ):
            return None

        payload_json = base64.b64decode(
            payload_encoded
            + "=" * (-len(payload_encoded) % 4),
            altchars=b"-_",
            validate=True,
        )

        payload = json.loads(
            payload_json.decode("utf-8")
        )

        if not isinstance(payload, dict):
            return None

        user_id = payload.get("user_id")
        email = payload.get("email")
        expiry = payload.get("exp")

        if not isinstance(user_id, str) or not user_id.strip():
            return None

        normalized_email = normalize_email(email)

        if normalized_email is None:
            return None

        if type(expiry) is not int:
            return None

        # Expired tokens must be rejected.
        if expiry <= int(time.time()):
            return None

        with managed_auth_connection() as connection:
            user = connection.execute(
                """
                SELECT user_id, email
                FROM users
                WHERE user_id = ? AND email = ?
                """,
                (
                    user_id,
                    normalized_email,
                ),
            ).fetchone()

        if user is None:
            return None

        return {
            "user_id": user[0],
            "email": user[1],
        }

    except (
        ValueError,
        TypeError,
        KeyError,
        json.JSONDecodeError,
        binascii.Error,
        UnicodeDecodeError,
        sqlite3.Error,
    ):
        return None
