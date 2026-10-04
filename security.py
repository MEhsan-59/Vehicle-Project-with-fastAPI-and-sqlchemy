# security.py
import bcrypt


class SecurityHelper:
    @staticmethod
    def hash_password(password: str) -> str:
        pwd_bytes = password.encode("utf-8")[:72]
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(pwd_bytes, salt)
        return hashed_password.decode("utf-8")

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        pwd_bytes = password.encode("utf-8")[:72]
        hashed_bytes = hashed.encode("utf-8")
        return bcrypt.checkpw(pwd_bytes, hashed_bytes)
