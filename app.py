"""
实习生成长导航 — 单文件后端
启动：python app.py
"""

import sqlite3
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn

DB = "intern_growth.db"

# ============================================================
# 数据库
# ============================================================
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT, role TEXT, department TEXT,
            position TEXT, mentor_id INTEGER,
            start_date TEXT, stage TEXT DEFAULT 'onboarding'
        );
        CREATE TABLE IF NOT EXISTS training_plan (
            id INTEGER PRIMARY KEY,
            department TEXT, stage TEXT,
            milestone_name TEXT, description TEXT,
            sort_order INTEGER
        );
        CREATE TABLE IF NOT EXISTS progress_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            intern_id INTEGER, plan_id INTEGER,
            mentor_id INTEGER, status TEXT DEFAULT 'pending',
            mentor_feedback TEXT, created_at TEXT
        );
    """)
    conn.commit()
    return conn

def seed_if_empty(conn):
    if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0:
        return
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Users: 1 HR + 3 mentors + 20 interns
    users = [
        (1, "王芳", "hr", None, None, None, None, None),
        (2, "张伟", "mentor", "研发", None, None, None, None),
        (3, "李明", "mentor", "产品", None, None, None, None),
        (4, "陈芳", "mentor", "销售", None, None, None, None),
    ]
    interns = [
        (5, "赵一", "研发", "后端开发", 2), (6, "钱二", "研发", "前端开发", 2),
        (7, "孙三", "研发", "测试工程师", 2), (8, "李四", "研发", "后端开发", 2),
        (9, "周五", "研发", "算法工程师", 2), (10, "吴六", "研发", "前端开发", 2),
        (11, "郑七", "研发", "运维工程师", 2), (12, "王八", "研发", "后端开发", 2),
        (13, "冯九", "产品", "产品助理", 3), (14, "陈十", "产品", "产品助理", 3),
        (15, "褚十一", "产品", "数据分析", 3), (16, "卫十二", "产品", "产品助理", 3),
        (17, "蒋十三", "产品", "用户研究", 3), (18, "沈十四", "产品", "数据分析", 3),
        (19, "韩十五", "销售", "大客户销售", 4), (20, "杨十六", "销售", "渠道销售", 4),
        (21, "朱十七", "销售", "销售运营", 4), (22, "秦十八", "销售", "大客户销售", 4),
        (23, "许十九", "销售", "渠道销售", 4), (24, "何二十", "销售", "销售运营", 4),
    ]
    base = datetime(2026, 3, 1)
    stages = ["onboarding"] * 10 + ["growth"] * 7 + ["independent"] * 3
    for i, (uid, name, dept, pos, mid) in enumerate(interns):
        sd = (base + timedelta(days=i)).strftime("%Y-%m-%d")
        users.append((uid, name, "intern", dept, pos, mid, sd, stages[i]))

    conn.executemany(
        "INSERT INTO users VALUES (?,?,?,?,?,?,?,?)", users
    )

    # Training plans: 3 depts x 3 stages x 4 milestones
    templates = {
        "研发": {
            "onboarding": ["开发环境搭建", "代码规范学习", "技术栈入门", "第一个Bug修复"],
            "growth": ["独立功能开发", "Code Review参与", "技术方案设计", "性能优化实践"],
            "independent": ["模块Owner", "技术分享主讲", "新人指导", "架构讨论参与"],
        },
        "产品": {
            "onboarding": ["产品流程学习", "竞品分析报告", "PRD文档撰写", "用户画像理解"],
            "growth": ["需求评审主持", "数据分析实践", "AB测试设计", "产品路线图参与"],
            "independent": ["产品模块Owner", "用户访谈主导", "跨部门协作", "产品策略建议"],
        },
        "销售": {
            "onboarding": ["产品知识学习", "销售话术培训", "客户拜访观摩", "CRM系统使用"],
            "growth": ["独立客户拜访", "销售方案设计", "商务谈判参与", "客户关系维护"],
            "independent": ["大客户负责人", "团队销售培训", "销售策略制定", "渠道拓展主导"],
        },
    }
    plans = []
    pid = 1
    for dept, stages_data in templates.items():
        for stage_key, milestones in stages_data.items():
            for i, milestone in enumerate(milestones):
                plans.append((pid, dept, stage_key, milestone, f"{stage_key}阶段里程碑", i))
                pid += 1
    conn.executemany(
        "INSERT INTO training_plan VALUES (?,?,?,?,?,?)", plans
    )

    # Demo progress: complete ~40% of milestones with feedback
    feedbacks = ["完成得很好，继续保持","基础扎实，注意代码规范","需要加强沟通能力","进步明显，已经能独立完成任务","多加练习，这部分还不熟练","表现优秀，超出预期"]
    flog = []
    import random
    random.seed(42)
    for iid in range(5, 25):
        dept = conn.execute("SELECT department FROM users WHERE id=?", (iid,)).fetchone()[0]
        dept_plans = conn.execute(
            "SELECT id FROM training_plan WHERE department=? ORDER BY sort_order", (dept,)
        ).fetchall()
        count = random.randint(3, min(8, len(dept_plans)))
        for j, plan in enumerate(dept_plans[:count]):
            mentor_id = conn.execute("SELECT mentor_id FROM users WHERE id=?", (iid,)).fetchone()[0]
            day_offset = random.randint(1, 90)
            ts = (base + timedelta(days=day_offset)).strftime("%Y-%m-%d %H:%M")
            flog.append((iid, plan["id"], mentor_id, "completed",
                         random.choice(feedbacks) if j % 3 != 0 else None, ts))
    conn.executemany(
        "INSERT INTO progress_log (intern_id,plan_id,mentor_id,status,mentor_feedback,created_at) VALUES (?,?,?,?,?,?)",
        flog
    )
    conn.commit()

# ============================================================
# FastAPI
# ============================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    conn = init_db()
    seed_if_empty(conn)
    conn.close()
    yield

app = FastAPI(title="实习生成长导航", lifespan=lifespan)

# ============================================================
# API
# ============================================================

@app.get("/api/me")
def get_me(user_id: int = Query(...)):
    conn = get_db()
    u = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    if not u:
        return JSONResponse({"error": "not found"}, 404)
    return dict(u)

@app.get("/api/intern/{intern_id}")
def get_intern(intern_id: int):
    conn = get_db()
    intern = conn.execute(
        "SELECT * FROM users WHERE id=? AND role='intern'", (intern_id,)
    ).fetchone()
    if not intern:
        conn.close(); return JSONResponse({"error": "not found"}, 404)

    plans = conn.execute(
        "SELECT * FROM training_plan WHERE department=? ORDER BY stage, sort_order",
        (intern["department"],)
    ).fetchall()

    logs_rows = conn.execute(
        "SELECT * FROM progress_log WHERE intern_id=?", (intern_id,)
    ).fetchall()
    logs = {l["plan_id"]: dict(l) for l in logs_rows}

    stage_names = {"onboarding": "入职适应", "growth": "快速成长", "independent": "独立贡献"}
    stages_data = {}
    for p in plans:
        key = stage_names.get(p["stage"], p["stage"])
        if key not in stages_data:
            stages_data[key] = {"stage_key": p["stage"], "milestones": []}
        log = logs.get(p["id"])
        stages_data[key]["milestones"].append({
            "plan_id": p["id"],
            "name": p["milestone_name"],
            "description": p["description"],
            "status": log["status"] if log else "pending",
            "feedback": log.get("mentor_feedback") if log else None,
        })

    total = len(plans)
    completed = sum(1 for l in logs.values() if l["status"] == "completed")
    pct = round(completed / total * 100) if total > 0 else 0

    conn.close()
    return {
        "intern": dict(intern),
        "stages": list(stages_data.values()),
        "progress_pct": pct,
        "total_milestones": total,
        "completed_milestones": completed,
    }

@app.get("/api/mentor/{mentor_id}/interns")
def mentor_interns(mentor_id: int):
    conn = get_db()
    interns = conn.execute(
        "SELECT * FROM users WHERE mentor_id=? AND role='intern'", (mentor_id,)
    ).fetchall()
    result = []
    for i in interns:
        total = conn.execute(
            "SELECT COUNT(*) FROM training_plan WHERE department=?", (i["department"],)
        ).fetchone()[0]
        done = conn.execute(
            "SELECT COUNT(*) FROM progress_log WHERE intern_id=? AND status='completed'",
            (i["id"],)
        ).fetchone()[0]
        pct = round(done / total * 100) if total > 0 else 0
        result.append({
            "id": i["id"], "name": i["name"], "department": i["department"],
            "position": i["position"], "stage": i["stage"],
            "progress_pct": pct, "completed": done, "total": total,
        })
    conn.close()
    return result

@app.get("/api/mentor/{mentor_id}/intern/{intern_id}/plan")
def mentor_plan(mentor_id: int, intern_id: int):
    conn = get_db()
    intern = conn.execute("SELECT * FROM users WHERE id=?", (intern_id,)).fetchone()
    if not intern:
        conn.close(); return JSONResponse({"error": "not found"}, 404)

    plans = conn.execute(
        "SELECT * FROM training_plan WHERE department=? ORDER BY stage, sort_order",
        (intern["department"],)
    ).fetchall()

    logs_rows = conn.execute(
        "SELECT * FROM progress_log WHERE intern_id=?", (intern_id,)
    ).fetchall()
    logs = {l["plan_id"]: dict(l) for l in logs_rows}

    items = []
    for p in plans:
        log = logs.get(p["id"])
        items.append({
            "plan_id": p["id"],
            "milestone": p["milestone_name"],
            "description": p["description"],
            "stage": p["stage"],
            "status": log["status"] if log else "pending",
            "feedback": log.get("mentor_feedback") if log else None,
        })

    conn.close()
    return {
        "intern_name": intern["name"],
        "department": intern["department"],
        "items": items,
    }

@app.post("/api/mentor/{mentor_id}/complete/{plan_id}")
def complete_milestone(mentor_id: int, plan_id: int, data: dict):
    conn = get_db()
    intern_id = data.get("intern_id")
    feedback = data.get("feedback", "")
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    existing = conn.execute(
        "SELECT id FROM progress_log WHERE intern_id=? AND plan_id=?",
        (intern_id, plan_id)
    ).fetchone()

    if existing:
        conn.execute(
            "UPDATE progress_log SET status='completed', mentor_feedback=?, created_at=? WHERE id=?",
            (feedback, now, existing["id"])
        )
    else:
        conn.execute(
            "INSERT INTO progress_log (intern_id,plan_id,mentor_id,status,mentor_feedback,created_at) VALUES (?,?,?,?,?,?)",
            (intern_id, plan_id, mentor_id, "completed", feedback, now)
        )
    conn.commit()
    conn.close()
    return {"ok": True}

@app.get("/api/hr/dashboard")
def hr_dashboard():
    conn = get_db()
    interns = conn.execute("SELECT * FROM users WHERE role='intern'").fetchall()

    stage_counts = {"onboarding": 0, "growth": 0, "independent": 0}
    dept_counts = {}
    intern_list = []
    anomaly_count = 0

    stage_labels = {"onboarding": "入职适应", "growth": "快速成长", "independent": "独立贡献"}
    base = datetime(2026, 3, 1)

    for i in interns:
        stage_counts[i["stage"]] = stage_counts.get(i["stage"], 0) + 1
        dept_counts[i["department"]] = dept_counts.get(i["department"], 0) + 1

        total = conn.execute(
            "SELECT COUNT(*) FROM training_plan WHERE department=?", (i["department"],)
        ).fetchone()[0]
        done = conn.execute(
            "SELECT COUNT(*) FROM progress_log WHERE intern_id=? AND status='completed'",
            (i["id"],)
        ).fetchone()[0]
        pct = round(done / total * 100) if total > 0 else 0

        anomaly = False
        if i["stage"] == "onboarding" and i["start_date"]:
            try:
                sd = datetime.strptime(i["start_date"], "%Y-%m-%d")
                if (datetime.now() - sd).days > 60:
                    anomaly = True
                    anomaly_count += 1
            except:
                pass

        intern_list.append({
            "id": i["id"], "name": i["name"], "department": i["department"],
            "position": i["position"], "stage": stage_labels.get(i["stage"], i["stage"]),
            "progress_pct": pct, "anomaly": anomaly, "start_date": i["start_date"],
        })

    total_count = len(interns)
    completion_rate = round(sum(x["progress_pct"] for x in intern_list) / total_count) if total_count > 0 else 0

    conn.close()
    return {
        "total": total_count,
        "stage_counts": [{"stage": stage_labels.get(k, k), "count": v} for k, v in stage_counts.items()],
        "dept_counts": [{"department": k, "count": v} for k, v in dept_counts.items()],
        "completion_rate": completion_rate,
        "anomaly_count": anomaly_count,
        "interns": intern_list,
    }

# ============================================================
# 静态文件
# ============================================================
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
