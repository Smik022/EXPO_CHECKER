import uvicorn
from fastapi import FastAPI, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import webbrowser
from threading import Timer, Thread
import os
import time

# FIX: Explicitly set git path for Windows if not found
# This prevents "ImportError: Bad git executable"
if os.name == 'nt':
    # Common standard paths for Git on Windows
    possible_paths = [
        r"C:\Program Files\Git\cmd\git.exe",
        r"C:\Program Files\Git\bin\git.exe",
        r"C:\Users\%USERNAME%\AppData\Local\Programs\Git\cmd\git.exe",
    ]
    
    # If not already set, try to find it
    if "GIT_PYTHON_GIT_EXECUTABLE" not in os.environ:
        for path in possible_paths:
            expanded_path = os.path.expandvars(path)
            if os.path.exists(expanded_path):
                os.environ["GIT_PYTHON_GIT_EXECUTABLE"] = expanded_path
                break

from scanner import ExpoScanner

app = FastAPI(title="ExpoCheck API")

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# State Management (Simple In-Memory)
class GlobalState:
    def __init__(self):
        self.is_scanning = False
        self.progress = 0
        self.status_message = "Idle"
        self.findings = []
        self.error = None

state = GlobalState()

class ScanRequest(BaseModel):
    path: str

def run_scan_thread(path: str):
    global state
    state.is_scanning = True
    state.progress = 0
    state.findings = []
    state.error = None
    state.status_message = "Initializing scanner..."
    
    try:
        if not os.path.exists(path):
            raise ValueError("Path does not exist")

        scanner = ExpoScanner(path)
        for update in scanner.scan_history():
            if update["status"] == "progress":
                state.progress = update["percent"]
                state.status_message = update["message"]
            elif update["status"] == "finding":
                state.findings.append(update["data"])
            elif update["status"] == "complete":
                state.progress = 100
                state.status_message = "Scan Complete"
                
    except Exception as e:
        state.error = str(e)
        state.status_message = "Error"
    finally:
        state.is_scanning = False

@app.get("/api/status")
async def get_status():
    return {
        "is_scanning": state.is_scanning,
        "progress": state.progress,
        "message": state.status_message,
        "findings_count": len(state.findings),
        "error": state.error
    }

@app.get("/api/results")
async def get_results():
    return state.findings

@app.post("/api/scan")
async def start_scan(request: ScanRequest, background_tasks: BackgroundTasks):
    if state.is_scanning:
        return {"status": "error", "message": "Scan already in progress"}
    
    # Run in background thread so we don't block the API
    t = Thread(target=run_scan_thread, args=(request.path,))
    t.start()
    
    return {"status": "started"}

# Serve Frontend
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

def start_browser():
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    Timer(1.5, start_browser).start()
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
