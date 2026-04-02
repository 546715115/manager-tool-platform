# Tool Hub - 工具管理平台设计文档

## 1. 项目概述

- **项目名称**：Tool Hub
- **类型**：Flask Web 应用
- **核心功能**：管理本地工具的启动/停止/监控，通过 Web UI 统一调度
- **目标用户**：个人开发者/小团队

## 2. 系统架构

```
┌─────────────────┐     HTTP      ┌─────────────────┐
│   前端 (HTML)   │ ◄──────────► │   Flask API     │
│   Organic UI    │              │   localhost     │
└─────────────────┘              └────────┬────────┘
                                           │
              ┌────────────────────────────┼────────────────────────────┐
              │                            │                            │
              ▼                            ▼                            ▼
      ┌───────────────┐          ┌─────────────────┐          ┌─────────────┐
      │    SQLite     │          │  Process Manager │          │   Port      │
      │  tools.db     │          │   (subprocess    │          │  Scanner    │
      │               │          │    + psutil)     │          │  (socket)   │
      └───────────────┘          └────────┬─────────┘          └─────────────┘
                                           │
                                           ▼
                                   ┌───────────────┐
                                   │  Child Process │
                                   │  (独立进程)    │
                                   └───────────────┘
```

## 3. 技术栈

| 组件 | 技术 |
|------|------|
| 前端 | HTML + CSS + Vanilla JS (Organic Modern UI) |
| 后端 | Python Flask |
| 数据库 | SQLite (Python 内置) |
| 进程管理 | subprocess + psutil |
| 端口检测 | socket |

## 4. 数据库结构

**表：tools**

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | INTEGER PRIMARY KEY | 主键 |
| `name` | TEXT NOT NULL | 工具名称 |
| `cmd` | TEXT NOT NULL | 启动命令 |
| `port` | INTEGER NOT NULL | 默认端口 |
| `url` | TEXT | 访问URL |
| `pid` | INTEGER | 进程ID（NULL=未运行） |
| `status` | TEXT DEFAULT 'stopped' | running/stopped/error |
| `created_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP | 创建时间 |

## 5. API 设计

### 5.1 工具管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/tools` | 获取所有工具列表 |
| GET | `/api/tools/<id>` | 获取单个工具 |
| POST | `/api/tools` | 新增工具 |
| PUT | `/api/tools/<id>` | 更新工具 |
| DELETE | `/api/tools/<id>` | 删除工具 |

### 5.2 进程控制

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/tools/<id>/start` | 启动工具 |
| POST | `/api/tools/<id>/stop` | 停止工具 |
| GET | `/api/tools/<id>/status` | 获取运行状态 |

### 5.3 端口检测

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/ports/check/<port>` | 检测端口是否可用 |
| GET | `/api/ports/find-available/<base_port>` | 查找空闲端口 |

## 6. 核心逻辑

### 6.1 启动工具

1. 检查 PID 文件是否存在
2. 如果 PID 存在，检查进程是否真的在运行
3. 检测目标端口是否被占用
4. 如果端口被占用，自动顺延找下一个空闲端口
5. 执行启动命令，启动独立子进程
6. 更新数据库：记录 PID、实际端口、状态

### 6.2 停止工具

1. 读取 PID
2. 发送 SIGTERM 信号
3. 等待进程退出（超时强制 SIGKILL）
4. 更新数据库：PID 置 NULL、状态改为 stopped

### 6.3 端口顺延逻辑

```
1. 检查端口是否可用（socket 连接测试）
2. 如果不可用，port += 1
3. 重复直到找到可用端口或达到最大尝试次数
4. 返回实际使用的端口
```

## 7. 前端交互

### 7.1 页面布局

- 单页应用，左侧工具卡片网格
- 点击工具卡片显示详情
- 弹窗编辑/新增工具
- 启动后点击 URL 直接跳转

### 7.2 状态显示

| 状态 | 显示 |
|------|------|
| stopped | 灰色圆点 + "启动" 按钮 |
| running | 绿色圆点 + "停止" 按钮 + "打开" 按钮 |
| starting | 橙色圆点 + "启动中..." |
| error | 红色圆点 + 错误提示 |

## 8. 文件结构

```
manager-tool/
├── app.py              # Flask 主应用
├── models.py           # 数据库模型
├── process_manager.py  # 进程管理模块
├── port_scanner.py     # 端口扫描模块
├── templates/
│   └── index.html      # 前端页面 (Organic Modern UI)
├── static/
│   └── style.css       # 样式文件
├── tools.db            # SQLite 数据库（自动创建）
└── requirements.txt    # 依赖列表
```

## 9. 验收标准

1. 前端页面可正常加载，显示工具列表
2. 可新增/编辑/删除工具
3. 点击启动，工具进程在后台运行
4. 端口被占用时自动顺延
5. 启动后显示实际端口和 URL
6. 点击 URL 可跳转
7. 可停止运行中的工具
8. 进程重启后能正确读取状态
