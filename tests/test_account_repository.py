# tests/test_account_repository.py
def test_create_account_creates_and_returns_account(account_repo):
    account = account_repo.create_account("ihsan", "M. Ihsan", "1234")

    assert account.user_id == "ihsan"
    assert account.user_name == "M. Ihsan"
    assert account.password != "1234"


def test_check_account_exists_true_after_creating(account_repo):
    account_repo.create_account("ihsan", "M. Ihsan", "1234")

    assert account_repo.check_account_exists("ihsan", skip_password_check=True) is not None


def test_check_account_exists_false_when_not_present(account_repo):
    assert account_repo.check_account_exists("ghost", skip_password_check=True) is None


def test_check_account_exists_with_correct_password(account_repo):
    account_repo.create_account("ihsan", "M. Ihsan", "1234")

    assert account_repo.check_account_exists("ihsan", "1234") is not None


def test_check_account_exists_with_wrong_password(account_repo):
    account_repo.create_account("ihsan", "M. Ihsan", "1234")

    assert account_repo.check_account_exists("ihsan", "wrong") is None


def test_get_account_by_id_found(account_repo):
    account_repo.create_account("ihsan", "M. Ihsan", "1234")

    assert account_repo.get_account_by_id("ihsan") is not None


def test_get_account_by_id_not_found(account_repo):
    assert account_repo.get_account_by_id("ghost") is None
