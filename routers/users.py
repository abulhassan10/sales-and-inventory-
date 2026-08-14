from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from utils import hash_password ,verify_password
from database import get_db
from models import User, Role
from schemas import (
    UserCreate,
    UserResponse,
    LoginRequest,
    TokenResponse
)
from fastapi.security import OAuth2PasswordRequestForm
from auth import (
    
    
    create_access_token,
    admin_required
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# -------------------------
# Register Staff
# -------------------------

@router.post(
    "/register",
    response_model=UserResponse
)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.username == user_data.username
    ).first()

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    staff_role = db.query(Role).filter(
        Role.name == "Staff"
    ).first()

    if not staff_role:

        raise HTTPException(
            status_code=500,
            detail="Staff role does not exist"
        )

    hashed_password = hash_password(user_data.password)
    new_user = User(
        username=user_data.username,
        password=hashed_password,
        role_id=staff_role.id
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# -------------------------
# Login
# -------------------------

@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    login_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.username == login_data.username
    ).first()

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    if not verify_password(
        login_data.password,
        user.password
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    token = create_access_token({
        "sub": str(user.id),
        "role": user.role.name
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# -------------------------
# Create Admin
# -------------------------

@router.post(
    "/create-admin",
    response_model=UserResponse
)
def create_admin(
    user_data: UserCreate,

    current_user: User = Depends(
        admin_required
    ),

    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.username == user_data.username
    ).first()

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    admin_role = db.query(Role).filter(
        Role.name == "Admin"
    ).first()

    if not admin_role:

        raise HTTPException(
            status_code=500,
            detail="Admin role does not exist"
        )

    hashed_password = hash_password(user_data.password)
    new_admin = User(
        username=user_data.username,
        password=hashed_password,
        role_id=admin_role.id
    )

    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)

    return new_admin