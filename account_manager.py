# account_manager.py
from logger_setup import logger


class AccountManager:

    def __init__(self, account_repo):
        self.account_repo = account_repo

    def create_account(self, user_id, user_name, password):
        if self.account_repo.check_account_exists(user_id, skip_password_check=True):
            logger.warning("Account already exists.")
            return False, "Account already exists."

        account = self.account_repo.create_account(user_id, user_name, password)

        if account:
            logger.info("Account Successfully created.")
            return True, "Account Successfully created."

        logger.warning("Account creation failed.")
        return False, "Account creation failed."

    def login_account(self, user_id, password):
        account = self.account_repo.check_account_exists(user_id, password)
        if not account:
            logger.warning("Invalid user_id or password")
            return False, "Invalid user_id or password"

        logger.info("Account login successfully.")
        return True, "Account login successfully."

    def get_account_by_id(self, user_id):
        account = self.account_repo.get_account_by_id(user_id)
        if not account:
            logger.warning("Invalid user id no account found.")
            return False, "Invalid user id no account found.", account
        return True, "Account found.", account
