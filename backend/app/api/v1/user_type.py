from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.user_type import *
from db.models.users import Users
from app.api.utils.users import get_current_user
from db.session import get_db
from app.services.user_type import UserTypeService

router = APIRouter(
    prefix="/user-types",
    tags=["user-types"],
)


@router.post("/", response_model=UserTypeOut, status_code=status.HTTP_201_CREATED)
def create_user_type(
    user_type_in: UserTypeCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    service = UserTypeService(db)
    return service.create_user_type(user_type_in.model_dump())


@router.get("/{user_type_id}", response_model=UserTypeOut)
def get_user_type(
    user_type_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    user_type = UserTypeService(db).get_user_type_by_id(user_type_id)
    if not user_type:
        raise HTTPException(status_code=404, detail="User type not found")
    return user_type


@router.get("/", response_model=List[UserTypeOut])
def list_user_types(
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    # simple list; the service currently doesn't have a list method, but we can query directly
    from db.models.user_types import UserTypes
    return db.query(UserTypes).all()


@router.patch("/{user_type_id}", response_model=UserTypeOut)
def update_user_type(
    user_type_id: int,
    user_type_in: UserTypeUpdate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    user_type = UserTypeService(db).update_user_type(
        user_type_id, user_type_in.model_dump(exclude_unset=True)
    )
    if not user_type:
        raise HTTPException(status_code=404, detail="User type not found")
    return user_type


@router.delete("/{user_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_type(
    user_type_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    # we add a delete method to the service or delete directly
    from db.models.user_types import UserTypes
    user_type = db.query(UserTypes).filter(UserTypes.id == user_type_id).first()
    if not user_type:
        raise HTTPException(status_code=404, detail="User type not found")
    db.delete(user_type)
    db.commit()