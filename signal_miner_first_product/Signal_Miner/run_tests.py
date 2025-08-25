#!/usr/bin/env python3
"""
Test runner for GrowthSignal modules
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a command and print results"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('='*60)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✅ SUCCESS")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ FAILED")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False

def main():
    """Run all tests and checks"""
    # Change to Signal_Miner directory
    signal_miner_dir = Path(__file__).parent
    os.chdir(signal_miner_dir)
    
    print("🚀 GrowthSignal Test Suite")
    print(f"Working directory: {os.getcwd()}")
    
    # Check if we're in the right directory
    if not Path("signal_miner.py").exists():
        print("❌ Error: signal_miner.py not found. Please run from Signal_Miner directory.")
        sys.exit(1)
    
    # Install dependencies if needed
    print("\n📦 Checking dependencies...")
    try:
        import pytest
        import flake8
        import bandit
        print("✅ All dependencies available")
    except ImportError:
        print("📥 Installing dependencies...")
        run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                   "Installing dependencies")
    
    # Run tests
    success = True
    
    # Unit tests
    success &= run_command([
        sys.executable, "-m", "pytest", 
        "rfg/tests/", "executor/tests/",
        "-v", "--tb=short", "--cov=rfg", "--cov=executor",
        "--cov-report=term-missing"
    ], "Unit Tests with Coverage")
    
    # Linting
    success &= run_command([
        sys.executable, "-m", "flake8",
        "rfg/", "executor/",
        "--count", "--select=E9,F63,F7,F82", "--show-source", "--statistics"
    ], "Linting (Critical Errors)")
    
    success &= run_command([
        sys.executable, "-m", "flake8",
        "rfg/", "executor/",
        "--count", "--exit-zero", "--max-complexity=10", "--max-line-length=127", "--statistics"
    ], "Linting (Style Warnings)")
    
    # Security checks
    success &= run_command([
        sys.executable, "-m", "bandit",
        "-r", "rfg/", "executor/",
        "-f", "txt"
    ], "Security Checks")
    
    # Summary
    print(f"\n{'='*60}")
    if success:
        print("🎉 All checks passed!")
        sys.exit(0)
    else:
        print("❌ Some checks failed. Please review the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
