# tests/test_account_manager.py
def test_create_account(account_manager):
    status, msg = account_manager.create_account("Hi", "HI", "1234")

    assert status is True
    assert msg.startswith("Account Successfully created")


def test_create_duplicate_account(account_manager):
    account_manager.create_account("ihsan", "M. Ihsan", "1234")
    status, msg = account_manager.create_account("ihsan", "M. Ihsan", "1234")

    assert status is False
    assert msg == "Account already exists."


def test_login_account_success(account_manager):
    account_manager.create_account("ihsan", "M. Ihsan", "1234")
    status, msg = account_manager.login_account("ihsan", "1234")

    assert status is True
    assert msg == "Account login successfully."


def test_login_account_wrong_password(account_manager):
    account_manager.create_account("ihsan", "M. Ihsan", "1234")
    status, msg = account_manager.login_account("ihsan", "wrong")

    assert status is False
    assert msg == "Invalid user_id or password"


def test_login_account_not_found(account_manager):
    status, msg = account_manager.login_account("ghost", "1234")

    assert status is False
    assert msg == "Invalid user_id or password"


def test_get_account_by_id_found(account_manager):
    account_manager.create_account("ihsan", "M. Ihsan", "1234")
    status, msg, account = account_manager.get_account_by_id("ihsan")

    assert status is True
    assert account.user_id == "ihsan"


def test_get_account_by_id_not_found(account_manager):
    status, msg, account = account_manager.get_account_by_id("ghost")

    assert status is False
    assert msg == "Invalid user id no account found."
    assert account is None
