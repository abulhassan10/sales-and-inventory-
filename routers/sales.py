from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Sale, SaleItem, Customer, Product, User
from schemas import CustomerResponse, SaleCreate, SaleItemResponse, SaleResponse
from auth import get_current_user


router = APIRouter(
    prefix="/sales",
    tags=["Sales"]
)


@router.post(
    "/",
    response_model=SaleResponse
)
def create_sale(
    sale_data: SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    customer = db.query(Customer).filter(
        Customer.id == sale_data.customer_id
    ).first()

    if not customer:

        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    sale = Sale(
        customer_id=sale_data.customer_id,
        total_amount=0
    )

    db.add(sale)
    db.flush()

    total_amount = 0

    for item in sale_data.items:

        product = db.query(Product).filter(
            Product.id == item.product_id
        ).first()

        if not product:

            raise HTTPException(
                status_code=404,
                detail=f"Product {item.product_id} not found"
            )

        if item.quantity <= 0:

            raise HTTPException(
                status_code=400,
                detail="Quantity must be greater than 0"
            )

        if product.stock < item.quantity:

            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for {product.name}"
            )

        item_total = (
            product.price * item.quantity
        )

        sale_item = SaleItem(
            sale_id=sale.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=product.price
        )

        db.add(sale_item)

        product.stock -= item.quantity

        total_amount += item_total

    sale.total_amount = total_amount

    db.commit()
    db.refresh(sale)

    return sale


@router.get(
    "/",
    response_model=list[SaleResponse]
)
def get_sales(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return db.query(Sale).all()


@router.get(
    "/{sale_id}",
    response_model=SaleResponse
)
def get_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    sale = db.query(Sale).filter(
        Sale.id == sale_id
    ).first()

    if not sale:

        raise HTTPException(
            status_code=404,
            detail="Sale not found"
        )

    return sale


@router.get("/sales/product/{product_id}", response_model=list[SaleItemResponse])
def get_sales_by_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    product= db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product.sale_items   


@router.get("/customer/{sale_id}", response_model=CustomerResponse)
def get_customer_by_sale(sale_id:int, db: Session = Depends(get_db)):

    sale= db.query(Sale).filter(Sale.id == sale_id).first()

    if not sale:
        raise HTTPException(
            status_code=404,
            detail="Sale not found"
        )

    return sale.customer