# -*- coding: utf-8 -*-
"""
Script to install project dependencies from requirements.pro.txt.
"""
import subprocess
import sys

def install_dependencies():
    print("Installing dependencies from requirements.pro.txt...")
    try:
        # Use pip to install dependencies
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.pro.txt"])
        print("All dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: requirements.pro.txt not found. Please ensure it's in the project root.")
        sys.exit(1)

if __name__ == "__main__":
    install_dependencies()
