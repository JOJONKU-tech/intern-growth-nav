from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User

router = APIRouter(prefix="/api/auth", tags=["auth"])

PRESET_ACCOUNTS = [
    {"id": 1, "name": "王芳", "role": "hr"},
    {"id": 2, "name": "张伟", "role": "mentor"},
    {"id": 3, "name": "李明", "role": "mentor"},
    {"id": 4, "name": "陈芳", "role": "mentor"},
    {"id": 5, "name": "赵一", "role": "intern"},
    {"id": 6, "name": "钱二", "role": "intern"},
    {"id": 11, "name": "冯九", "role": "intern"},
    {"id": 19, "name": "韩十五", "role": "intern"},
]

@router.get("/accounts")
def list_accounts():
    return PRESET_ACCOUNTS

@router.get("/login/{user_id}")
def login(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user.id,
        "name": user.name,
        "role": user.role,
        "department": user.department,
        "position": user.position,
        "stage": user.stage,
        "mentor_id": user.mentor_id,
    }
