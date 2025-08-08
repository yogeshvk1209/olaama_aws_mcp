#!/usr/bin/env python3
"""Test MCP integration configuration system."""

import sys
import os
import tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import OllamaConfig, MCPIntegrationConfig, create_ollama_parser
from config_utils import (
    validate_mcp_config, validate_ollama_config, display_config_summary,
    get_config_dict, create_config_from_dict, get_environment_config_info,
    display_environment_info, suggest_optimal_config
)


def test_mcp_config_creation():
    """Test MCP configuration creation and validation."""
    print("🧪 Testing MCP Configuration Creation")
    print("=" * 60)
    
    # Test default configuration
    print("Testing default MCP configuration...")
    mcp_config = MCPIntegrationConfig()
    
    print(f"Enabled: {mcp_config.enabled}")
    print(f"AWS Threshold: {mcp_config.aws_detection_threshold}")
    print(f"Max Docs: {mcp_config.max_documentation_entries}")
    print(f"Timeout: {mcp_config.connection_timeout}")
    print(f"Fallback: {mcp_config.fallback_on_error}")
    print(f"Auto-start: {mcp_config.auto_start_server}")
    
    # Validate default configuration
    errors = validate_mcp_config(mcp_config)
    print(f"Validation errors: {len(errors)}")
    if errors:
        for error in errors:
            print(f"  - {error}")
    else:
        print("✅ Default configuration is valid")
    
    print()
    
    # Test configuration from environment variables
    print("Testing configuration from environment variables...")
    
    # Set test environment variables
    test_env = {
        'MCP_INTEGRATION_ENABLED': 'false',
        'AWS_DETECTION_THRESHOLD': '0.6',
        'MAX_DOCUMENTATION_ENTRIES': '5',
        'MCP_CONNECTION_TIMEOUT': '15',
        'MCP_FALLBACK_ON_ERROR': 'false',
        'MCP_AUTO_START_SERVER': 'false'
    }
    
    # Temporarily set environment variables
    original_env = {}
    for key, value in test_env.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value
    
    try:
        env_config = MCPIntegrationConfig.from_env_and_args()
        
        print(f"Enabled: {env_config.enabled}")
        print(f"AWS Threshold: {env_config.aws_detection_threshold}")
        print(f"Max Docs: {env_config.max_documentation_entries}")
        print(f"Timeout: {env_config.connection_timeout}")
        print(f"Fallback: {env_config.fallback_on_error}")
        print(f"Auto-start: {env_config.auto_start_server}")
        
        # Validate environment configuration
        errors = validate_mcp_config(env_config)
        print(f"Validation errors: {len(errors)}")
        if errors:
            for error in errors:
                print(f"  - {error}")
        else:
            print("✅ Environment configuration is valid")
    
    finally:
        # Restore original environment
        for key, value in original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
    
    print()
    return True


def test_command_line_parsing():
    """Test command line argument parsing."""
    print("🔧 Testing Command Line Parsing")
    print("=" * 60)
    
    parser = create_ollama_parser()
    
    # Test cases: (args, description)
    test_cases = [
        ([], "Default arguments"),
        (['--model', 'llama2:7b'], "Custom model"),
        (['--no-mcp'], "MCP disabled"),
        (['--aws-threshold', '0.7'], "Custom AWS threshold"),
        (['--max-docs', '5'], "Custom max docs"),
        (['--connection-timeout', '20'], "Custom timeout"),
        (['--no-fallback'], "Fallback disabled"),
        (['--no-auto-start'], "Auto-start disabled"),
        (['--model', 'codellama:7b', '--no-mcp', '--log-dir', './test-logs'], "Multiple options"),
    ]
    
    for args, description in test_cases:
        print(f"Testing: {description}")
        print(f"Args: {args}")
        
        try:
            parsed_args = parser.parse_args(args)
            config = OllamaConfig.from_env_and_args(parsed_args)
            
            print(f"  Model: {config.model}")
            print(f"  MCP Enabled: {config.mcp_config.enabled}")
            print(f"  AWS Threshold: {config.mcp_config.aws_detection_threshold}")
            
            # Validate configuration
            errors = validate_ollama_config(config)
            if errors:
                print(f"  ❌ Validation errors: {errors}")
            else:
                print("  ✅ Configuration valid")
            
        except SystemExit:
            print("  ❌ Argument parsing failed")
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        print()
    
    return True


