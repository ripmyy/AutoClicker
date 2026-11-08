"""
Build script to compile AutoClicker Reimagined into a standalone Windows .exe
using PyInstaller.
"""

import os
import sys
import shutil
import subprocess
import customtkinter

def build():
    print("=" * 60)
    print("Building AutoClicker Reimagined Standalone Executable (.exe)")
    print("=" * 60)

    # Path to customtkinter package assets
    ctk_path = os.path.dirname(customtkinter.__file__)
    print(f"[+] CustomTkinter path: {ctk_path}")

    # Build command
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed",
        "--name=AutoClickerReimagined",
        "--icon=assets/icon.ico",
        f"--add-data=assets;assets",
        f"--add-data={ctk_path};customtkinter",
        "--hidden-import=pynput.keyboard",
        "--hidden-import=pynput.mouse",
        "--hidden-import=keyboard",
        "--hidden-import=psutil",
        "main.py",
    ]

    print("[+] Executing PyInstaller:")
    print(" ".join(cmd))
    result = subprocess.run(cmd)

    if result.returncode == 0:
        exe_path = os.path.abspath(os.path.join("dist", "AutoClickerReimagined.exe"))
        print("\n" + "=" * 60)
        print(" BUILD SUCCESSFUL!")
        print(f" Executable created at: {exe_path}")
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f" File Size: {size_mb:.2f} MB")
        print("=" * 60)
    else:
        print("\n[-] Build failed with exit code:", result.returncode)
        sys.exit(result.returncode)

if __name__ == "__main__":
    build()
