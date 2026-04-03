@echo off
cd /d "%~dp0"
echo 正在关闭 CES测试工具管理平台...
powershell -Command "Get-CimInstance Win32_Process | Where-Object {$_.Name -eq 'python.exe' -and $_.CommandLine -like '*manager-tool*'} | Stop-Process -Force"
echo 已关闭
