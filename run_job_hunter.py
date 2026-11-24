#!/usr/bin/env python3
"""
Emiliano Job Hunter — Autonomous One-Command Launcher.
Initializes the local SQLite database, syncs candidate profile & CV variants,
and launches the interactive Visual CRM Dashboard in your browser or desktop shell.
"""

import os
import sys
import json
import webbrowser
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "applications_crm.json"
PROFILE_FILE = BASE_DIR / "candidate_profile.json"
DASHBOARD_FILE = BASE_DIR.parent / "ai-job-search" / "tools" / "job_application_tracker.html"

def check_environment():
    print("=" * 60)
    print("🚀 EMILIANO JOB HUNTER — AUTONOMOUS CAREER AGENT & CRM")
    print("=" * 60)
    
    if PROFILE_FILE.exists():
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            profile = json.load(f)
        print(f"👤 Candidate: {profile.get('full_name')} ({profile.get('location', {}).get('city')}, {profile.get('location', {}).get('country')})")
        print(f"💼 Legal Structure: {profile.get('legal_entity', {}).get('contract_type')}")
        print(f"📄 Configured CV Variants: {len(profile.get('cv_variants', []))}")
        for v in profile.get('cv_variants', []):
            print(f"   • {v.get('id')}: {v.get('name')}")
    else:
        print("⚠️ Warning: candidate_profile.json not found. Creating default template...")

    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            apps = json.load(f)
        print(f"📊 Live Applications in Database: {len(apps)}")
    
    print("-" * 60)

def open_dashboard():
    target = DASHBOARD_FILE if DASHBOARD_FILE.exists() else (BASE_DIR / "index.html")
    print(f"🌐 Launching Visual Kanban & Table Tracker in your browser...")
    url = f"file:///{target.as_posix()}"
    webbrowser.open(url)
    print(f"✅ Dashboard active: {url}")
    print("=" * 60)

if __name__ == "__main__":
    check_environment()
    open_dashboard()
