from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    role_id: int

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class ProductCreate(BaseModel):
    name: str
    price: float
    stock: int


class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    stock: int

    class Config:
        from_attributes = True


class CustomerCreate(BaseModel):
    name: str
    phone: str


class CustomerResponse(BaseModel):
    id: int
    name: str
    phone: str

    class Config:
        from_attributes = True


class SaleItemCreate(BaseModel):
    product_id: int
    quantity: int


class SaleItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float

    class Config:
        from_attributes = True


class SaleCreate(BaseModel):
    customer_id: int
    items: list[SaleItemCreate]


class SaleResponse(BaseModel):
    id: int
    customer_id: int
    total_amount: float
    items: list[SaleItemResponse]

    class Config:
        from_attributes = True