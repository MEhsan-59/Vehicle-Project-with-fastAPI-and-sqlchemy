# account_repository.py
from models import Account
from sqlalchemy.orm import Session
import security


class AccountRepository:

    def __init__(self, database=Session):
        self.db = database

    def create_account(self, user_id, user_name, password):
        hash_password = security.SecurityHelper.hash_password(password)

        account = Account(user_id=user_id, user_name=user_name, password=hash_password)
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)

        return account

    def check_account_exists(self, user_id, password=None, skip_password_check=False):
        account = self.db.query(Account).filter(Account.user_id == user_id).first()
        if not account:
            return None
        if skip_password_check or password is None:
            return account
        if not security.SecurityHelper.verify_password(password, account.password):
            return None
        return account

    def get_account_by_id(self, user_id):
        return self.db.query(Account).filter(Account.user_id == user_id).first()
