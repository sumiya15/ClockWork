"""Salted credential hashing shared by seeding and backend login."""
import hashlib
import hmac
import secrets

DEMO_PASSWORD = "ClockWork-Demo-Only-2026!"


def hash_password(password):
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1, maxmem=64*1024*1024)
    return f"scrypt$16384$8$1${salt.hex()}${digest.hex()}"


def verify_password(password, encoded):
    try:
        algorithm, n, r, p, salt, expected = encoded.split("$")
        if (algorithm, n, r, p) != ("scrypt", "16384", "8", "1"):
            return False
        digest = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=int(n), r=int(r), p=int(p), maxmem=64*1024*1024)
        return hmac.compare_digest(digest.hex(), expected)
    except (ValueError, TypeError):
        return False
