from fastapi import FastAPI
from sqlalchemy.orm import Session

from database import Base, engine, SessionLocal
from models import User, Role
from utils import hash_password

from routers.users import router as users_router
from routers.products import router as products_router
from routers.customers import router as customers_router
from routers.sales import router as sales_router

import os
from dotenv import load_dotenv


load_dotenv()


# Create database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Sales & Inventory Management API"
)


# --------------------------------
# Create default roles
# --------------------------------

def create_default_roles():

    db = SessionLocal()

    try:

        admin_role = db.query(Role).filter(
            Role.name == "Admin"
        ).first()

        if not admin_role:
            db.add(Role(name="Admin"))

        staff_role = db.query(Role).filter(
            Role.name == "Staff"
        ).first()

        if not staff_role:
            db.add(Role(name="Staff"))

        db.commit()

    finally:
        db.close()


# --------------------------------
# Create initial Admin
# --------------------------------

def create_initial_admin():
    db = SessionLocal()

    try:
        admin_role = db.query(Role).filter(
            Role.name == "Admin"
        ).first()

        admin_username = os.getenv("ADMIN_USERNAME")
        admin_password = os.getenv("ADMIN_PASSWORD")

        if admin_username is None:
            raise RuntimeError("ADMIN_USERNAME is missing")

        if admin_password is None:
            raise RuntimeError("ADMIN_PASSWORD is missing")

        existing_admin = db.query(User).filter(
            User.username == admin_username
        ).first()
        hashed_password = hash_password(admin_password)
        if not existing_admin:
            new_admin = User(
                username=admin_username,
                password=hashed_password,
                role_id=admin_role.id
            )

            db.add(new_admin)
            db.commit()

    finally:
        db.close()


# Run initial setup
create_default_roles()
create_initial_admin()


# --------------------------------
# Routers
# --------------------------------

app.include_router(users_router)
app.include_router(products_router)
app.include_router(customers_router)
app.include_router(sales_router)


# --------------------------------
# Home
# --------------------------------

@app.get("/")
def home():

    return {
        "message": "Sales & Inventory Management API is running"
    }