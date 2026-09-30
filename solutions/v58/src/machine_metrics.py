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


def memory_pages(text: str) -> dict:
    """Expose page categories; non-cache usage is an estimate, not Activity Monitor's exact counter."""
    size = re.search(r"page size of (\d+) bytes", text)
    fields = {}
    for label in ("Anonymous pages", "Pages wired down", "Pages occupied by compressor",
                  "File-backed pages", "Pages free", "Pages speculative"):
        match = re.search(r"(?:\"?" + re.escape(label) + r"\"?):\s*(\d+)", text)
        fields[label] = int(match.group(1)) if match else None
    if not size or any(value is None for value in fields.values()):
        return {}
    page = int(size.group(1))
    return {"memory_noncache_estimate_bytes": page * (fields["Anonymous pages"] + fields["Pages wired down"] + fields["Pages occupied by compressor"]),
            "memory_file_cache_bytes": page * fields["File-backed pages"],
            "memory_compressed_resident_bytes": page * fields["Pages occupied by compressor"],
            "memory_wired_bytes": page * fields["Pages wired down"],
            "memory_unused_pages_bytes": page * (fields["Pages free"] + fields["Pages speculative"])}


def collect(project: Path) -> dict:
    result = {"sampled_at_utc": utc_now(), "platform": platform.system(), "cores": os.cpu_count(),
              "cpu_percent": None, "gpu_percent": None, "memory_total_bytes": None,
              "memory_pressure_free_percent": None, "swap_used_bytes": None,
              "gpu_shared_memory_bytes": None, "model_server_online": False,
              "models": [], "processes": []}
    if platform.system() == "Darwin":
        result["chip"] = (command(["sysctl", "-n", "machdep.cpu.brand_string"]) or "Apple Silicon").strip()
        total = command(["sysctl", "-n", "hw.memsize"])
        if total and total.strip().isdigit():
            result["memory_total_bytes"] = int(total.strip())
        page_stats = command(["vm_stat"])
        if page_stats:
            result.update(memory_pages(page_stats))
        top = command(["top", "-l", "2", "-s", "1", "-n", "0"], timeout=4)
        if top:
            matches = re.findall(r"CPU usage:\s*([\d.]+)% user,\s*([\d.]+)% sys", top)
            if matches:
                result["cpu_percent"] = sum(map(float, matches[-1]))
        pressure = command(["memory_pressure", "-Q"])
        if pressure:
            match = re.search(r"System-wide memory free percentage:\s*(\d+)%", pressure)
            if match:
                result["memory_pressure_free_percent"] = int(match.group(1))
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
