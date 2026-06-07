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
interns = []
for i, (name, dept, pos, mid, stage) in enumerate(intern_data):
    intern = User(
        name=name, role="intern", department=dept, position=pos,
        mentor_id=mid, start_date=(base_date + timedelta(days=i)).strftime("%Y-%m-%d"),
        stage=stage
    )
    db.add(intern)
    interns.append(intern)

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

plans = []
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
            plans.append(plan)

db.commit()

# Create progress logs for demo (some completed, some pending)
# For each intern, complete the first 1-2 milestones of their current stage
demo_logs = []
now = datetime.now()
for intern in interns:
    # Get plans for this intern's department and current stage
    dept_plans = [p for p in plans if p.department == intern.department]
    # Filter to current stage (and earlier stages)
    stages_order = ["onboarding", "growth", "independent"]
    current_idx = stages_order.index(intern.stage)
    # Complete all milestones in stages before current, and some in current
    for p in dept_plans:
        plan_stage_idx = stages_order.index(p.stage)
        if plan_stage_idx < current_idx:
            # Already passed this stage - complete all
            status = "completed"
        elif plan_stage_idx == current_idx:
            # Current stage - complete first 2 milestones
            status = "completed" if p.sort_order < 2 else "pending"
        else:
            # Future stage - pending
            status = "pending"

        log = ProgressLog(
            intern_id=intern.id,
            plan_id=p.id,
            mentor_id=intern.mentor_id,
            status=status,
            mentor_feedback=f"表现良好，继续保持！" if status == "completed" else None,
            created_at=(now - timedelta(days=p.sort_order)).strftime("%Y-%m-%d %H:%M"),
        )
        demo_logs.append(log)

db.add_all(demo_logs)
db.commit()
db.close()

print("Seed data created: 1 HR + 3 mentors + 20 interns + 36 training plan items + demo progress logs")
