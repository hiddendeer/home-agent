@echo off
REM 数据库迁移脚本 - 添加 last_hydration_remind_at 字段

echo ========================================
echo   数据库迁移
echo ========================================
echo.
echo 正在添加 last_hydration_remind_at 字段到 users 表...
echo.

cd /d %~dp0Home-backend

.venv\Scripts\activate
python scripts\add_hydration_field.py

echo.
echo ========================================
echo   迁移完成！
echo ========================================
echo.
pause
