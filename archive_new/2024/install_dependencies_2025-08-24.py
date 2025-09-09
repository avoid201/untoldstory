#!/usr/bin/env python3
"""
Installation helper for Type System Migration
Ensures all dependencies are available
"""

import subprocess
import sys
import os

def run_command(cmd):
    """Run a shell command and return output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_numpy():
    """Check if NumPy is installed."""
    try:
        import numpy as np
        return True, np.__version__
    except ImportError:
        return False, None

def install_numpy():
    """Try to install NumPy."""
    print("📦 NumPy not found. Attempting to install...")
    
    # Try pip3 first
    success, out, err = run_command("pip3 install numpy --user")
    if success:
        print("✅ NumPy installed successfully with pip3")
        return True
    
    # Try pip
    success, out, err = run_command("pip install numpy --user")
    if success:
        print("✅ NumPy installed successfully with pip")
        return True
    
    # Try python3 -m pip
    success, out, err = run_command("python3 -m pip install numpy --user")
    if success:
        print("✅ NumPy installed successfully with python3 -m pip")
        return True
    
    print("❌ Could not install NumPy automatically")
    print("Please install manually with: pip install numpy")
    return False

def main():
    print("=" * 70)
    print("TYPE SYSTEM MIGRATION - DEPENDENCY CHECK")
    print("=" * 70)
    print()
    
    # Check Python version
    print(f"Python version: {sys.version}")
    print()
    
    # Check NumPy
    has_numpy, version = check_numpy()
    
    if has_numpy:
        print(f"✅ NumPy is installed (version {version})")
    else:
        if install_numpy():
            # Verify installation
            has_numpy, version = check_numpy()
            if has_numpy:
                print(f"✅ NumPy is now available (version {version})")
            else:
                print("⚠️  NumPy installed but not yet available. Please restart Python.")
        else:
            print("\n⚠️  FALLBACK MODE")
            print("The optimized type system requires NumPy for best performance.")
            print("You can still use the system, but with reduced performance.")
            print("\nTo install NumPy manually:")
            print("  macOS: pip3 install numpy")
            print("  or: python3 -m pip install numpy")
    
    print()
    print("=" * 70)
    
    # Run validation
    if has_numpy:
        print("\n🧪 Running validation tests...")
        os.system("python3 validate_migration.py")
    else:
        print("\n⚠️  Skipping validation tests (NumPy required)")
        print("The type system will work but without performance optimizations.")

if __name__ == "__main__":
    main()