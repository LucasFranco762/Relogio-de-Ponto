"""Serviços de segurança para credenciais."""

import hashlib
import hmac


class PasswordHasher:
    """Hash seguro usando PBKDF2-HMAC-SHA256 da biblioteca padrão."""

    iterations = 310_000

    def hash(self, password: str) -> str:
        salt = hashlib.sha256(password.encode()).hexdigest()[:32]
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), self.iterations)
        return f"pbkdf2_sha256${self.iterations}${salt}${digest.hex()}"

    def verify(self, password: str, encoded: str) -> bool:
        try:
            algorithm, iterations, salt, expected = encoded.split("$", 3)
            if algorithm != "pbkdf2_sha256":
                return False
            actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), int(iterations))
            return hmac.compare_digest(actual.hex(), expected)
        except (ValueError, TypeError):
            return False
