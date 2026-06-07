# 业务部实习生成长导航 — 设计文档

**日期**：2026-06-07
**状态**：已确认

---

## 背景与问题

某部门近期迎来 20 名校招实习生，分布在研发、产品、销售岗位。三个痛点：

1. **导师凭经验带教**，缺乏标准化节奏把控
2. **实习生迷茫**，不知道"我该学什么"，频繁私聊 HR
3. **HR/招聘缺乏全局视角**，常追问"这批人适岗情况如何"

## 目标

构建一套智能工具，标准化导师带教流程，让实习生看到成长路径，让 HR 一眼掌握全局。

## 用户角色

| 角色 | 核心需求 | 页面 |
|------|---------|------|
| 导师 | 看我的实习生、按标准计划带教、记录反馈 | 实习生列表 + 带教详情 |
| 实习生 | 看我的成长阶段、当前目标、导师反馈 | 成长路径时间线 |
| HR/招聘 | 20 人全局适岗状态、异常预警、个人钻取 | 总览仪表盘 + 详情 |

## 架构

```
前端单页应用（原生 HTML/CSS/JS）
  ├── 登录页（选择角色）
  ├── 导师视图
  ├── 实习生视图
  └── HR 视图
        │
        ▼
FastAPI REST API
  ├── /api/auth        — 登录/角色
  ├── /api/intern      — 实习生数据
  ├── /api/mentor      — 导师操作
  └── /api/hr          — HR 仪表盘
        │
        ▼
SQLite 数据库
  ├── users            — 用户表
  ├── interns          — 实习生表
  ├── training_plan    — 带教计划模板
  └── progress_log     — 进度记录
```

## 数据模型

### users
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | |
| name | TEXT | 姓名 |
| role | TEXT | mentor / intern / hr |
| department | TEXT | 研发/产品/销售 (intern 专用) |
| mentor_id | INTEGER FK | 导师 ID (intern 专用) |
| position | TEXT | 具体岗位名 |
| start_date | TEXT | 入职日期 |
| stage | TEXT | 当前阶段: onboarding/growth/independent |

### training_plan
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | |
| department | TEXT | 研发/产品/销售 |
| stage | TEXT | onboarding/growth/independent |
| milestone_name | TEXT | 里程碑名称 |
| description | TEXT | 具体内容 |
| sort_order | INTEGER | 排序 |

### progress_log
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | |
| intern_id | INTEGER FK | |
| plan_id | INTEGER FK | 对应的带教计划条目 |
| mentor_id | INTEGER FK | 操作导师 |
| status | TEXT | pending/completed/flagged |
| mentor_feedback | TEXT | 导师反馈 |
| created_at | TEXT | 时间戳 |

## 功能模块

### 1. 登录页
- 预设 3 个演示账号（导师张伟 / 实习生李婷 / HR 王芳）
- 点选角色直接进入，无注册流程
- 也可切换账号

### 2. 导师视图
**页面 1：我的实习生列表**
- 卡片列表，显示姓名、岗位、当前阶段、最近进度
- 按阶段筛选（onboarding/growth/independent）
- 点击进入带教详情

**页面 2：带教计划详情**
- 实习生基本信息 + 当前阶段高亮
- 带教计划清单（按岗位类型加载），每项可勾选完成
- 完成时弹窗填写反馈
- 历史进度时间线

### 3. 实习生视图
**我的成长路径**
- 三阶段时间线可视化（入职适应 → 快速成长 → 独立贡献）
- 当前位置高亮 + 进度条
- 当前阶段目标清单（已完成灰色 + 待完成蓝色）
- 导师反馈展示
- 下一阶段预告

### 4. HR 视图
**页面 1：总览仪表盘**
- KPI 卡片行：总人数、各阶段人数、完成率、异常数
- 岗位分布（研发/产品/销售占比）
- 20 人状态列表（紧凑表格，阶段+进度一目了然）
- 异常标记（超期未完成阶段标红）

**页面 2：个人详情钻取**
- 点击任一实习生 → 查看成长轨迹详情
- 时间线 + 完成率 + 导师反馈历史

## 前端设计令牌

```
主色:      #0052d9
主色 hover: #366ef4
主色浅色:   #e8f0fe
页面底:    #f5f7fa
卡片白:    #ffffff
主文字:    #1d2129
次文字:    #4e5969
边框:      #e7e9ed
成功:      #00a870
警告:      #ed7b2f
错误:      #e34d59
字体:      'PingFang SC','Microsoft YaHei',system-ui
圆角:      6-12px
卡片阴影:  0 2px 12px rgba(0,0,0,0.06)
```

## 技术栈

- 后端：Python FastAPI + SQLAlchemy + SQLite
- 前端：原生 HTML/CSS/JS，单文件离线可用
- 图表：Chart.js（内嵌，不依赖 CDN）
- 交付：`python main.py` 一键启动

## 非功能需求

- Mock 数据：20 个实习生，3 个岗位类型分布
- 带教计划：每个岗位类型 3 个阶段 × 4-5 个里程碑
- 演示账号：1 导师 + 1 实习生 + 1 HR
- 所有数据预置，启动即用
