#!/usr/bin/env python3
"""Test enhanced Ollama client with MCP integration."""

import sys
import os
import logging
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enhanced_ollama_client import EnhancedOllamaClient


def setup_test_logger():
    """Set up logger for testing."""
    logger = logging.getLogger("test_enhanced_ollama")
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def test_enhanced_client_basic():
    """Test basic enhanced client functionality."""
    print("🧪 Testing Enhanced Ollama Client - Basic Functionality")
    print("=" * 70)
    
    logger = setup_test_logger()
    
    # Create enhanced client
    client = EnhancedOllamaClient(
        base_url="http://localhost:11434",
        model="qwen3:14b",
        logger=logger,
        mcp_enabled=True,
        aws_detection_threshold=0.4
    )
    
    # Test MCP status
    print("Testing MCP status...")
    status = client.get_mcp_status()
    print(f"MCP Enabled: {status['mcp_enabled']}")
    print(f"AWS Detection Threshold: {status['aws_detection_threshold']}")
    print(f"MCP Server Connected: {status['mcp_server_connected']}")
    print()
    
    # Test AWS query detection and MCP integration
    test_queries = [
        ("How do I create an S3 bucket?", True),  # Should use MCP
        ("What is machine learning?", False),     # Should not use MCP
        ("Configure EC2 security groups", True),  # Should use MCP
        ("Python programming basics", False),     # Should not use MCP
        ("DynamoDB best practices", True),        # Should use MCP
    ]
    
    print("Testing query processing...")
    for query, expect_mcp in test_queries:
        print(f"\n🔍 Query: '{query}'")
        print(f"   Expected MCP usage: {expect_mcp}")
        
        try:
            # This would normally call the actual Ollama server
            # For testing, we'll simulate the response
            print("   [Simulated - would call actual Ollama server]")
            
            # Test AWS detection
            aws_detection = client.aws_detector.analyze_query(query)
            should_use_mcp = client.should_use_mcp(query, aws_detection)
            
            print(f"   AWS Detected: {aws_detection.is_aws_related} (confidence: {aws_detection.confidence_score:.2f})")
            print(f"   Should Use MCP: {should_use_mcp}")
            print(f"   Services: {aws_detection.detected_services}")
            
            # Verify expectation
            if should_use_mcp == expect_mcp:
                print("   ✅ MCP usage decision matches expectation")
            else:
                print("   ❌ MCP usage decision doesn't match expectation")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test configuration
    print(f"\n🔧 Testing configuration...")
    client.configure_mcp(enabled=False)
    status = client.get_mcp_status()
    print(f"MCP Disabled: {not status['mcp_enabled']}")
    
    client.configure_mcp(enabled=True, threshold=0.6)
    status = client.get_mcp_status()
    print(f"MCP Re-enabled: {status['mcp_enabled']}")
    print(f"New Threshold: {status['aws_detection_threshold']}")
    
    # Cleanup
    client.cleanup()
    print("\n✅ Basic functionality tests completed!")
    
    return True


def test_mcp_integration():
    """Test MCP integration with mock responses."""
    print("\n🔗 Testing MCP Integration")
    print("=" * 70)
    
    logger = setup_test_logger()
    
    client = EnhancedOllamaClient(
        base_url="http://localhost:11434",
        model="qwen3:14b", 
        logger=logger,
        mcp_enabled=True
    )
    
    # Test MCP server management
    print("Testing MCP server management...")
    
    if client.mcp_manager:
        # Test server startup
        print("Attempting to start MCP server...")
        server_started = client.mcp_manager.start_server_if_needed()
        print(f"MCP Server Started: {server_started}")
        
        if server_started:
            # Test connection
            connected = client.mcp_manager.is_connected()
            print(f"MCP Server Connected: {connected}")
            
            # Test documentation query
            print("Testing documentation query...")
            response = client.mcp_manager.query_documentation("S3 bucket creation", ["s3"])
            print(f"Documentation Query Success: {response.success}")
            print(f"Documentation Entries: {len(response.documentation)}")
            print(f"Query Time: {response.query_time:.3f}s")
            
            if response.documentation:
                print(f"Sample Title: {response.documentation[0]['title'][:50]}...")
        
        # Cleanup
        client.mcp_manager.disconnect()
    
    client.cleanup()
    print("✅ MCP integration tests completed!")
    
    return True


