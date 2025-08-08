#!/usr/bin/env python3
"""Test the new log directory functionality."""

import os
import tempfile
from config import OllamaConfig, MCPConfig
from pathlib import Path


def test_log_dir_functionality():
    """Test the central log directory functionality."""
    print("🧪 Testing central log directory functionality...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test environment variable
        os.environ['LOG_DIR'] = temp_dir
        
        # Test Ollama config
        ollama_config = OllamaConfig.from_env_and_args()
        expected_ollama_log = str(Path(temp_dir) / 'ollama-cli.log')
        
        if ollama_config.log_file == expected_ollama_log:
            print(f"✅ Ollama log path: {ollama_config.log_file}")
        else:
            print(f"❌ Ollama log path mismatch: {ollama_config.log_file} != {expected_ollama_log}")
            return False
        
        # Test MCP config
        mcp_config = MCPConfig.from_env_and_args()
        expected_mcp_log = str(Path(temp_dir) / 'aws-mcp-server.log')
        
        if mcp_config.log_file == expected_mcp_log:
            print(f"✅ MCP log path: {mcp_config.log_file}")
        else:
            print(f"❌ MCP log path mismatch: {mcp_config.log_file} != {expected_mcp_log}")
            return False
        
        # Clean up environment
        del os.environ['LOG_DIR']
        
        return True


def test_priority_order():
    """Test the priority order: command args > env vars > defaults."""
    print("🧪 Testing priority order...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Set environment variable
        os.environ['LOG_DIR'] = temp_dir
        
        # Create mock args with log_dir
        class MockArgs:
            def __init__(self):
                self.log_dir = '/custom/path'
                self.log_file = None
                self.model = None
                self.ollama_url = None
                self.command = None
                self.working_dir = None
        
        args = MockArgs()
        
        # Test Ollama config with command line override
        ollama_config = OllamaConfig.from_env_and_args(args)
        expected_path = '/custom/path/ollama-cli.log'
        
        if ollama_config.log_file == expected_path:
            print(f"✅ Command line override works: {ollama_config.log_file}")
        else:
            print(f"❌ Command line override failed: {ollama_config.log_file} != {expected_path}")
            return False
        
        # Clean up
        del os.environ['LOG_DIR']
        
        return True


if __name__ == "__main__":
    print("🚀 Testing new log directory functionality")
    print("=" * 50)
    
    success = True
    success &= test_log_dir_functionality()
    print()
    success &= test_priority_order()
    
    print("=" * 50)
    if success:
        print("🎉 All log directory tests passed!")
    else:
        print("❌ Some tests failed!")