@echo off
cd /d "%~dp0"
echo 启动 CES测试工具管理平台...
start "" http://localhost:5000
python app.py
