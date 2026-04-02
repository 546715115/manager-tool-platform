# Tool Hub - 研究发现

## 项目背景
- 用户需要一个工具管理平台
- 核心功能：配置工具、启动/停止、端口自动顺延
- UI：Organic Modern 风格（流体曲线、圆润部件、柔和泥土色调）

## 设计决策
1. **方案B**：Flask + SQLite + 独立进程管理
2. **端口检测**：PID文件 + socket扫描双重检测
3. **进程管理**：每个工具独立子进程

## 技术要点
- SQLite 是 Python 内置库，无需额外安装
- psutil 用于进程检测和管理
- socket 用于端口扫描
- Flask 提供 REST API

## 文件结构
```
manager-tool/
├── app.py              # Flask 主应用
├── models.py           # 数据库模型
├── process_manager.py  # 进程管理
├── port_scanner.py     # 端口扫描
├── templates/
│   └── index.html      # 前端页面
├── static/
│   └── style.css       # 样式
└── tools.db            # SQLite 数据库
```

---
*最后更新: 2026-04-02*
