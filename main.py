# main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from logger_setup import logger
from schema import (
    CreateAccountSchema, CreateAccountResponse,
    LoginAccountSchema, TokenResponse, ProfileResponse,
    MessageResponse, PartConfigSchema, PartUpdateSchema, PartConfigResponse
)
from account_manager import AccountManager
from account_repository import AccountRepository
from part_manager import PartManager
from part_repository import PartRepository
from database import get_db
from auth import decode_access_token, create_access_token

app = FastAPI(title="Vehicle Manager API", version="2.0")
security_scheme = HTTPBearer()

ERROR_STATUS = {
    "Part already exists.": 409,
    "Part not found.": 404,
}


def raise_http(message: str):
    logger.warning(message)
    if message.startswith("Part is in use"):
        raise HTTPException(status_code=409, detail=message)
    raise HTTPException(status_code=ERROR_STATUS.get(message, 400), detail=message)


def get_account_manager(db: Session = Depends(get_db)) -> AccountManager:
    return AccountManager(AccountRepository(db))


def get_part_manager(db: Session = Depends(get_db)) -> PartManager:
    return PartManager(PartRepository(db))


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


@app.post("/parts", response_model=MessageResponse, status_code=201)
def add_part(
    data: PartConfigSchema,
    manager: PartManager = Depends(get_part_manager),
    current_user=Depends(get_current_user)
):
    logger.info(f"API : Add part ({data.part}).")
    status, msg = manager.add_part_config(
        data.part, data.km_life, data.month_life, data.km_limit, data.day_limit
    )
    if not status:
        raise_http(msg)
    return MessageResponse(status=True, message=msg)


@app.put("/parts/{part}", response_model=MessageResponse)
def update_part_config(
    part: str,
    data: PartUpdateSchema,
    manager: PartManager = Depends(get_part_manager),
    current_user=Depends(get_current_user)
):
    logger.info(f"API : Update part ({part}).")
    status, msg = manager.update_part_config(
        part.strip().lower(), data.km_life, data.month_life, data.km_limit, data.day_limit
    )
    if not status:
        raise_http(msg)
    return MessageResponse(status=True, message=msg)


@app.delete("/parts/{part}", response_model=MessageResponse)
def delete_part_config(
    part: str,
    manager: PartManager = Depends(get_part_manager),
    current_user=Depends(get_current_user)
):
    logger.info(f"API : Delete part ({part}).")
    status, msg = manager.delete_part_config(part.strip().lower())
    if not status:
        raise_http(msg)
    return MessageResponse(status=True, message=msg)


@app.get("/parts", response_model=list[PartConfigResponse])
def get_parts(
    manager: PartManager = Depends(get_part_manager),
    current_user=Depends(get_current_user)
):
    return manager.get_all_parts()
