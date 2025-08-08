#!/usr/bin/env python3
"""Test CLI startup without interactive session."""

import sys
import os
import signal
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch, Mock

# Mock input to prevent interactive session
def mock_input(prompt):
    print(f"[MOCK INPUT] {prompt}")
    # Simulate quit command
    return "quit"

def test_cli_startup():
    """Test CLI startup process."""
    print("🧪 Testing CLI Startup Process")
    print("=" * 50)
    
    try:
        # Mock the input function to prevent interactive session
        with patch('builtins.input', side_effect=mock_input):
            # Import and run the main function
            from ollama_cli import main
            
            # Mock sys.argv to simulate command line args
            original_argv = sys.argv
            sys.argv = ['ollama_cli.py', '--no-mcp', '--log-dir', './test-logs']
            
            try:
                main()
                print("✅ CLI startup completed successfully")
                return True
            except KeyboardInterrupt:
                print("✅ CLI startup completed (interrupted as expected)")
                return True
            except SystemExit as e:
                if e.code == 0:
                    print("✅ CLI startup completed with clean exit")
                    return True
                else:
                    print(f"❌ CLI startup failed with exit code: {e.code}")
                    return False
            finally:
                sys.argv = original_argv
                
    except Exception as e:
        print(f"❌ CLI startup error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_cli_startup()
    sys.exit(0 if success else 1)