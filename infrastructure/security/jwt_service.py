import base64
import hashlib
import hmac
import json
import os
import time
from typing import Any

from fastapi import HTTPException, status


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


class JwtService:
    def __init__(self):
        self.secret = os.getenv("JWT_SECRET_KEY", "cambiar-esta-clave-en-env")
        self.expiration_minutes = int(os.getenv("JWT_EXPIRATION_MINUTES", "60"))

    def create_token(self, claims: dict[str, Any]) -> str:
        now = int(time.time())
        payload = claims.copy()
        payload["iat"] = now
        payload["exp"] = now + self.expiration_minutes * 60
        header = {"alg": "HS256", "typ": "JWT"}

        header_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode())
        payload_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode())
        signing_input = f"{header_b64}.{payload_b64}".encode()
        signature = hmac.new(self.secret.encode(), signing_input, hashlib.sha256).digest()
        return f"{header_b64}.{payload_b64}.{_b64url_encode(signature)}"

    def verify_token(self, token: str) -> dict[str, Any]:
        try:
            header_b64, payload_b64, signature_b64 = token.split(".")
            signing_input = f"{header_b64}.{payload_b64}".encode()
            expected = hmac.new(self.secret.encode(), signing_input, hashlib.sha256).digest()
            provided = _b64url_decode(signature_b64)
            if not hmac.compare_digest(expected, provided):
                raise ValueError("Firma inválida")
            payload = json.loads(_b64url_decode(payload_b64))
            if int(payload.get("exp", 0)) < int(time.time()):
                raise ValueError("Token expirado")
            return payload
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )
