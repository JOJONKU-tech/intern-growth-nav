# 业务部实习生成长导航 — 实现计划

> **For agentic workers:** Use delegate_task per task. Steps use checkbox syntax.

**Goal:** 构建 FastAPI + SQLite + 原生前端的企业实习生成长导航 Web 应用

**Architecture:** FastAPI 提供 REST API 并托管静态前端文件。前端三视图（导师/实习生/HR）按角色路由。SQLite 单文件数据库。

**Tech Stack:** Python 3, FastAPI, SQLAlchemy, SQLite, Chart.js (CDN), 原生 HTML/CSS/JS

---

### Task 1: 项目骨架 + 数据库模型 [BE]

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/models.py`
- Create: `backend/database.py`

- [ ] **Step 1: 写 requirements.txt**

```
fastapi==0.115.0
uvicorn==0.30.0
sqlalchemy==2.0.35
```

- [ ] **Step 2: 写 database.py**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./intern_growth.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 3: 写 models.py** — 4 张表

```python
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    role = Column(String)  # mentor, intern, hr
    department = Column(String, nullable=True)
    position = Column(String, nullable=True)
    mentor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    start_date = Column(String, nullable=True)
    stage = Column(String, nullable=True)  # onboarding, growth, independent
    interns = relationship("User", backref="mentor", remote_side=[id], foreign_keys=[mentor_id])

class TrainingPlan(Base):
    __tablename__ = "training_plan"
    id = Column(Integer, primary_key=True)
    department = Column(String)
    stage = Column(String)
    milestone_name = Column(String)
    description = Column(Text)
    sort_order = Column(Integer)

class ProgressLog(Base):
    __tablename__ = "progress_log"
    id = Column(Integer, primary_key=True)
    intern_id = Column(Integer, ForeignKey("users.id"))
    plan_id = Column(Integer, ForeignKey("training_plan.id"))
    mentor_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="pending")  # pending, completed, flagged
    mentor_feedback = Column(Text, nullable=True)
    created_at = Column(String)
```

- [ ] **Step 4: 验证模型可创建** → `python3 -c "from models import Base; from database import engine; Base.metadata.create_all(bind=engine); print('OK')"`

- [ ] **Step 5: 提交** → `git add backend/ && git commit -m "feat: 数据库模型"`

---

### Task 2: Mock 数据种子 [BE]

**Files:**
- Create: `backend/seed.py`

- [ ] **Step 1: 写 seed.py** — 包含：
  - 1 个 HR 账号（王芳）
  - 3 个导师（研发张伟、产品李明、销售陈芳）
  - 20 个实习生（研发 8 人、产品 6 人、销售 6 人），分配到不同导师
  - 带教计划模板（每个岗位类型 × 3 阶段 × 4 条里程碑 = 36 条计划）
  - 部分已完成进度日志（让演示数据不全是空的）

```python
from database import SessionLocal, engine
from models import Base, User, TrainingPlan, ProgressLog
from datetime import datetime, timedelta

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# HR
hr = User(name="王芳", role="hr")
db.add(hr)

# Mentors
mentors = [
    User(name="张伟", role="mentor", department="研发"),
    User(name="李明", role="mentor", department="产品"),
    User(name="陈芳", role="mentor", department="销售"),
]
db.add_all(mentors)
db.flush()

# Interns — 20 people across 3 departments
intern_data = [
    # 研发 (8人) → mentor 张伟
    ("赵一", "研发", "后端开发工程师", mentors[0].id, "onboarding"),
    ("钱二", "研发", "前端开发工程师", mentors[0].id, "onboarding"),
    ("孙三", "研发", "测试工程师", mentors[0].id, "growth"),
    ("李四", "研发", "后端开发工程师", mentors[0].id, "growth"),
    ("周五", "研发", "算法工程师", mentors[0].id, "onboarding"),
    ("吴六", "研发", "前端开发工程师", mentors[0].id, "growth"),
    ("郑七", "研发", "运维工程师", mentors[0].id, "independent"),
    ("王八", "研发", "后端开发工程师", mentors[0].id, "onboarding"),
    # 产品 (6人) → mentor 李明
    ("冯九", "产品", "产品助理", mentors[1].id, "onboarding"),
    ("陈十", "产品", "产品助理", mentors[1].id, "growth"),
    ("褚十一", "产品", "数据分析", mentors[1].id, "onboarding"),
    ("卫十二", "产品", "产品助理", mentors[1].id, "growth"),
    ("蒋十三", "产品", "用户研究", mentors[1].id, "onboarding"),
    ("沈十四", "产品", "数据分析", mentors[1].id, "independent"),
    # 销售 (6人) → mentor 陈芳
    ("韩十五", "销售", "大客户销售", mentors[2].id, "onboarding"),
    ("杨十六", "销售", "渠道销售", mentors[2].id, "growth"),
    ("朱十七", "销售", "销售运营", mentors[2].id, "onboarding"),
    ("秦十八", "销售", "大客户销售", mentors[2].id, "growth"),
    ("许十九", "销售", "渠道销售", mentors[2].id, "independent"),
    ("何二十", "销售", "销售运营", mentors[2].id, "onboarding"),
]
base_date = datetime(2026, 3, 1)
for i, (name, dept, pos, mid, stage) in enumerate(intern_data):
    intern = User(
        name=name, role="intern", department=dept, position=pos,
        mentor_id=mid, start_date=(base_date + timedelta(days=i)).strftime("%Y-%m-%d"),
        stage=stage
    )
    db.add(intern)

