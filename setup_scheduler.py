"""
Run this script ONCE (as Administrator) to schedule the daily report.
The report will be sent automatically every day at the time defined below.
"""
import subprocess
import sys
import os

SEND_TIME = "15:55"  # <- Change this to set the daily send time (HH:MM)


def setup():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(project_dir, "main.py")
    python_exe = sys.executable
    task_name = "MarketReporter"

    # Remove existing task if any
    subprocess.run(
        ["schtasks", "/delete", "/tn", task_name, "/f"],
        capture_output=True,
    )

    cmd = [
        "schtasks", "/create",
        "/tn", task_name,
        "/tr", f'"{python_exe}" "{main_script}"',
        "/sc", "DAILY",
        "/st", SEND_TIME,
        "/rl", "HIGHEST",
        "/f",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"✓ Scheduled task created: '{task_name}'")
        print(f"  Report will be sent daily at {SEND_TIME}")
        print(f"  Python: {python_exe}")
        print(f"  Script: {main_script}")
    else:
        print(f"✗ Failed to create scheduled task:")
        print(result.stderr)
        print("\nTry running this script as Administrator.")


if __name__ == "__main__":
    setup()
