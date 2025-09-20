@echo off
title Snake Game Publisher
echo 🐍 Starting Snake Game Publisher...
echo.

REM Check if virtual environment exists
if exist ".venv\Scripts\python.exe" (
    echo ✅ Using virtual environment
    .venv\Scripts\python.exe publisher_gui.py
) else (
    echo ⚠️  Virtual environment not found, using system Python
    python publisher_gui.py
)

echo.
echo Publisher closed.
pause