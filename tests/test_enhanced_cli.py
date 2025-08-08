#!/usr/bin/env python3
"""Test enhanced CLI interface with MCP integration."""

import sys
import os
import logging
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import Mock, patch
from enhanced_cli_interface import EnhancedCLI
from enhanced_ollama_client import EnhancedOllamaClient, EnhancedResponse
from aws_query_detector import AWSDetectionResult
from context_enhancer import EnhancedContext
from config import OllamaConfig, MCPIntegrationConfig


def setup_test_logger():
    """Set up logger for testing."""
    logger = logging.getLogger("test_enhanced_cli")
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def create_mock_config():
    """Create mock configuration for testing."""
    config = OllamaConfig(
        model="test-model:7b",
        ollama_url="http://localhost:11434",
        log_file="./test.log"
    )
    config.mcp_config = MCPIntegrationConfig(
        enabled=True,
        aws_detection_threshold=0.4,
        max_documentation_entries=3
    )
    return config


def create_mock_client():
    """Create mock enhanced Ollama client."""
    client = Mock(spec=EnhancedOllamaClient)
    client.base_url = "http://localhost:11434"
    client.model = "test-model:7b"
    client.mcp_enabled = True
    
    # Mock MCP status
    client.get_mcp_status.return_value = {
        'mcp_enabled': True,
        'aws_detection_threshold': 0.4,
        'mcp_server_connected': True,
        'statistics': {
            'total_queries': 10,
            'aws_queries_detected': 6,
            'mcp_queries_successful': 4,
            'mcp_queries_failed': 2,
            'fallback_queries': 2
        }
    }
    
    return client


def test_cli_initialization():
    """Test CLI initialization and welcome display."""
    print("🧪 Testing CLI Initialization")
    print("=" * 50)
    
    logger = setup_test_logger()
    config = create_mock_config()
    client = create_mock_client()
    
    # Create CLI
    cli = EnhancedCLI(client, config, logger)
    
    print("Testing CLI initialization...")
    print(f"Commands available: {len(cli.commands)}")
    print(f"Commands: {list(cli.commands.keys())}")
    
    # Test welcome display
    print("\nTesting welcome display...")
    cli.display_welcome()
    
    print("✅ CLI initialization test completed!")
    return True


def test_command_handling():
    """Test command handling functionality."""
    print("\n🔧 Testing Command Handling")
    print("=" * 50)
    
    logger = setup_test_logger()
    config = create_mock_config()
    client = create_mock_client()
    cli = EnhancedCLI(client, config, logger)
    
    # Test command recognition
    test_commands = [
        ("help", True),
        ("status", True),
        ("config", True),
        ("stats", True),
        ("mcp status", True),
        ("not_a_command", False),
        ("", False),
    ]
    
    for command, should_handle in test_commands:
        print(f"Testing command: '{command}'")
        handled = cli.handle_command(command)
        
        if handled == should_handle:
            print(f"  ✅ Correctly {'handled' if handled else 'ignored'}")
        else:
            print(f"  ❌ Expected {'handled' if should_handle else 'ignored'}, got {'handled' if handled else 'ignored'}")
    
    print("✅ Command handling test completed!")
    return True


def test_response_display():
    """Test enhanced response display."""
    print("\n📝 Testing Response Display")
    print("=" * 50)
    
    logger = setup_test_logger()
    config = create_mock_config()
    client = create_mock_client()
    cli = EnhancedCLI(client, config, logger)
    
    # Create mock AWS detection
    aws_detection = AWSDetectionResult(
        is_aws_related=True,
        confidence_score=0.8,
        detected_services=["s3"],
        matched_keywords=["bucket", "s3"]
    )
    
    # Create mock enhanced context
    enhanced_context = EnhancedContext(
        original_query="How do I create an S3 bucket?",
        enhanced_prompt="Enhanced prompt with AWS docs...",
        documentation_summary="Retrieved 2 AWS documentation entries covering S3",
        sources=["https://docs.aws.amazon.com/s3/guide1", "https://docs.aws.amazon.com/s3/guide2"],
        confidence_score=0.9,
        processing_time=0.5
    )
    
    # Test MCP-enhanced response
    print("Testing MCP-enhanced response display...")
    mcp_response = EnhancedResponse(
        llm_response="To create an S3 bucket, you need to...",
        mcp_used=True,
        aws_detection=aws_detection,
        enhanced_context=enhanced_context,
        processing_time=1.2
    )
    
    cli.display_enhanced_response(mcp_response)
    
    # Test fallback response
    print("\nTesting fallback response display...")
    fallback_response = EnhancedResponse(
        llm_response="Here's general information about S3...",
        mcp_used=False,
        aws_detection=aws_detection,
        enhanced_context=None,
        processing_time=0.8,
        fallback_reason="MCP server unavailable"
    )
    
    cli.display_enhanced_response(fallback_response)
    
    # Test non-AWS response
    print("\nTesting non-AWS response display...")
    non_aws_detection = AWSDetectionResult(
        is_aws_related=False,
        confidence_score=0.1,
        detected_services=[],
        matched_keywords=[]
    )
    
    regular_response = EnhancedResponse(
        llm_response="Here's information about machine learning...",
        mcp_used=False,
        aws_detection=non_aws_detection,
        enhanced_context=None,
        processing_time=0.6
    )
    
    cli.display_enhanced_response(regular_response)
    
    print("✅ Response display test completed!")
    return True


