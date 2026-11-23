import csv
import os
import platform
import subprocess
import psutil
from datetime import datetime

LOG = os.path.join ("logs", "telemetry.csv")

FIELDS = ["timestamp", "model", "param_size", "quantisation", "prompt_tokens", "tokens_generated", "response_s", "load_s", "tokens_per_s", "os", "cpu", "gpu", "ram_gb"]


def get_cpu():
    try:
        out = subprocess.check_output(
            ["powershell", "-NoProfile", "-Command",
             "(Get-CimInstance Win32_Processor).Name"],
            text=True, timeout=10)
        return out.strip().splitlines()[0]
    except Exception:
        return platform.processor() or "unknown"


def get_gpu():
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            text=True, timeout=10)
        return out.strip().splitlines()[0]
    except Exception:
        return "unknown"


CPU = get_cpu()
GPU = get_gpu()
OS = f"{platform.system()}"
RAM_GB = round(psutil.virtual_memory().total / 1e9, 1)


def log(row: dict):
    os.makedirs("logs", exist_ok=True)
    new_file = not os.path.exists(LOG)
    with open(LOG, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            writer.writeheader()
        writer.writerow({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "os": OS,
            "cpu": CPU,
            "gpu": GPU,
            "ram_gb": RAM_GB,
            **row,
        })
