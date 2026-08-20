from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Customer, Sale, User
from schemas import CustomerCreate, CustomerResponse, SaleResponse
from auth import get_current_user


router = APIRouter(
    prefix="/customers",
    tags=["Customers"]
)


@router.post(
    "/",
    response_model=CustomerResponse
)
def create_customer(
    customer_data: list[CustomerCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
      customer = []
      for data in customer_data:
        customer = db.query(Customer).filter(customer.phone == data.phone).first()
        if customer:
            raise HTTPException(
                status_code=400,
                detail=f"Customer with phone {data.phone} already exists"
            )

        
      customers =[]
      for data in customer_data:
        customer = Customer(
            name=data.name,
            phone=data.phone
        )
        db.add(customer)
        customers.append(customer)
    

      db.commit()
      db.refresh(customer)

      return customer


@router.get(
    "/",
    response_model=list[CustomerResponse]
)
def get_customers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return db.query(Customer).all()


@router.get(
    "/{customer_id}",
    response_model=CustomerResponse
)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    customer = db.query(Customer).filter(
        Customer.id == customer_id
    ).first()

    if not customer:

        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    return customer


@router.put(
    "/{customer_id}",
    response_model=CustomerResponse
)
def update_customer(
    customer_id: int,
    customer_data: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    customer = db.query(Customer).filter(
        Customer.id == customer_id
    ).first()

    if not customer:

        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    for key, value in customer_data.dict().items():
        setattr(customer, key, value)

    db.commit()
    db.refresh(customer)

    return customer


@router.delete("/{customer_id}")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    customer = db.query(Customer).filter(
        Customer.id == customer_id
    ).first()

    if not customer:

        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    db.delete(customer)
    db.commit()

    return {
        "message": "Customer deleted successfully"
    }



@router.get("/customer/{customer_id}/sales", response_model=list[SaleResponse])
def get_sales_by_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    
):

    customer= db.query(Customer).filter(
        Customer.id == customer_id
    ).first()

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    return customer.sales