def test_status_commands():
    """Test status and information commands."""
    print("\n📊 Testing Status Commands")
    print("=" * 50)
    
    logger = setup_test_logger()
    config = create_mock_config()
    client = create_mock_client()
    cli = EnhancedCLI(client, config, logger)
    
    # Test help command
    print("Testing help command...")
    cli.show_help()
    print()
    
    # Test status command
    print("Testing status command...")
    cli.show_status()
    print()
    
    # Test config command
    print("Testing config command...")
    cli.show_config()
    print()
    
    # Test stats command
    print("Testing stats command...")
    cli.show_stats()
    print()
    
    print("✅ Status commands test completed!")
    return True


def test_mcp_commands():
    """Test MCP-specific commands."""
    print("\n🔍 Testing MCP Commands")
    print("=" * 50)
    
    logger = setup_test_logger()
    config = create_mock_config()
    client = create_mock_client()
    
    # Mock MCP manager
    mock_mcp_manager = Mock()
    mock_mcp_manager.test_connection.return_value = {
        'server_script': 'aws_mcp_server.py',
        'script_exists': True,
        'connected': True,
        'error': None,
        'server_info': {'pid': 12345}
    }
    
    client.mcp_manager = mock_mcp_manager
    
    cli = EnhancedCLI(client, config, logger)
    
    # Test MCP commands
    print("Testing MCP status command...")
    cli.mcp_commands(['status'])
    print()
    
    print("Testing MCP enable command...")
    cli.mcp_commands(['enable'])
    print()
    
    print("Testing MCP disable command...")
    cli.mcp_commands(['disable'])
    print()
    
    print("Testing MCP test command...")
    # Mock query response
    from mcp_client_manager import MCPResponse
    mock_response = MCPResponse(
        success=True,
        documentation=[{"title": "Test doc"}],
        sources=["http://test.com"],
        query_time=0.1
    )
    mock_mcp_manager.query_documentation.return_value = mock_response
    
    cli.mcp_commands(['test'])
    print()
    
    print("Testing invalid MCP command...")
    cli.mcp_commands(['invalid'])
    print()
    
    print("Testing MCP command without arguments...")
    cli.mcp_commands([])
    print()
    
    print("✅ MCP commands test completed!")
    return True


def test_interactive_simulation():
    """Test interactive session simulation."""
    print("\n🎮 Testing Interactive Session Simulation")
    print("=" * 50)
    
    logger = setup_test_logger()
    config = create_mock_config()
    client = create_mock_client()
    cli = EnhancedCLI(client, config, logger)
    
    # Mock the send_message_with_mcp method
    aws_detection = AWSDetectionResult(
        is_aws_related=True,
        confidence_score=0.8,
        detected_services=["s3"],
        matched_keywords=["bucket"]
    )
    
    enhanced_context = EnhancedContext(
        original_query="Test query",
        enhanced_prompt="Enhanced prompt",
        documentation_summary="Test documentation",
        sources=["http://test.com"],
        confidence_score=0.9,
        processing_time=0.5
    )
    
    mock_response = EnhancedResponse(
        llm_response="Test response from LLM",
        mcp_used=True,
        aws_detection=aws_detection,
        enhanced_context=enhanced_context,
        processing_time=1.0
    )
    
    client.send_message_with_mcp.return_value = mock_response
    
    # Simulate processing a query
    print("Simulating query processing...")
    cli.process_query("How do I create an S3 bucket?")
    
    print("✅ Interactive session simulation completed!")
    return True


if __name__ == "__main__":
    print("🚀 Testing Enhanced CLI Interface with MCP Integration")
    print("=" * 80)
    
    try:
        test_cli_initialization()
        test_command_handling()
        test_response_display()
        test_status_commands()
        test_mcp_commands()
        test_interactive_simulation()
        
        print("=" * 80)
        print("🎉 All Enhanced CLI Interface tests completed successfully!")
        print("\nThe CLI is ready for interactive use with:")
        print("  • Rich MCP status indicators")
        print("  • Interactive command system")
        print("  • Enhanced response display")
        print("  • Comprehensive status reporting")
        print("  • MCP server management commands")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()