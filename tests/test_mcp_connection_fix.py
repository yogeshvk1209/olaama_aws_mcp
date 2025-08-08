#!/usr/bin/env python3
"""Test the MCP connection fix."""

import sys
import time
from unittest.mock import patch

def test_mcp_connection_status():
    """Test MCP connection status with and without auto-start."""
    print("🧪 Testing MCP Connection Status Fix")
    print("=" * 50)
    
    # Mock input to prevent interactive session
    def mock_input(prompt):
        print(f"[MOCK INPUT] {prompt}")
        return "quit"
    
    try:
        # Test without auto-start (should show disconnected)
        print("1. Testing without --start-mcp-now (should show disconnected):")
        with patch('builtins.input', side_effect=mock_input):
            from ollama_cli import main
            original_argv = sys.argv
            sys.argv = ['ollama_cli.py', '--log-dir', './test-logs']
            
            try:
                main()
            except (KeyboardInterrupt, SystemExit):
                pass
            finally:
                sys.argv = original_argv
        
        print("\n" + "="*50)
        
        # Test with auto-start (should show connected)
        print("2. Testing with --start-mcp-now (should show connected):")
        with patch('builtins.input', side_effect=mock_input):
            sys.argv = ['ollama_cli.py', '--start-mcp-now', '--log-dir', './test-logs']
            
            try:
                main()
            except (KeyboardInterrupt, SystemExit):
                pass
            finally:
                sys.argv = original_argv
        
        print("\n✅ MCP connection status test completed!")
        print("\nTo see the difference in your manual testing:")
        print("  python3 ollama_cli.py                    # Shows 🔴 Disconnected")
        print("  python3 ollama_cli.py --start-mcp-now    # Shows 🟢 Connected")
        
        return True
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

if __name__ == "__main__":
    success = test_mcp_connection_status()
    sys.exit(0 if success else 1)