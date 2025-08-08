#!/usr/bin/env python3
"""Test the integrated Ollama CLI with MCP functionality."""

import os
import sys
import subprocess
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_cli_help():
    """Test CLI help output."""
    print("🧪 Testing CLI Help Output")
    print("=" * 50)
    
    try:
        result = subprocess.run(
            [sys.executable, 'ollama_cli.py', '--help'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ Help command works")
            print("Help output preview:")
            print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
        else:
            print(f"❌ Help command failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Help command timed out")
        return False
    except Exception as e:
        print(f"❌ Help command error: {e}")
        return False
    
    return True


def test_cli_version():
    """Test CLI version output."""
    print("\n🔖 Testing CLI Version")
    print("=" * 50)
    
    try:
        result = subprocess.run(
            [sys.executable, 'ollama_cli.py', '--version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ Version command works")
            print(f"Version: {result.stdout.strip()}")
        else:
            print(f"❌ Version command failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Version command timed out")
        return False
    except Exception as e:
        print(f"❌ Version command error: {e}")
        return False
    
    return True


def test_configuration_validation():
    """Test configuration validation with various settings."""
    print("\n⚙️  Testing Configuration Validation")
    print("=" * 50)
    
    # Test with valid configuration
    print("Testing valid configuration...")
    try:
        from config import OllamaConfig, create_ollama_parser
        from config_utils import validate_ollama_config
        
        parser = create_ollama_parser()
        args = parser.parse_args(['--model', 'test-model:7b'])
        config = OllamaConfig.from_env_and_args(args)
        
        errors = validate_ollama_config(config)
        if not errors:
            print("✅ Valid configuration passes validation")
        else:
            print(f"❌ Valid configuration failed: {errors}")
            return False
            
    except Exception as e:
        print(f"❌ Configuration validation error: {e}")
        return False
    
    # Test with invalid configuration
    print("Testing invalid configuration...")
    try:
        from config import OllamaConfig
        
        invalid_config = OllamaConfig(
            model="",  # Invalid empty model
            ollama_url="invalid-url",  # Invalid URL
            log_file=""  # Invalid empty log file
        )
        
        errors = validate_ollama_config(invalid_config)
        if errors:
            print(f"✅ Invalid configuration correctly detected {len(errors)} errors")
        else:
            print("❌ Invalid configuration should have been detected")
            return False
            
    except Exception as e:
        print(f"❌ Invalid configuration test error: {e}")
        return False
    
    return True


def test_mcp_integration_components():
    """Test that all MCP integration components can be imported and initialized."""
    print("\n🔗 Testing MCP Integration Components")
    print("=" * 50)
    
    components = [
        ("AWS Query Detector", "aws_query_detector", "AWSQueryDetector"),
        ("MCP Client Manager", "mcp_client_manager", "MCPClientManager"),
        ("Context Enhancer", "context_enhancer", "ContextEnhancer"),
        ("Enhanced Ollama Client", "enhanced_ollama_client", "EnhancedOllamaClient"),
        ("Enhanced CLI Interface", "enhanced_cli_interface", "EnhancedCLI"),
        ("Configuration Utils", "config_utils", "validate_ollama_config"),
    ]
    
    for name, module_name, class_or_function in components:
        try:
            module = __import__(module_name)
            component = getattr(module, class_or_function)
            print(f"✅ {name}: Available")
        except ImportError as e:
            print(f"❌ {name}: Import failed - {e}")
            return False
        except AttributeError as e:
            print(f"❌ {name}: Component not found - {e}")
            return False
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
            return False
    
    return True


def test_environment_variable_support():
    """Test environment variable configuration support."""
    print("\n🌍 Testing Environment Variable Support")
    print("=" * 50)
    
    # Test with custom environment variables
    test_env = os.environ.copy()
    test_env.update({
        'OLLAMA_MODEL': 'test-env-model:7b',
        'MCP_INTEGRATION_ENABLED': 'false',
        'AWS_DETECTION_THRESHOLD': '0.7',
        'LOG_DIR': './test-logs'
    })
    
    try:
        # Create a temporary test script
        test_script = '''
import sys
sys.path.insert(0, '.')
from config import OllamaConfig, create_ollama_parser

parser = create_ollama_parser()
args = parser.parse_args([])
config = OllamaConfig.from_env_and_args(args)

print(f"Model: {config.model}")
print(f"MCP Enabled: {config.mcp_config.enabled}")
print(f"AWS Threshold: {config.mcp_config.aws_detection_threshold}")
print(f"Log File: {config.log_file}")
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_script)
            temp_script = f.name
        
        try:
            result = subprocess.run(
                [sys.executable, temp_script],
                capture_output=True,
                text=True,
                env=test_env,
                timeout=10
            )
            
            if result.returncode == 0:
                output = result.stdout.strip()
                if 'test-env-model:7b' in output and 'False' in output and '0.7' in output:
                    print("✅ Environment variables correctly applied")
                    print("Environment test output:")
                    print(output)
                else:
                    print(f"❌ Environment variables not applied correctly: {output}")
                    return False
            else:
                print(f"❌ Environment test failed: {result.stderr}")
                return False
                
        finally:
            os.unlink(temp_script)
            
    except Exception as e:
        print(f"❌ Environment variable test error: {e}")
        return False
    
    return True


def test_command_line_argument_parsing():
    """Test command line argument parsing."""
    print("\n🔧 Testing Command Line Argument Parsing")
    print("=" * 50)
    
    test_cases = [
        (['--model', 'custom-model:7b'], "Custom model"),
        (['--no-mcp'], "MCP disabled"),
        (['--aws-threshold', '0.8'], "Custom AWS threshold"),
        (['--max-docs', '5'], "Custom max docs"),
        (['--log-dir', './custom-logs'], "Custom log directory"),
    ]
    
    for args, description in test_cases:
        print(f"Testing: {description}")
        try:
            from config import create_ollama_parser, OllamaConfig
            
            parser = create_ollama_parser()
            parsed_args = parser.parse_args(args)
            config = OllamaConfig.from_env_and_args(parsed_args)
            
            print(f"  ✅ Arguments parsed successfully")
            
            # Verify specific argument effects
            if '--model' in args:
                expected_model = args[args.index('--model') + 1]
                if config.model == expected_model:
                    print(f"  ✅ Model correctly set to {config.model}")
                else:
                    print(f"  ❌ Model not set correctly: {config.model}")
                    return False
            
            if '--no-mcp' in args:
                if not config.mcp_config.enabled:
                    print(f"  ✅ MCP correctly disabled")
                else:
                    print(f"  ❌ MCP should be disabled")
                    return False
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False
    
    return True


def test_integration_imports():
    """Test that the main script can import all required components."""
    print("\n📦 Testing Integration Imports")
    print("=" * 50)
    
    try:
        # Test the main script imports
        test_script = '''
import sys
sys.path.insert(0, '.')

# Test all imports from ollama_cli.py
from config import OllamaConfig, create_ollama_parser
from config_utils import validate_ollama_config, display_config_summary
from logging_utils import setup_ollama_logging
from enhanced_ollama_client import EnhancedOllamaClient
from enhanced_cli_interface import EnhancedCLI

print("All imports successful")
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_script)
            temp_script = f.name
        
        try:
            result = subprocess.run(
                [sys.executable, temp_script],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and "All imports successful" in result.stdout:
                print("✅ All integration imports successful")
            else:
                print(f"❌ Import test failed: {result.stderr}")
                return False
                
        finally:
            os.unlink(temp_script)
            
    except Exception as e:
        print(f"❌ Integration import test error: {e}")
        return False
    
    return True


if __name__ == "__main__":
    print("🚀 Testing Integrated Ollama CLI with MCP Functionality")
    print("=" * 80)
    
    tests = [
        test_cli_help,
        test_cli_version,
        test_configuration_validation,
        test_mcp_integration_components,
        test_environment_variable_support,
        test_command_line_argument_parsing,
        test_integration_imports,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print("❌ Test failed")
        except Exception as e:
            print(f"❌ Test error: {e}")
        print()
    
    print("=" * 80)
    print(f"📊 Integration Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests passed!")
        print("\n🚀 The Enhanced Ollama CLI with MCP Integration is ready!")
        print("\nTo use the CLI:")
        print("  python3 ollama_cli.py                    # Start with defaults")
        print("  python3 ollama_cli.py --help             # Show all options")
        print("  python3 ollama_cli.py --no-mcp           # Disable MCP integration")
        print("  python3 ollama_cli.py --aws-threshold 0.6 # Adjust AWS detection")
    else:
        print("⚠️  Some integration tests failed. Please check the implementation.")
    
    sys.exit(0 if passed == total else 1)