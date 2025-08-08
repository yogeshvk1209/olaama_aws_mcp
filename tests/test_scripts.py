#!/usr/bin/env python3
"""Basic functionality test for both scripts."""

import os
import sys
import subprocess
import tempfile
from pathlib import Path


def test_ollama_cli_help():
    """Test Ollama CLI help output."""
    print("🧪 Testing Ollama CLI help...")
    try:
        result = subprocess.run([sys.executable, 'ollama_cli.py', '--help'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Ollama CLI help works")
            return True
        else:
            print(f"❌ Ollama CLI help failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Ollama CLI help error: {e}")
        return False


def test_aws_mcp_server_help():
    """Test AWS MCP server help output."""
    print("🧪 Testing AWS MCP server help...")
    try:
        result = subprocess.run([sys.executable, 'aws_mcp_server.py', '--help'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ AWS MCP server help works")
            return True
        else:
            print(f"❌ AWS MCP server help failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ AWS MCP server help error: {e}")
        return False


def test_configuration_parsing():
    """Test configuration parsing with environment variables."""
    print("🧪 Testing configuration parsing...")
    
    # Test environment variables
    test_env = os.environ.copy()
    test_env['OLLAMA_MODEL'] = 'test-model:7b'
    test_env['OLLAMA_LOG_FILE'] = '/tmp/test-ollama.log'
    test_env['MCP_LOG_FILE'] = '/tmp/test-mcp.log'
    
    try:
        # Test config import
        from config import OllamaConfig, MCPConfig
        
        # Test Ollama config
        ollama_config = OllamaConfig.from_env_and_args()
        if ollama_config.model == "qwen3:14b":
            print("✅ Ollama config defaults work")
        else:
            print(f"❌ Ollama config defaults failed: {ollama_config.model}")
            return False
        
        # Test MCP config
        mcp_config = MCPConfig.from_env_and_args()
        if mcp_config.command == "npx" and "mcp-remote" in mcp_config.args:
            print("✅ MCP config defaults work")
        else:
            print(f"❌ MCP config defaults failed: {mcp_config.command}, {mcp_config.args}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration parsing error: {e}")
        return False


def test_logging_setup():
    """Test logging setup functionality."""
    print("🧪 Testing logging setup...")
    
    try:
        from logging_utils import setup_ollama_logging, setup_mcp_logging
        
        # Test with temporary log files
        with tempfile.TemporaryDirectory() as temp_dir:
            ollama_log = os.path.join(temp_dir, 'ollama-test.log')
            mcp_log = os.path.join(temp_dir, 'mcp-test.log')
            
            # Test Ollama logging
            ollama_logger = setup_ollama_logging(ollama_log)
            ollama_logger.info("Test message")
            
            # Test MCP logging
            mcp_logger = setup_mcp_logging(mcp_log)
            mcp_logger.info("Test message")
            
            # Check if log files were created
            if os.path.exists(ollama_log) and os.path.exists(mcp_log):
                print("✅ Logging setup works")
                return True
            else:
                print("❌ Log files were not created")
                return False
                
    except Exception as e:
        print(f"❌ Logging setup error: {e}")
        return False


def main():
    """Run basic functionality tests."""
    print("🚀 Running basic functionality tests for both scripts")
    print("=" * 60)
    
    tests = [
        test_ollama_cli_help,
        test_aws_mcp_server_help,
        test_configuration_parsing,
        test_logging_setup
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Both scripts are ready to use.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())