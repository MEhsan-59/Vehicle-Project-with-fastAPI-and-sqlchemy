# main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from logger_setup import logger
from schema import (
    CreateAccountSchema, CreateAccountResponse,
    LoginAccountSchema, TokenResponse, ProfileResponse
)
from account_manager import AccountManager
from account_repository import AccountRepository
from database import get_db
from auth import decode_access_token, create_access_token

app = FastAPI(title="Vehicle Manager API", version="1.0")
security_scheme = HTTPBearer()


def get_account_manager(db: Session = Depends(get_db)) -> AccountManager:
    repo = AccountRepository(db)
    return AccountManager(repo)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    manager: AccountManager = Depends(get_account_manager)
):
    payload = decode_access_token(credentials.credentials)

    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    account = manager.account_repo.get_account_by_id(payload.get("sub"))

    if account is None:
        raise HTTPException(status_code=401, detail="User not found")

    return account


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/create_account", response_model=CreateAccountResponse)
def create_account(data: CreateAccountSchema, manager: AccountManager = Depends(get_account_manager)):
    logger.info("API : Create account.")
    status, msg = manager.create_account(data.user_id, data.user_name, data.password)

    if not status:
        logger.warning(msg)
        if msg == "Account already exists.":
            raise HTTPException(status_code=409, detail=msg)
        raise HTTPException(status_code=400, detail=msg)

    return CreateAccountResponse(status=True, message=msg)


@app.post("/login_account", response_model=TokenResponse)
def login_account(data: LoginAccountSchema, manager: AccountManager = Depends(get_account_manager)):
    logger.info("API : Login Account.")
    status, msg = manager.login_account(data.user_id, data.password)

    if not status:
        logger.warning(msg)
        raise HTTPException(status_code=401, detail=msg)

    token = create_access_token(data.user_id)
    return {"access_token": token, "token_type": "bearer"}


@app.get("/me", response_model=ProfileResponse)
def get_profile(current_user=Depends(get_current_user)):
    return {
        "message": f"Welcome, {current_user.user_name}!",
        "user_id": current_user.user_id,
        "name": current_user.user_name
    }
