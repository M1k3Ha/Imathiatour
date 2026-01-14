from fastapi import FastAPI, Header, HTTPException
from typing import Optional

from .models import AboutMember, LoginRequest, RefreshRequest, TokenResponse
from .data import TEAM_MEMBERS
from .auth import (
    verify_user,
    create_access_token,
    create_refresh_token,
    decode_token,
    require_access_token,
)

app = FastAPI(
    title="Imathiatour API",
    version="1.0.0"
)

@app.get("/about", response_model=list[AboutMember])
def about():
    return TEAM_MEMBERS


@app.post("/api/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    if not verify_user(payload.email, payload.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access = create_access_token(payload.email)
    refresh = create_refresh_token(payload.email)
    return TokenResponse(access_token=access, refresh_token=refresh)


@app.post("/api/auth/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest):
    data = decode_token(payload.refresh_token)
    if data.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Not a refresh token")

    sub = data.get("sub")
    access = create_access_token(sub)
    new_refresh = create_refresh_token(sub)
    return TokenResponse(access_token=access, refresh_token=new_refresh)


# Προσωρινό protected endpoint για τεστ
@app.get("/api/protected")
def protected(authorization: Optional[str] = Header(default=None)):
    user = require_access_token(authorization)
    return {"ok": True, "user": user}