# Training plans — 3 departments × 3 stages × 4 milestones
stage_names = {"onboarding": "入职适应", "growth": "快速成长", "independent": "独立贡献"}
templates = {
    "研发": {
        "onboarding": ["环境搭建", "代码规范学习", "技术栈入门", "第一个 Bug 修复"],
        "growth": ["独立功能开发", "代码评审参与", "技术方案设计", "性能优化实践"],
        "independent": ["模块 owner", "技术分享", "新人指导", "架构讨论参与"],
    },
    "产品": {
        "onboarding": ["产品流程学习", "竞品分析报告", "需求文档撰写", "用户画像理解"],
        "growth": ["需求评审主持", "数据分析实践", "AB 测试设计", "产品路线图参与"],
        "independent": ["产品模块 owner", "用户访谈主导", "跨部门协作", "产品策略建议"],
    },
    "销售": {
        "onboarding": ["产品知识学习", "销售话术培训", "客户拜访观摩", "CRM 系统使用"],
        "growth": ["独立客户拜访", "销售方案设计", "商务谈判参与", "客户关系维护"],
        "independent": ["大客户负责人", "团队销售培训", "销售策略制定", "渠道拓展主导"],
    },
}

for dept, stages in templates.items():
    for stage_key, milestones in stages.items():
        for i, milestone in enumerate(milestones):
            plan = TrainingPlan(
                department=dept, stage=stage_key,
                milestone_name=milestone,
                description=f"{stage_names[stage_key]}阶段 - {milestone}",
                sort_order=i
            )
            db.add(plan)

db.commit()
db.close()
print("Seed data created: 1 HR + 3 mentors + 20 interns + 36 training plan items")
```

- [ ] **Step 2: 运行验证** → `python3 backend/seed.py`

- [ ] **Step 3: 提交** → `git add backend/seed.py && git commit -m "feat: Mock 数据种子"`

---

### Task 3: Auth API [BE]

**Files:**
- Create: `backend/routes/__init__.py`
- Create: `backend/routes/auth.py`

- [ ] **Step 1: 写 auth.py**

```python
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
```

- [ ] **Step 2: 验证 API** → 启动服务 `uvicorn main:app --reload`，`curl localhost:8000/api/auth/accounts`

- [ ] **Step 3: 提交**

---

### Task 4: Intern API [BE]

**Files:**
- Create: `backend/routes/intern.py`

- [ ] **Step 1: 写 intern.py**

```python
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

    # Calculate progress
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
```

- [ ] **Step 2: 验证** → `curl localhost:8000/api/intern/5`

- [ ] **Step 3: 提交**

---

### Task 5: Mentor API [BE]

**Files:**
- Create: `backend/routes/mentor.py`

```python
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
```

- [ ] **Step 2: 验证** → `curl localhost:8000/api/mentor/2/interns`

- [ ] **Step 3: 提交**

---

### Task 6: HR API [BE]

**Files:**
- Create: `backend/routes/hr.py`

```python
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

        # Anomaly: onboarding stage but > 60 days since start
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
```

- [ ] **Step 2: 验证** → `curl localhost:8000/api/hr/dashboard`

- [ ] **Step 3: 提交**

---

### Task 7: FastAPI 主入口 + 静态文件托管 [BE]

**Files:**
- Create: `backend/main.py`

- [ ] **Step 1: 写 main.py**

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from database import engine
from models import Base
from routes import auth, intern, mentor, hr

Base.metadata.create_all(bind=engine)

app = FastAPI(title="实习生成长导航")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(auth.router)
app.include_router(intern.router)
app.include_router(mentor.router)
app.include_router(hr.router)

app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")
```

