import subprocess
import sys


def run_dev():
    # 1. Start Tailwind Watcher (Standalone CLI via Python wrapper)
    # Using v4 logic as established
    tailwind_cmd = [
        "tailwindcss",
        "-i",
        "./static/css/input.css",
        "-o",
        "./static/css/output.css",
        "--watch",
    ]

    # 2. Start FastAPI Server
    server_cmd = [sys.executable, "main.py"]

    try:
        tailwind_proc = subprocess.Popen(tailwind_cmd)
        server_proc = subprocess.Popen(server_cmd)

        tailwind_proc.wait()
        server_proc.wait()
    except KeyboardInterrupt:
        tailwind_proc.terminate()
        server_proc.terminate()


if __name__ == "__main__":
    run_dev()
