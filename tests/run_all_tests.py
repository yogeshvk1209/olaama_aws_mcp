#!/usr/bin/env python3
"""Run all tests for Enhanced Ollama CLI with MCP Integration."""

import sys
import os
import subprocess
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def run_test_file(test_file: str) -> bool:
    """Run a single test file and return success status."""
    print(f"\n🧪 Running {test_file}")
    print("=" * 60)
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            cwd=Path(__file__).parent,
            capture_output=False,
            text=True
        )
        
        success = result.returncode == 0
        if success:
            print(f"✅ {test_file} passed")
        else:
            print(f"❌ {test_file} failed")
        
        return success
        
    except Exception as e:
        print(f"❌ Error running {test_file}: {e}")
        return False

def main():
    """Run all test files."""
    print("🚀 Running All Tests - Enhanced Ollama CLI with MCP Integration")
    print("=" * 80)
    
    # List of test files to run
    test_files = [
        "test_aws_detection.py",
        "test_mcp_client.py", 
        "test_context_enhancer.py",
        "test_enhanced_ollama.py",
        "test_config_system.py",
        "test_enhanced_cli.py",
        "test_integrated_cli.py",
        "test_startup.py",
        "integration_test_suite.py"
    ]
    
    passed = 0
    total = len(test_files)
    
    for test_file in test_files:
        if run_test_file(test_file):
            passed += 1
    
    print("\n" + "=" * 80)
    print(f"📊 Overall Test Results: {passed}/{total} test files passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Enhanced Ollama CLI with MCP Integration is fully validated")
        return True
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)