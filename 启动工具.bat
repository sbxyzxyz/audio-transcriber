@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
    echo 首次运行，正在安装依赖，请稍候...
    python -m venv .venv
    .venv\Scripts\pip install -r requirements.txt
)
start "" .venv\Scripts\pythonw.exe app.py
