from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User, TrainingPlan, ProgressLog

router = APIRouter(prefix="/api/hr", tags=["hr"])

@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    interns = db.query(User).filter(User.role == "intern").all()
    total = len(interns)
    stage_counts = {"onboarding": 0, "growth": 0, "independent": 0}
    dept_counts = {}
    intern_list = []
    anomaly_count = 0

    stage_name_map = {"onboarding": "入职适应", "growth": "快速成长", "independent": "独立贡献"}

    for i in interns:
        stage_counts[i.stage] = stage_counts.get(i.stage, 0) + 1
        dept_counts[i.department] = dept_counts.get(i.department, 0) + 1

        plans = db.query(TrainingPlan).filter(TrainingPlan.department == i.department).all()
        logs = db.query(ProgressLog).filter(ProgressLog.intern_id == i.id).all()
        total_plan = len(plans)
        completed = len([l for l in logs if l.status == "completed"])
        pct = round(completed / total_plan * 100) if total_plan > 0 else 0

        from datetime import datetime, timedelta
        anomaly = False
        if i.stage == "onboarding" and i.start_date:
            try:
                sd = datetime.strptime(i.start_date, "%Y-%m-%d")
                if (datetime.now() - sd).days > 60:
                    anomaly = True
                    anomaly_count += 1
            except:
                pass

        intern_list.append({
            "id": i.id, "name": i.name, "department": i.department,
            "position": i.position, "stage": stage_name_map.get(i.stage, i.stage),
            "progress_pct": pct, "anomaly": anomaly, "start_date": i.start_date,
        })

    completion_rate = round(
        sum(x["progress_pct"] for x in intern_list) / total
    ) if total > 0 else 0

    return {
        "total": total,
        "stage_counts": [{"stage": stage_name_map.get(k, k), "count": v} for k, v in stage_counts.items()],
        "dept_counts": [{"department": k, "count": v} for k, v in dept_counts.items()],
        "completion_rate": completion_rate,
        "anomaly_count": anomaly_count,
        "interns": intern_list,
    }