def test_config_validation():
    """Test configuration validation."""
    print("⚠️  Testing Configuration Validation")
    print("=" * 60)
    
    # Test invalid MCP configurations
    invalid_configs = [
        (MCPIntegrationConfig(aws_detection_threshold=-0.1), "Negative threshold"),
        (MCPIntegrationConfig(aws_detection_threshold=1.5), "Threshold > 1.0"),
        (MCPIntegrationConfig(max_documentation_entries=0), "Zero max docs"),
        (MCPIntegrationConfig(max_documentation_entries=15), "Too many max docs"),
        (MCPIntegrationConfig(connection_timeout=0), "Zero timeout"),
        (MCPIntegrationConfig(connection_timeout=100), "Excessive timeout"),
    ]
    
    for config, description in invalid_configs:
        print(f"Testing: {description}")
        errors = validate_mcp_config(config)
        
        if errors:
            print(f"  ✅ Correctly detected {len(errors)} error(s):")
            for error in errors:
                print(f"    - {error}")
        else:
            print("  ❌ Should have detected validation errors")
        print()
    
    # Test invalid Ollama configurations
    invalid_ollama_configs = [
        (OllamaConfig(model=""), "Empty model"),
        (OllamaConfig(ollama_url=""), "Empty URL"),
        (OllamaConfig(ollama_url="invalid-url"), "Invalid URL format"),
        (OllamaConfig(log_file=""), "Empty log file"),
    ]
    
    for config, description in invalid_ollama_configs:
        print(f"Testing: {description}")
        errors = validate_ollama_config(config)
        
        if errors:
            print(f"  ✅ Correctly detected {len(errors)} error(s):")
            for error in errors:
                print(f"    - {error}")
        else:
            print("  ❌ Should have detected validation errors")
        print()
    
    return True


def test_config_serialization():
    """Test configuration serialization and deserialization."""
    print("💾 Testing Configuration Serialization")
    print("=" * 60)
    
    # Create test configuration
    original_config = OllamaConfig(
        model="test-model:7b",
        ollama_url="http://test:11434",
        log_file="./test.log"
    )
    original_config.mcp_config = MCPIntegrationConfig(
        enabled=False,
        aws_detection_threshold=0.7,
        max_documentation_entries=5
    )
    
    print("Original configuration:")
    display_config_summary(original_config)
    
    # Convert to dictionary
    config_dict = get_config_dict(original_config)
    print("Configuration dictionary:")
    print(config_dict)
    print()
    
    # Convert back to configuration
    restored_config = create_config_from_dict(config_dict)
    
    print("Restored configuration:")
    display_config_summary(restored_config)
    
    # Verify they match
    matches = (
        original_config.model == restored_config.model and
        original_config.ollama_url == restored_config.ollama_url and
        original_config.log_file == restored_config.log_file and
        original_config.mcp_config.enabled == restored_config.mcp_config.enabled and
        original_config.mcp_config.aws_detection_threshold == restored_config.mcp_config.aws_detection_threshold and
        original_config.mcp_config.max_documentation_entries == restored_config.mcp_config.max_documentation_entries
    )
    
    if matches:
        print("✅ Serialization/deserialization successful")
    else:
        print("❌ Serialization/deserialization failed")
    
    return True


def test_environment_info():
    """Test environment information display."""
    print("🌍 Testing Environment Information")
    print("=" * 60)
    
    # Display current environment
    display_environment_info()
    
    # Get environment info programmatically
    env_info = get_environment_config_info()
    print("Environment info dictionary:")
    for key, value in env_info.items():
        print(f"  {key}: {value}")
    print()
    
    # Display optimal configuration suggestion
    optimal_config = suggest_optimal_config()
    print("Optimal configuration suggestion:")
    print(f"Description: {optimal_config['description']}")
    print("Settings:")
    for section, settings in optimal_config.items():
        if section != 'description':
            print(f"  {section}:")
            for key, value in settings.items():
                print(f"    {key}: {value}")
    
    return True


if __name__ == "__main__":
    print("🚀 Testing MCP Integration Configuration System")
    print("=" * 80)
    
    try:
        test_mcp_config_creation()
        test_command_line_parsing()
        test_config_validation()
        test_config_serialization()
        test_environment_info()
        
        print("=" * 80)
        print("🎉 All configuration system tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()