@echo off
setlocal
cd /d "%~dp0"

echo [Emiliano Job Hunter] Starting Candidate Tracking System (CTS)...

if exist "src-tauri\target\release\emiliano-job-hunter.exe" (
    start "" "src-tauri\target\release\emiliano-job-hunter.exe"
    exit /b 0
)

if exist "src-tauri\target\debug\emiliano-job-hunter.exe" (
    start "" "src-tauri\target\debug\emiliano-job-hunter.exe"
    exit /b 0
)

echo [Emiliano Job Hunter] Standalone binary not found. Launching via Python browser runner...
python run_job_hunter.py
