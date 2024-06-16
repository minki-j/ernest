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
    fetch_review,
    fetch_reviews_by_user_id,
    delete_reviews_by_user_id,
    add_new_user,
    add_vendor
)

from app.langchain.main_graph import langgraph_app
from app.schemas.schemas import (
    Message,
    Role,
    Review,
    User,
    Vendor,
    State,
    ParallelState,
)
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
    print("===>API CALL: db/ route called")
    return {"message": "/history route working fine"}


@router.post("/getReview")
def get_review(
    token= Depends(get_current_user),
    review_id: str = Query(...),
):
    print("===>API CALL: db/getReview called")
    review = fetch_review(review_id)
    return review

@router.post("/getReviewsByUser")
def get_review_by_user(
    token= Depends(get_current_user),
    user_id: str = Query(...),
):
    print("===>API CALL: db/getReviewsByUser")
    try:    
        review = fetch_reviews_by_user_id(user_id)
        return review
    except ValueError as e:
        error_msg = str(e)
        raise HTTPException(status_code=404, detail=error_msg)

# delete all reviews for a user
@router.post("/deleteReviewsByUser")
def delete_reviews_by_user(
    token= Depends(get_current_user),
    user_id: str = Query(...),
):
    print("===>API CALL: db/deleteReviewsByUser")
    result = delete_reviews_by_user_id(user_id)
    return result

@router.post("/addNewUser")
def add_new_user(
    token= Depends(get_current_user),
    user= Body(...),
):
    print("===>API CALL: db/addNewUser")
    print("    : user ->", user)
    user_id = user.get("user_id")
    user = fetch_user(user_id)
    if user:
        raise HTTPException(status_code=400, detail="User already exists")
    user = {
        "user_id": user_id,
        "name": user.get("name"),
        "email": user.get("email"),
        "created_at": datetime.now(),
    }
    result = add_new_user(user)
    return result

@router.post("/addVendor")
def addVendor(
    token= Depends(get_current_user),
    body= Body(...),
):
    print("===>API CALL: db/addVendor")

    vendor = {
        "name": body.get("name"),
        "address": body.get("address"),
        "created_at": datetime.now(),
        "review_ids": [body.get("reviewID")],
    }
    print("    : reviewID ->", body.get("reviewID"))
    vendor_id = add_vendor(vendor)

    return str(vendor_id)