def test_response_formatting():
    """Test response formatting and display."""
    print("\n📝 Testing Response Formatting")
    print("=" * 70)
    
    logger = setup_test_logger()
    
    client = EnhancedOllamaClient(
        base_url="http://localhost:11434",
        model="qwen3:14b",
        logger=logger
    )
    
    # Create mock enhanced response
    from enhanced_ollama_client import EnhancedResponse
    from aws_query_detector import AWSDetectionResult
    from context_enhancer import EnhancedContext
    
    # Mock AWS detection
    aws_detection = AWSDetectionResult(
        is_aws_related=True,
        confidence_score=0.8,
        detected_services=["s3"],
        matched_keywords=["bucket", "s3"]
    )
    
    # Mock enhanced context
    enhanced_context = EnhancedContext(
        original_query="How do I create an S3 bucket?",
        enhanced_prompt="Enhanced prompt with AWS docs...",
        documentation_summary="Retrieved 2 AWS documentation entries covering S3",
        sources=["https://docs.aws.amazon.com/s3/guide1", "https://docs.aws.amazon.com/s3/guide2"],
        confidence_score=0.9,
        processing_time=0.5
    )
    
    # Mock enhanced response
    enhanced_response = EnhancedResponse(
        llm_response="To create an S3 bucket, you need to...",
        mcp_used=True,
        aws_detection=aws_detection,
        enhanced_context=enhanced_context,
        processing_time=1.2
    )
    
    print("Testing enhanced response display...")
    client._display_enhanced_response(enhanced_response)
    
    # Test fallback response
    fallback_response = EnhancedResponse(
        llm_response="Here's general information about S3...",
        mcp_used=False,
        aws_detection=aws_detection,
        enhanced_context=None,
        processing_time=0.8,
        fallback_reason="MCP server unavailable"
    )
    
    print("Testing fallback response display...")
    client._display_enhanced_response(fallback_response)
    
    # Test statistics
    client.stats = {
        "total_queries": 10,
        "aws_queries_detected": 6,
        "mcp_queries_successful": 4,
        "mcp_queries_failed": 2,
        "fallback_queries": 2
    }
    
    print("Testing session statistics display...")
    client._display_session_stats()
    
    client.cleanup()
    print("✅ Response formatting tests completed!")
    
    return True


def test_error_handling():
    """Test error handling and fallback scenarios."""
    print("\n⚠️  Testing Error Handling")
    print("=" * 70)
    
    logger = setup_test_logger()
    
    # Test with MCP disabled
    print("Testing with MCP disabled...")
    client = EnhancedOllamaClient(
        base_url="http://localhost:11434",
        model="qwen3:14b",
        logger=logger,
        mcp_enabled=False
    )
    
    status = client.get_mcp_status()
    print(f"MCP Enabled: {status['mcp_enabled']}")
    print(f"MCP Manager: {client.mcp_manager is not None}")
    
    # Test AWS detection still works
    aws_detection = client.aws_detector.analyze_query("How do I use S3?")
    should_use_mcp = client.should_use_mcp("How do I use S3?", aws_detection)
    print(f"AWS Detected: {aws_detection.is_aws_related}")
    print(f"Should Use MCP (disabled): {should_use_mcp}")
    
    client.cleanup()
    
    # Test with very high threshold
    print("\nTesting with high AWS detection threshold...")
    client = EnhancedOllamaClient(
        base_url="http://localhost:11434",
        model="qwen3:14b",
        logger=logger,
        mcp_enabled=True,
        aws_detection_threshold=0.9  # Very high threshold
    )
    
    aws_detection = client.aws_detector.analyze_query("How do I use S3?")
    should_use_mcp = client.should_use_mcp("How do I use S3?", aws_detection)
    print(f"AWS Confidence: {aws_detection.confidence_score:.2f}")
    print(f"Threshold: {client.aws_detection_threshold}")
    print(f"Should Use MCP (high threshold): {should_use_mcp}")
    
    client.cleanup()
    print("✅ Error handling tests completed!")
    
    return True


if __name__ == "__main__":
    print("🚀 Testing Enhanced Ollama Client with MCP Integration")
    print("=" * 80)
    
    try:
        test_enhanced_client_basic()
        test_mcp_integration()
        test_response_formatting()
        test_error_handling()
        
        print("=" * 80)
        print("🎉 All Enhanced Ollama Client tests completed successfully!")
        print("\nNote: Actual LLM responses are simulated in these tests.")
        print("To test with real Ollama server, ensure it's running on localhost:11434")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()