- [ ] **Step 2: 启动验证** → `cd backend && python3 main.py` 报错需要 uvicorn 的话用 `uvicorn main:app --host 0.0.0.0 --port 8000`

- [ ] **Step 3: 验证前端路由** → `curl localhost:8000/` 应返回前端 HTML

- [ ] **Step 4: 提交**

---

### Task 8: 前端 — 登录页 + 导航框架 [FE]

**Files:**
- Create: `frontend/index.html`
- Create: `frontend/css/style.css`

功能：TDesign 风格登录页，列出预设账号，点选进入对应视图。顶部导航按角色切换。

设计令牌：`#0052d9` 主色、`#f5f7fa` 底色、PingFang SC 字体、6-12px 圆角。

- [ ] **Step 1: 写 style.css** — 全局样式 + 设计令牌
- [ ] **Step 2: 写 index.html** — 登录页 + 角色卡片选择
- [ ] **Step 3: 写导航框架** — 顶部栏 + 侧边栏（按角色切换内容）
- [ ] **Step 4: 验证** — 浏览器打开 `localhost:8000`，能登录并看到空视图
- [ ] **Step 5: 提交**

---

### Task 9: 前端 — 实习生视图 [FE]

**Files:**
- Modify: `frontend/index.html`（添加实习生视图 HTML）
- Create: `frontend/js/intern.js`

功能：成长路径时间线 + 阶段目标清单 + 进度条 + 导师反馈。

- [ ] **Step 1: 写实习生视图 HTML** — 三阶段时间线 + 进度条 + 任务清单 + 反馈区
- [ ] **Step 2: 写 intern.js** — 调用 `/api/intern/{id}` 渲染数据
- [ ] **Step 3: 验证** — 登录赵一，看到时间线 + 任务状态
- [ ] **Step 4: 提交**

---

### Task 10: 前端 — 导师视图 [FE]

**Files:**
- Modify: `frontend/index.html`（添加导师视图 HTML）
- Create: `frontend/js/mentor.js`

功能：实习生卡片列表 + 带教计划详情 + 里程碑打勾 + 反馈弹窗。

- [ ] **Step 1: 写导师视图 HTML** — 实习生卡片网格 + 计划详情面板 + 反馈 modal
- [ ] **Step 2: 写 mentor.js** — 调用 `/api/mentor/{id}/interns` 和完成 API
- [ ] **Step 3: 验证** — 登录张伟，看到 8 个实习生，点击进入带教计划
- [ ] **Step 4: 提交**

---

### Task 11: 前端 — HR 仪表盘 [FE]

**Files:**
- Modify: `frontend/index.html`（添加 HR 视图 HTML）
- Create: `frontend/js/hr.js`

功能：KPI 卡片行 + 岗位分布图 + 20 人状态表 + 异常标记 + 个人钻取。

- [ ] **Step 1: 写 HR 视图 HTML** — 4 KPI 卡片 + 图表容器 + 紧凑数据表
- [ ] **Step 2: 写 hr.js** — 调用 `/api/hr/dashboard`，Chart.js 渲染图表
- [ ] **Step 3: 验证** — 登录王芳，看到总览仪表盘 + 异常标记
- [ ] **Step 4: 提交**

---

### Task 12: 集成测试 + 启动脚本 [BE]

**Files:**
- Create: `start.sh`

- [ ] **Step 1: 写 start.sh**

```bash
#!/bin/bash
cd "$(dirname "$0")/backend"
pip install -r requirements.txt -q 2>/dev/null
python3 seed.py
echo ""
echo "==================================="
echo "  实习生成长导航系统"
echo "  访问: http://localhost:8000"
echo "==================================="
echo ""
echo "演示账号："
echo "  导师-张伟(研发)  id=2"
echo "  导师-李明(产品)  id=3"
echo "  导师-陈芳(销售)  id=4"
echo "  实习生-赵一(研发) id=5"
echo "  实习生-冯九(产品) id=11"
echo "  实习生-韩十五(销售) id=19"
echo "  HR-王芳          id=1"
echo ""
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

- [ ] **Step 2: chmod +x start.sh**
- [ ] **Step 3: 端到端测试** — `./start.sh`，浏览器访问，三角色全流程走通
- [ ] **Step 4: 提交**
