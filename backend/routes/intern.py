from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User, TrainingPlan, ProgressLog

router = APIRouter(prefix="/api/intern", tags=["intern"])

@router.get("/{intern_id}")
def get_intern_profile(intern_id: int, db: Session = Depends(get_db)):
    intern = db.query(User).filter(User.id == intern_id, User.role == "intern").first()
    if not intern:
        return {"error": "Not found"}
    plans = db.query(TrainingPlan).filter(
        TrainingPlan.department == intern.department
    ).order_by(TrainingPlan.stage, TrainingPlan.sort_order).all()
    logs = db.query(ProgressLog).filter(ProgressLog.intern_id == intern_id).all()
    log_map = {l.plan_id: l for l in logs}

    stages_data = {}
    for plan in plans:
        stage_name_map = {"onboarding": "入职适应", "growth": "快速成长", "independent": "独立贡献"}
        key = stage_name_map.get(plan.stage, plan.stage)
        if key not in stages_data:
            stages_data[key] = {"stage_key": plan.stage, "items": []}
        log = log_map.get(plan.id)
        stages_data[key]["items"].append({
            "id": plan.id,
            "name": plan.milestone_name,
            "description": plan.description,
            "status": log.status if log else "pending",
            "feedback": log.mentor_feedback if log else None,
        })

    total = len(plans)
    completed = len([l for l in logs if l.status == "completed"])
    progress_pct = round(completed / total * 100) if total > 0 else 0

    return {
        "intern": {"id": intern.id, "name": intern.name, "department": intern.department,
                    "position": intern.position, "stage": intern.stage, "start_date": intern.start_date},
        "stages": list(stages_data.values()),
        "progress_pct": progress_pct,
        "total_milestones": total,
        "completed_milestones": completed,
    }

@router.get("/{intern_id}/history")
def get_history(intern_id: int, db: Session = Depends(get_db)):
    logs = db.query(ProgressLog).filter(ProgressLog.intern_id == intern_id)\
        .order_by(ProgressLog.created_at.desc()).all()
    result = []
    for l in logs:
        plan = db.query(TrainingPlan).filter(TrainingPlan.id == l.plan_id).first()
        mentor = db.query(User).filter(User.id == l.mentor_id).first()
        result.append({
            "id": l.id,
            "milestone": plan.milestone_name if plan else "",
            "status": l.status,
            "feedback": l.mentor_feedback,
            "mentor_name": mentor.name if mentor else "",
            "created_at": l.created_at,
        })
    return result
