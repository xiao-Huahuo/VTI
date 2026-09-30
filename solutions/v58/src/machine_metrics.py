"""Local machine observations, never used to alter experimental model settings."""
from __future__ import annotations

import json
import os
import platform
import re
import shutil
import subprocess
import urllib.request
from pathlib import Path

from journal import utc_now


def command(args: list[str], timeout: float = 3) -> str | None:
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        return result.stdout if result.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def collect(project: Path) -> dict:
    result = {"sampled_at_utc": utc_now(), "platform": platform.system(), "cores": os.cpu_count(),
              "cpu_percent": None, "gpu_percent": None, "memory_total_bytes": None,
              "memory_available_percent": None, "swap_used_bytes": None,
              "gpu_shared_memory_bytes": None, "model_server_online": False,
              "models": [], "processes": []}
    if platform.system() == "Darwin":
        result["chip"] = (command(["sysctl", "-n", "machdep.cpu.brand_string"]) or "Apple Silicon").strip()
        total = command(["sysctl", "-n", "hw.memsize"])
        if total and total.strip().isdigit():
            result["memory_total_bytes"] = int(total.strip())
        top = command(["top", "-l", "2", "-s", "1", "-n", "0"], timeout=4)
        if top:
            matches = re.findall(r"CPU usage:\s*([\d.]+)% user,\s*([\d.]+)% sys", top)
            if matches:
                result["cpu_percent"] = sum(map(float, matches[-1]))
        pressure = command(["memory_pressure", "-Q"])
        if pressure:
            match = re.search(r"System-wide memory free percentage:\s*(\d+)%", pressure)
            if match:
                result["memory_available_percent"] = int(match.group(1))
        swap = command(["sysctl", "vm.swapusage"])
        if swap:
            match = re.search(r"used\s*=\s*([\d.]+)([MG])", swap)
            if match:
                result["swap_used_bytes"] = float(match.group(1)) * (1024 ** (2 if match.group(2) == "M" else 3))
        gpu = command(["ioreg", "-r", "-c", "AGXAccelerator", "-l"])
        if gpu:
            utilization = re.findall(r'"Device Utilization %"=(\d+)', gpu)
            memory = re.findall(r'"In use system memory"=(\d+)', gpu)
            result["gpu_percent"] = max(map(int, utilization)) if utilization else None
            result["gpu_shared_memory_bytes"] = sum(map(int, memory)) if memory else None
    result["load_average"] = list(os.getloadavg()) if hasattr(os, "getloadavg") else None
    disk = shutil.disk_usage(project)
    result["disk"] = {"total_bytes": disk.total, "used_bytes": disk.used, "free_bytes": disk.free}
    process_text = command(["ps", "-axo", "pid=,pcpu=,rss=,args="])
    if process_text:
        for line in process_text.splitlines():
            parts = line.strip().split(None, 3)
            if len(parts) != 4:
                continue
            cmd = parts[3]
            label = ("V58 runner" if "/src/runner.py" in cmd else
                     "Ollama" if "ollama serve" in cmd else
                     "Qwen 推理进程" if "llama-server --model" in cmd else None)
            if label:
                try:
                    result["processes"].append({"pid": int(parts[0]), "label": label,
                                                "cpu_percent": float(parts[1]), "rss_bytes": int(parts[2]) * 1024})
                except ValueError:
                    pass
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open("http://127.0.0.1:11434/api/ps", timeout=1) as response:
            payload = json.load(response)
        result["model_server_online"] = True
        result["models"] = [{key: model.get(key) for key in
                             ("name", "digest", "size", "size_vram", "context_length")}
                            for model in payload.get("models", [])]
    except (OSError, ValueError):
        pass
    return result
