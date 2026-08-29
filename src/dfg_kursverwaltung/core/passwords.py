from __future__ import annotations

import base64
import hashlib
import hmac
import secrets


ALGORITHM = "scrypt"
FORMAT_VERSION = "v1"

SCRYPT_N = 2**14
SCRYPT_R = 8
SCRYPT_P = 1

SCRYPT_MIN_N = 2**12
SCRYPT_MAX_N = 2**15
SCRYPT_MAX_R = 8
SCRYPT_MAX_P = 4
SCRYPT_MAX_MEMORY = 32 * 1024 * 1024

SALT_LENGTH = 16
KEY_LENGTH = 32

MAX_SALT_LENGTH = 64
MAX_KEY_LENGTH = 64


def hash_password(
    password: str,
) -> str:
    """Erzeugt einen sicheren, gesalzenen Passwort-Hash."""
    _validate_password(password)

    salt = secrets.token_bytes(
        SALT_LENGTH
    )

    derived_key = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=SCRYPT_N,
        r=SCRYPT_R,
        p=SCRYPT_P,
        dklen=KEY_LENGTH,
    )

    salt_b64 = _encode_bytes(salt)
    key_b64 = _encode_bytes(
        derived_key
    )

    return (
        f"{ALGORITHM}"
        f"${FORMAT_VERSION}"
        f"$n={SCRYPT_N}"
        f"$r={SCRYPT_R}"
        f"$p={SCRYPT_P}"
        f"${salt_b64}"
        f"${key_b64}"
    )


def verify_password(
    password: str,
    encoded_hash: str,
) -> bool:
    """Prüft ein Passwort gegen einen gespeicherten Hash."""
    if not isinstance(password, str):
        return False

    try:
        (
            algorithm,
            version,
            n_part,
            r_part,
            p_part,
            salt_b64,
            key_b64,
        ) = encoded_hash.split("$")

        if algorithm != ALGORITHM:
            return False

        if version != FORMAT_VERSION:
            return False

        n = _parse_parameter(
            n_part,
            "n",
        )
        r = _parse_parameter(
            r_part,
            "r",
        )
        p = _parse_parameter(
            p_part,
            "p",
        )

        if not _parameters_are_safe(
            n=n,
            r=r,
            p=p,
        ):
            return False

        salt = _decode_bytes(
            salt_b64
        )
        expected_key = _decode_bytes(
            key_b64
        )

        if not (
            1
            <= len(salt)
            <= MAX_SALT_LENGTH
        ):
            return False

        if not (
            1
            <= len(expected_key)
            <= MAX_KEY_LENGTH
        ):
            return False

        actual_key = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=n,
            r=r,
            p=p,
            dklen=len(expected_key),
        )

    except (
        AttributeError,
        TypeError,
        ValueError,
    ):
        return False

    return hmac.compare_digest(
        actual_key,
        expected_key,
    )


def needs_rehash(
    encoded_hash: str,
) -> bool:
    """Prüft, ob ein Hash mit aktuellen Parametern neu erzeugt werden sollte."""
    try:
        (
            algorithm,
            version,
            n_part,
            r_part,
            p_part,
            _salt_b64,
            _key_b64,
        ) = encoded_hash.split("$")

        n = _parse_parameter(
            n_part,
            "n",
        )
        r = _parse_parameter(
            r_part,
            "r",
        )
        p = _parse_parameter(
            p_part,
            "p",
        )

    except (
        AttributeError,
        TypeError,
        ValueError,
    ):
        return True

    return (
        algorithm != ALGORITHM
        or version != FORMAT_VERSION
        or n != SCRYPT_N
        or r != SCRYPT_R
        or p != SCRYPT_P
    )


def _parameters_are_safe(
    *,
    n: int,
    r: int,
    p: int,
) -> bool:
    if (
        n < SCRYPT_MIN_N
        or n > SCRYPT_MAX_N
    ):
        return False

    if n & (n - 1):
        return False

    if (
        r <= 0
        or r > SCRYPT_MAX_R
    ):
        return False

    if (
        p <= 0
        or p > SCRYPT_MAX_P
    ):
        return False

    estimated_memory = (
        128 * n * r
    )

    return (
        estimated_memory
        <= SCRYPT_MAX_MEMORY
    )


def _validate_password(
    password: str,
) -> None:
    if not isinstance(password, str):
        raise TypeError(
            "Das Passwort muss eine "
            "Zeichenkette sein."
        )

    if not password:
        raise ValueError(
            "Das Passwort darf nicht leer sein."
        )


def _parse_parameter(
    value: str,
    expected_name: str,
) -> int:
    name, separator, number = (
        value.partition("=")
    )

    if (
        separator != "="
        or name != expected_name
    ):
        raise ValueError(
            "Ungültiges Hash-Format."
        )

    parsed = int(number)

    if parsed <= 0:
        raise ValueError(
            "Ungültiger Hash-Parameter."
        )

    return parsed


def _encode_bytes(
    value: bytes,
) -> str:
    return (
        base64.urlsafe_b64encode(value)
        .decode("ascii")
        .rstrip("=")
    )


def _decode_bytes(
    value: str,
) -> bytes:
    padding = (
        "=" * (-len(value) % 4)
    )

    return base64.b64decode(
        value + padding,
        altchars=b"-_",
        validate=True,
    )
