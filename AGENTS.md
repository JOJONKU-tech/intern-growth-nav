# Multi-Agent Workflow v2

## Roles
- be (DeepSeek V4): PM + 后端，主导 Research/Plan 阶段
- fe (MiniMax M3): 前端 UI，Work 阶段执行前端任务

## Protocol
- 默认 agent 是 be
- UI/视觉/前端任务 → 委派 fe 子代理
- 后端任务 → be 子代理执行

## 设计规范（本项目）
- TDesign × 腾讯校招风格（浅色模式）
- 主色 #0052d9，底色 #f5f7fa，卡片白 #ffffff
- 字体 PingFang SC / Microsoft YaHei / system-ui
- 圆角 6-12px，轻阴影
- HTML 单文件离线可用，不依赖 CDN
- onclick 绑定，不 addEventListener
- 无 emoji、无 AI 标签、无渐变泛滥
