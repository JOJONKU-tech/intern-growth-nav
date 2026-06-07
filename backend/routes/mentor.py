from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User, TrainingPlan, ProgressLog
from datetime import datetime

router = APIRouter(prefix="/api/mentor", tags=["mentor"])

@router.get("/{mentor_id}/interns")
def get_my_interns(mentor_id: int, db: Session = Depends(get_db)):
    interns = db.query(User).filter(User.mentor_id == mentor_id, User.role == "intern").all()
    result = []
    for i in interns:
        logs = db.query(ProgressLog).filter(ProgressLog.intern_id == i.id).all()
        completed = len([l for l in logs if l.status == "completed"])
        plans = db.query(TrainingPlan).filter(TrainingPlan.department == i.department).all()
        total = len(plans)
        result.append({
            "id": i.id, "name": i.name, "department": i.department,
            "position": i.position, "stage": i.stage,
            "progress_pct": round(completed / total * 100) if total > 0 else 0,
            "completed": completed, "total": total,
        })
    return result

@router.get("/{mentor_id}/intern/{intern_id}/plan")
def get_intern_plan(mentor_id: int, intern_id: int, db: Session = Depends(get_db)):
    intern = db.query(User).filter(User.id == intern_id).first()
    plans = db.query(TrainingPlan).filter(
        TrainingPlan.department == intern.department
    ).order_by(TrainingPlan.stage, TrainingPlan.sort_order).all()
    logs = db.query(ProgressLog).filter(ProgressLog.intern_id == intern_id).all()
    log_map = {l.plan_id: l for l in logs}
    items = []
    for p in plans:
        log = log_map.get(p.id)
        items.append({
            "plan_id": p.id, "milestone": p.milestone_name,
            "description": p.description, "stage": p.stage,
            "status": log.status if log else "pending",
            "feedback": log.mentor_feedback if log else None,
        })
    return {"intern_name": intern.name, "department": intern.department, "items": items}

@router.post("/{mentor_id}/complete/{plan_id}")
def complete_milestone(mentor_id: int, plan_id: int, data: dict, db: Session = Depends(get_db)):
    intern_id = data.get("intern_id")
    feedback = data.get("feedback", "")
    log = db.query(ProgressLog).filter(
        ProgressLog.intern_id == intern_id, ProgressLog.plan_id == plan_id
    ).first()
    if log:
        log.status = "completed"
        log.mentor_feedback = feedback
        log.created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    else:
        log = ProgressLog(
            intern_id=intern_id, plan_id=plan_id, mentor_id=mentor_id,
            status="completed", mentor_feedback=feedback,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M")
        )
        db.add(log)
    db.commit()
    return {"ok": True}
