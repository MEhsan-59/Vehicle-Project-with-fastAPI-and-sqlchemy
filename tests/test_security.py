# tests/test_security.py
from security import SecurityHelper


def test_hash_is_not_plain_password():
    assert SecurityHelper.hash_password("12345678") != "12345678"


def test_hash_is_salted():
    assert SecurityHelper.hash_password("12345678") != SecurityHelper.hash_password("12345678")


def test_verify_correct_password():
    hashed = SecurityHelper.hash_password("12345678")
    assert SecurityHelper.verify_password("12345678", hashed) is True


def test_verify_wrong_password():
    hashed = SecurityHelper.hash_password("12345678")
    assert SecurityHelper.verify_password("wrong", hashed) is False
