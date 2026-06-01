import base64
import hashlib
import hmac
import os


class PasswordHasher:
    iterations = 120_000

    def hash(self, password: str) -> str:
        salt = os.urandom(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, self.iterations)
        return f"pbkdf2_sha256${self.iterations}${base64.b64encode(salt).decode()}${base64.b64encode(digest).decode()}"

    def verify(self, password: str, password_hash: str) -> bool:
        try:
            algorithm, iterations, salt_b64, digest_b64 = password_hash.split("$", 3)
            if algorithm != "pbkdf2_sha256":
                return False
            salt = base64.b64decode(salt_b64)
            expected = base64.b64decode(digest_b64)
            actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, int(iterations))
            return hmac.compare_digest(actual, expected)
        except Exception:
            return False
