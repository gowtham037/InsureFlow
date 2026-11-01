#!/usr/bin/env python3
"""
InsureFlow Standalone Runner
Runs the InsureFlow platform locally using Python and built-in SQLite without Docker.
"""

import sys
import os
import webbrowser

# Add project root and backend to Python path
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, "backend"))

# Configure standalone environment variables
os.environ.setdefault("ENVIRONMENT", "standalone")
os.environ.setdefault("DATABASE_URL", f"sqlite:///{os.path.join(ROOT_DIR, 'insureflow.db')}")
os.environ.setdefault("AUTO_SEED_ON_STARTUP", "true")
os.environ.setdefault("DATA_GEN_SEED", "20261022")


def main():
    print("\n========================================================")
    print("           InsureFlow Standalone Evaluation Runner      ")
    print("========================================================")
    print("• Runtime Mode    : Standalone (Zero-Docker)")
    print("• Database Engine : SQLite (insureflow.db)")
    print("• Auto-Seeding    : Enabled (Seed: 20261022)")
    print("• API & Docs URL  : http://localhost:8000/docs")
    print("• Health Probe    : http://localhost:8000/health")
    print("========================================================\n")

    try:
        import uvicorn
        from backend.app.main import app
    except ImportError as e:
        print(f"\n[ERROR] Missing required Python dependency: {e}")
        print("Please install requirements first:")
        print("    pip install -r backend/requirements.txt\n")
        sys.exit(1)

    host = "127.0.0.1"
    port = int(os.getenv("PORT", 8000))

    print(f"Starting InsureFlow backend server at http://{host}:{port} ...")
    uvicorn.run("backend.app.main:app", host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
