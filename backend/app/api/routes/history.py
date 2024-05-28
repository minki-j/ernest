from datetime import datetime
from bson.objectid import ObjectId

from fastapi import APIRouter, Form, Query, Body
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.security.oauth2 import OAuth2PasswordBearer

from app.utils.mongodb import (
    fetch_document,
    update_document,
    delete_document,
    fetch_user,
)

from app.langchain.main_graph import langgraph_app
from app.schemas.schemas import Message, Role
from app.langchain.schema import Documents


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    if token != "test1234":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


router = APIRouter()


@router.get("/")
def root(
    token: str = Depends(get_current_user),
):
    return {"message": "/history route working fine"}


@router.post("/getchats")
def get_chats(
    user = Body(...),
    token= Depends(get_current_user),
):
    name = user["name"]
    email = user["email"]
    id = user["id"]
    documents = fetch_user(id, name, email)
    return documents
