from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from config import database
from models import users
from auth import (
    verify_password, create_access_token, hash_password,
    get_current_user, require_admin, TokenData
)

router = APIRouter(prefix="/api/auth", tags=["auth"])

class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str | None = None
    role: str = "viewer"

class ChangePassword(BaseModel):
    old_password: str
    new_password: str

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    query = users.select().where(users.c.username == form_data.username)
    user = await database.fetch_one(query)
    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user["is_active"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")
    token = create_access_token({"sub": user["id"], "username": user["username"], "role": user["role"]})
    return {"access_token": token, "token_type": "bearer", "role": user["role"], "full_name": user["full_name"]}

@router.get("/me")
async def me(current_user: TokenData = Depends(get_current_user)):
    query = users.select().where(users.c.id == current_user.user_id)
    user = await database.fetch_one(query)
    return {"id": user["id"], "username": user["username"], "full_name": user["full_name"], "role": user["role"]}

@router.post("/users", dependencies=[Depends(require_admin)])
async def create_user(body: UserCreate):
    if body.role not in ("admin", "editor", "viewer"):
        raise HTTPException(status_code=400, detail="Invalid role")
    query = users.insert().values(
        username=body.username,
        password_hash=hash_password(body.password),
        full_name=body.full_name,
        role=body.role,
    )
    user_id = await database.execute(query)
    return {"id": user_id, "username": body.username, "role": body.role}

@router.get("/users", dependencies=[Depends(require_admin)])
async def list_users():
    query = users.select().order_by(users.c.id)
    rows = await database.fetch_all(query)
    return [{"id": r["id"], "username": r["username"], "full_name": r["full_name"],
             "role": r["role"], "is_active": r["is_active"], "created_at": str(r["created_at"])} for r in rows]

@router.patch("/users/{user_id}", dependencies=[Depends(require_admin)])
async def update_user(user_id: int, body: dict):
    allowed = {"role", "is_active", "full_name"}
    update_data = {k: v for k, v in body.items() if k in allowed}
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields to update")
    await database.execute(users.update().where(users.c.id == user_id).values(**update_data))
    return {"ok": True}

@router.post("/change-password")
async def change_password(body: ChangePassword, current_user: TokenData = Depends(get_current_user)):
    user = await database.fetch_one(users.select().where(users.c.id == current_user.user_id))
    if not verify_password(body.old_password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Old password incorrect")
    await database.execute(
        users.update().where(users.c.id == current_user.user_id)
        .values(password_hash=hash_password(body.new_password))
    )
    return {"ok": True}
