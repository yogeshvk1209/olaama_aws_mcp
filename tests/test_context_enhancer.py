#!/usr/bin/env python3
"""Test context enhancement system."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from context_enhancer import ContextEnhancer
from mcp_client_manager import MCPClientManager


def test_context_enhancement():
    """Test context enhancement with various queries."""
    print("🧪 Testing Context Enhancement System")
    print("=" * 60)
    
    # Create MCP client manager and context enhancer
    mcp_manager = MCPClientManager()
    enhancer = ContextEnhancer(mcp_manager)
    
    # Start MCP server for testing
    print("Starting MCP server for testing...")
    server_started = mcp_manager.start_server_if_needed()
    print(f"MCP Server Started: {server_started}")
    print()
    
    # Test cases: (query, services)
    test_cases = [
        ("How do I create an S3 bucket?", ["s3"]),
        ("Configure EC2 instance with security groups", ["ec2"]),
        ("Set up Lambda function with API Gateway", ["lambda", "api gateway"]),
        ("DynamoDB table design best practices", ["dynamodb"]),
        ("What is AWS?", []),  # General query
    ]
    
    for query, services in test_cases:
        print(f"🔍 Testing Query: '{query}'")
        print(f"   Services: {services if services else 'None detected'}")
        
        # Get enhancement preview
        preview = enhancer.preview_enhancement(query, services)
        print(f"   Preview:\n{preview}")
        
        # Perform actual enhancement
        enhanced_context = enhancer.enhance_query(query, services)
        
        print(f"   Enhancement Results:")
        print(f"   - Confidence Score: {enhanced_context.confidence_score:.2f}")
        print(f"   - Processing Time: {enhanced_context.processing_time:.3f}s")
        print(f"   - Documentation Summary: {enhanced_context.documentation_summary}")
        print(f"   - Sources: {len(enhanced_context.sources)}")
        
        # Show enhanced prompt (truncated)
        enhanced_preview = enhanced_context.enhanced_prompt[:200] + "..." if len(enhanced_context.enhanced_prompt) > 200 else enhanced_context.enhanced_prompt
        print(f"   - Enhanced Prompt Preview: {enhanced_preview}")
        
        # Get enhancement statistics
        stats = enhancer.get_enhancement_stats(enhanced_context)
        print(f"   - Enhancement Stats:")
        print(f"     * Original Length: {stats['original_query_length']} chars")
        print(f"     * Enhanced Length: {stats['enhanced_prompt_length']} chars")
        print(f"     * Enhancement Ratio: {stats['enhancement_ratio']:.1f}x")
        print(f"     * Documentation Sources: {stats['documentation_sources']}")
        
        print("-" * 60)
    
    # Cleanup
    mcp_manager.disconnect()
    
    return True


def test_documentation_formatting():
    """Test documentation formatting functionality."""
    print("📝 Testing Documentation Formatting")
    print("=" * 60)
    
    # Create enhancer with mock MCP manager
    mcp_manager = MCPClientManager()
    enhancer = ContextEnhancer(mcp_manager)
    
    # Test documentation formatting with mock data
    mock_docs = [
        {
            "title": "Amazon S3 Bucket Creation Guide",
            "content": "Amazon Simple Storage Service (S3) is a scalable object storage service. To create a bucket, you need to specify a unique bucket name and select a region. Bucket names must be globally unique across all AWS accounts. The bucket name must be between 3 and 63 characters long and can contain only lowercase letters, numbers, and hyphens.",
            "service": "s3",
            "url": "https://docs.aws.amazon.com/s3/latest/userguide/create-bucket.html",
            "relevance_score": 0.9
        },
        {
            "title": "S3 Security Best Practices",
            "content": "Security is a critical aspect of S3 bucket management. Always enable bucket versioning, configure appropriate access policies, and use encryption for sensitive data. Consider using S3 Block Public Access settings to prevent accidental public exposure of your data.",
            "service": "s3",
            "url": "https://docs.aws.amazon.com/s3/latest/userguide/security-best-practices.html",
            "relevance_score": 0.8
        }
    ]
    
    # Test formatting
    from mcp_client_manager import MCPResponse
    mock_response = MCPResponse(
        success=True,
        documentation=mock_docs,
        sources=[doc["url"] for doc in mock_docs],
        query_time=0.5
    )
    
    formatted_docs = enhancer.format_documentation(mock_response)
    print("Formatted Documentation:")
    print(formatted_docs)
    print()
    
    # Test enhanced prompt creation
    original_query = "How do I create a secure S3 bucket?"
    enhanced_prompt = enhancer.create_enhanced_prompt(original_query, formatted_docs)
    
    print("Enhanced Prompt:")
    print(enhanced_prompt[:500] + "..." if len(enhanced_prompt) > 500 else enhanced_prompt)
    print()
    
    # Test documentation summary
    doc_summary = enhancer.create_documentation_summary(mock_docs)
    print(f"Documentation Summary: {doc_summary}")
    print()
    
    # Test confidence calculation
    confidence = enhancer.calculate_confidence_score(mock_response)
    print(f"Confidence Score: {confidence:.2f}")
    
    return True


def test_edge_cases():
    """Test edge cases and error handling."""
    print("⚠️  Testing Edge Cases")
    print("=" * 60)
    
    mcp_manager = MCPClientManager()
    enhancer = ContextEnhancer(mcp_manager)
    
    # Test with empty query
    print("Testing empty query...")
    enhanced_context = enhancer.enhance_query("", [])
    print(f"Empty Query Result: {enhanced_context.confidence_score:.2f} confidence")
    print()
    
    # Test with very long query
    long_query = "How do I configure " + "AWS services " * 50 + "for my application?"
    print("Testing very long query...")
    enhanced_context = enhancer.enhance_query(long_query, ["ec2", "s3"])
    print(f"Long Query Result: {enhanced_context.confidence_score:.2f} confidence")
    print(f"Enhanced Length: {len(enhanced_context.enhanced_prompt)} chars")
    print()
    
    # Test with no MCP server connection
    print("Testing without MCP server connection...")
    enhanced_context = enhancer.enhance_query("What is S3?", ["s3"])
    print(f"No Connection Result: {enhanced_context.confidence_score:.2f} confidence")
    print(f"Documentation Summary: {enhanced_context.documentation_summary}")
    print()
    
    return True


if __name__ == "__main__":
    print("🚀 Testing Context Enhancement System")
    print("=" * 80)
    
    try:
        test_context_enhancement()
        print()
        test_documentation_formatting()
        print()
        test_edge_cases()
        
        print("=" * 80)
        print("✅ Context Enhancement System tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()