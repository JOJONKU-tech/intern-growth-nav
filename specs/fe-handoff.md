# 实习生成长导航 — 前端设计规格书

## 给 MiniMax M3 的几句话

你是一个有品味的前端设计师。这个项目的核心不是做管理后台，而是做一个**陪伴实习生成长的导航工具**。

请在开始编码前，先加载以下技能来建立你的设计判断：
1. `taste-frontend` — 反 AI 味设计规则
2. `impeccable` — 设计系统参考（调用 `reference/product.md`）
3. `popular-web-designs` — 真实设计系统参考

**你有完全的设计自主权**——选择你认为最能传达"成长陪伴"感觉的风格。不要被任何预设风格束缚。

---

## 项目背景

某部门 20 名校招实习生，分布在研发、产品、销售岗位。三个痛点：
- 导师凭经验带教，缺乏标准节奏
- 实习生对"我该学什么"迷茫
- HR 缺乏全局适岗视角

---

## 设计哲学（核心方向）

| 维度 | 方向 |
|------|------|
| 核心隐喻 | 成长旅程 / 冒险 |
| 实习生视角 | 陪伴式的成长路径——"我在哪里、做过什么、要去哪" |
| 视觉语言 | 温暖、有节奏感、有惊喜 |
| 交互模式 | 探索、打卡、解锁——不是填表 |
| 参考感觉 | Duolingo / Forest / Headspace 的感觉，但不是照抄 |

**实习生页面是主角**——它不是被监控的状态表，而是一个引导实习生看到自己成长的伴侣。

---

## 约束条件

- 单文件 HTML（CSS 可以内嵌或独立文件，JS 内嵌）
- 部署到 Web 服务器，非离线——可以用 CDN 引 Chart.js 或其他库
- `onclick` 绑定事件，不用 `addEventListener`
- **禁止 emoji**
- **禁止 Inter/Roboto 字体**——用 PingFang SC / system-ui
- 后端跑在 `localhost:8000`，前端通过相对路径调 API

---

## API 接口文档

### 1. 获取当前用户
```
GET /api/me?user_id=5
Response: { id, name, role, department, position, mentor_id, start_date, stage }
```
role 值: "intern" | "mentor" | "hr"
stage 值: "onboarding" | "growth" | "independent"

### 2. 实习生成长数据
```
GET /api/intern/{intern_id}
Response: {
  intern: { id, name, department, position, stage, start_date },
  stages: [
    {
      stage_key: "onboarding",
      milestones: [
        { plan_id, name, description, status, feedback }
      ]
    }
  ],
  progress_pct: 67,
  total_milestones: 12,
  completed_milestones: 8
}
```
milestone.status: "pending" | "completed" | "flagged"
milestone.feedback: string|null (导师反馈)

### 3. 导师的实习生列表
```
GET /api/mentor/{mentor_id}/interns
Response: [{ id, name, department, position, stage, progress_pct, completed, total }]
```

### 4. 导师查看某实习生带教计划
```
GET /api/mentor/{mentor_id}/intern/{intern_id}/plan
Response: {
  intern_name, department,
  items: [{ plan_id, milestone, description, stage, status, feedback }]
}
```

### 5. 导师完成里程碑
```
POST /api/mentor/{mentor_id}/complete/{plan_id}
Body: { intern_id, feedback }
Response: { ok: true }
```

### 6. HR 仪表盘
```
GET /api/hr/dashboard
Response: {
  total, completion_rate, anomaly_count,
  stage_counts: [{ stage, count }],
  dept_counts: [{ department, count }],
  interns: [{ id, name, department, position, stage, progress_pct, anomaly, start_date }]
}
```

---

## 演示账号

| 角色 | 姓名 | user_id | 备注 |
|------|------|---------|------|
| HR | 王芳 | 1 | |
| 导师 | 张伟 | 2 | 研发部，带 8 人 |
| 导师 | 李明 | 3 | 产品部，带 6 人 |
| 导师 | 陈芳 | 4 | 销售部，带 6 人 |
| 实习生 | 赵一 | 5 | 研发-后端开发 |
| 实习生 | 冯九 | 13 | 产品-产品助理 |
| 实习生 | 韩十五 | 19 | 销售-大客户销售 |

---

## 页面要求

### 登录页
用户看到三个入口（实习生/导师/HR），点击后选择具体身份进入。
- 预设演示账号直接可选
- 不需要注册流程

### 实习生页面（⭐ 核心页面）

这是整个产品最重要的页面。实习生登录后看到的是**自己的成长旅程**。

要求：
- 一条成长路径作为视觉主轴（三阶段 = 三个章节）
- 里程碑是路上的"站点"——完成一个，亮一个
- 进度感不是冷冰冰的 "67%"，而是 "你已走了多远" 的叙事感
- 能看到已完成的是什么（成就感）、正在做什么（方向感）、接下来是什么（期待感）
- 导师的反馈要展示出来——像"路上的指引"
- **有趣味性和交互感**——不是数据报表，是旅程

### 导师页面
- 看到自己带的实习生卡片（简洁，不要大表）
- 点击进入某个实习生的带教计划
- 计划以步骤流展示——清晰的阶段分隔
- 可以勾选完成里程碑 + 写反馈

### HR 页面
- 全局总览：多少人、阶段分布、完成率、异常
- 实习生列表（紧凑）
- 点击可查看个人成长详情
- 保持简洁——这不是运营大屏，是快速了解状态

---

## 交付要求

1. 输出到 `/Users/jojo/projects/intern-growth-nav/static/index.html`
2. CSS 可以内嵌，或在 `static/css/style.css`
3. 启动 `python app.py` 后浏览器打开 `localhost:8000` 就能访问
4. 三角形色全流程能走通
5. 实测页面，确认按钮能点、数据能加载、交互正常
