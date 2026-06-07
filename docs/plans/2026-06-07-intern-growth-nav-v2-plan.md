# 实习生成长导航 v2 — 实现计划

**日期**：2026-06-07
**架构**：单文件后端 (app.py) + MiniMax M3 前端

## 架构

```
intern-growth-nav/
├── app.py              # 一个文件：FastAPI + SQLite + seed + API
├── static/
│   └── index.html      # MiniMax M3 写的前端
└── start.sh            # 启动脚本
```

后端 6 个端点，全部在一个 app.py 里。

---

### Task 1: 单文件后端 app.py [BE]

**文件**：`app.py`

一个 FastAPI 文件包含：
- SQLite 数据库初始化
- 4 张表建表（users, training_plan, progress_log）
- seed 数据（1 HR + 3 导师 + 20 实习生 + 36 条计划 + 演示进度）
- 6 个 API 端点
- 静态文件托管

**端点**：

| 方法 | 路径 | 用途 |
|------|------|------|
| GET | /api/me | 当前用户信息 (query: user_id) |
| GET | /api/intern/{id} | 实习生成长数据（阶段+里程碑+进度） |
| GET | /api/mentor/{id}/interns | 导师的实习生列表 |
| GET | /api/mentor/{id}/intern/{iid}/plan | 带教计划详情 |
| POST | /api/mentor/{id}/complete/{plan_id} | 完成里程碑 |
| GET | /api/hr/dashboard | HR 全局总览 |

**交付标准**：`python app.py` 启动，浏览器能调通所有 API。

---

### Task 2: 前端设计 handoff [Spec]

**文件**：`specs/fe-handoff.md`

写给 MiniMax M3 的前端设计规格书，包含：
- 设计哲学（成长旅程隐喻、温暖、有趣味）
- 三角色页面功能描述
- API 接口文档
- 设计规范要求（调用 impeccable/taste-frontend/popular-web-designs）
- 交付标准

---

### Task 3: 委派 MiniMax M3 写前端 [FE]

通过 `hermes -p fe` 启动 MiniMax M3，读取 fe-handoff.md，输出到 `static/index.html`。

MiniMax M3 需自行加载知识库设计技能，选择设计风格和交互方案。

---

### Task 4: 集成测试 + 启动脚本

- 创建 start.sh
- 端到端验证：启动 → 三角色登录 → 全流程走通
- 浏览器实测
