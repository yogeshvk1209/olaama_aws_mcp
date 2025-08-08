# Test Suite - Enhanced Ollama CLI with MCP Integration

This directory contains comprehensive tests for the Enhanced Ollama CLI with AWS MCP Integration.

## Test Files

### Component Tests
- `test_aws_detection.py` - AWS query detection accuracy tests
- `test_mcp_client.py` - MCP client manager functionality tests
- `test_context_enhancer.py` - Context enhancement pipeline tests
- `test_enhanced_ollama.py` - Enhanced Ollama client integration tests
- `test_config_system.py` - Configuration system tests
- `test_enhanced_cli.py` - Enhanced CLI interface tests

### Integration Tests
- `test_integrated_cli.py` - Integrated CLI functionality tests
- `test_startup.py` - CLI startup process tests
- `integration_test_suite.py` - Comprehensive integration test suite

### Utility Tests
- `test_scripts.py` - Basic script functionality tests
- `test_log_dir.py` - Log directory functionality tests

### Demo and Examples
- `demo_mcp_integration.py` - Feature demonstration script

## Running Tests

### Run All Tests
```bash
cd tests
python3 run_all_tests.py
```

### Run Individual Tests
```bash
cd tests
python3 test_aws_detection.py
python3 test_mcp_client.py
# ... etc
```

### Run Integration Test Suite
```bash
cd tests
python3 integration_test_suite.py
```

## Test Results

All tests should pass for a fully functional system:
- ✅ AWS Query Detection: 25/25 test cases
- ✅ MCP Server Lifecycle: 5/5 test scenarios
- ✅ Context Enhancement: 5/5 pipeline tests
- ✅ Enhanced Ollama Client: 5/5 integration tests
- ✅ CLI Interface: 7/7 functionality tests
- ✅ Configuration System: 4/4 validation tests
- ✅ End-to-End Integration: 5/5 flow tests
- ✅ Fallback Mechanisms: 2/2 scenario tests

## Requirements

Tests require the same dependencies as the main application:
- Python 3.7+
- requests library
- All main application modules

## Notes

- Tests are designed to work without requiring an actual Ollama server
- MCP server tests use mock data when the server is not available
- Integration tests validate the complete system workflow
- All tests include proper cleanup and resource management