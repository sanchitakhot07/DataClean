import hashlib
import re
import secrets
import mysql.connector

from database import get_connection


# Username rules
USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_]{3,32}$")

# Password rules
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128

# Scrypt configuration
SCRYPT_N = 2**14


def _validate_credentials(username, password):
    """Validate username and password."""

    if not USERNAME_PATTERN.fullmatch(username or ""):
        raise ValueError(
            "Username must be 3-32 letters, numbers, or underscores."
        )

    if not (
        PASSWORD_MIN_LENGTH
        <= len(password or "")
        <= PASSWORD_MAX_LENGTH
    ):
        raise ValueError(
            f"Password must be between "
            f"{PASSWORD_MIN_LENGTH} and "
            f"{PASSWORD_MAX_LENGTH} characters."
        )


def _hash_password(password, salt):
    """Hash password using scrypt."""

    return hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=SCRYPT_N,
        r=8,
        p=1,
        dklen=32,
    )


def register_user(username, password):
    """Register a new user in MySQL."""

    _validate_credentials(username, password)

    username = username.strip().lower()

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        # Check whether username already exists
        cursor.execute(
            "SELECT id FROM users WHERE username = %s",
            (username,)
        )

        existing_user = cursor.fetchone()

        if existing_user is not None:
            return False

        # Create password salt
        salt = secrets.token_bytes(16)

        # Create password hash
        password_hash = _hash_password(
            password,
            salt
        )

        # Insert user
        cursor.execute(
            """
            INSERT INTO users
            (
                username,
                password_salt,
                password_hash
            )
            VALUES (%s, %s, %s)
            """,
            (
                username,
                salt.hex(),
                password_hash.hex()
            )
        )

        connection.commit()

        return True

    except mysql.connector.Error as error:
        if connection:
            connection.rollback()

        raise error

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


def authenticate_user(username, password):
    """Check username and password from MySQL."""

    if not username or not password:
        return False

    if len(password) > PASSWORD_MAX_LENGTH:
        return False

    username = username.strip().lower()

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT password_salt, password_hash
            FROM users
            WHERE username = %s
            """,
            (username,)
        )

        user = cursor.fetchone()

        if user is None:
            return False

        stored_salt = bytes.fromhex(user[0])
        stored_hash = bytes.fromhex(user[1])

        entered_hash = _hash_password(
            password,
            stored_salt
        )

        return secrets.compare_digest(
            entered_hash,
            stored_hash
        )

    except mysql.connector.Error:
        return False

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()