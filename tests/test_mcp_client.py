#!/usr/bin/env python3
"""Test MCP client manager functionality."""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_client_manager import MCPClientManager


def test_mcp_client_basic():
    """Test basic MCP client functionality."""
    print("🧪 Testing MCP Client Manager")
    print("=" * 50)
    
    # Create client manager
    client = MCPClientManager()
    
    # Test connection (will likely fail since server isn't running)
    print("Testing connection...")
    connection_result = client.test_connection()
    
    print(f"Server Script: {connection_result['server_script']}")
    print(f"Script Exists: {connection_result['script_exists']}")
    print(f"Connected: {connection_result['connected']}")
    
    if connection_result['error']:
        print(f"Error: {connection_result['error']}")
    
    if connection_result['server_info']:
        print(f"Server Info: {connection_result['server_info']}")
    
    print()
    
    # Test query (will fail if not connected)
    print("Testing documentation query...")
    query_result = client.query_documentation("How to create S3 bucket?", ["s3"])
    
    print(f"Query Success: {query_result.success}")
    print(f"Query Time: {query_result.query_time:.3f}s")
    print(f"Documentation Entries: {len(query_result.documentation)}")
    print(f"Sources: {len(query_result.sources)}")
    
    if query_result.error_message:
        print(f"Error: {query_result.error_message}")
    
    print()
    
    # Test server auto-start (will try to start our aws_mcp_server.py)
    print("Testing server auto-start...")
    start_result = client.start_server_if_needed()
    print(f"Server Start Result: {start_result}")
    
    if start_result:
        print("Waiting for server to be ready...")
        time.sleep(2)
        
        # Test connection again
        connection_result = client.test_connection()
        print(f"Post-start Connected: {connection_result['connected']}")
        
        if connection_result['connected']:
            # Test a real query
            print("Testing query with running server...")
            query_result = client.query_documentation("S3 bucket configuration", ["s3"])
            print(f"Query Success: {query_result.success}")
            print(f"Documentation Entries: {len(query_result.documentation)}")
            if query_result.documentation:
                print(f"Sample Title: {query_result.documentation[0]['title'][:50]}...")
                print(f"Sources: {query_result.sources}")
    
    # Cleanup
    client.disconnect()
    
    return True


def test_mcp_client_mock():
    """Test MCP client with mock responses (for when server isn't available)."""
    print("🔧 Testing MCP Client Mock Scenarios")
    print("=" * 50)
    
    client = MCPClientManager()
    
    # Test various error scenarios
    test_cases = [
        ("Empty query", ""),
        ("AWS S3 query", "How do I configure S3 bucket permissions?"),
        ("Multi-service query", "Connect S3 to Lambda with CloudWatch monitoring"),
        ("Generic AWS query", "AWS best practices"),
    ]
    
    for test_name, query in test_cases:
        print(f"Testing: {test_name}")
        result = client.query_documentation(query)
        
        print(f"  Success: {result.success}")
        print(f"  Query Time: {result.query_time:.3f}s")
        print(f"  Error: {result.error_message or 'None'}")
        print()
    
    return True


def test_connection_resilience():
    """Test connection resilience and health checking."""
    print("🔄 Testing Connection Resilience")
    print("=" * 50)
    
    client = MCPClientManager()
    
    # Test multiple connection attempts
    for i in range(3):
        print(f"Connection attempt {i+1}:")
        connected = client.connect()
        print(f"  Result: {connected}")
        print(f"  Is Connected: {client.is_connected()}")
        time.sleep(1)
    
    print()
    
    # Test health check behavior
    print("Testing health check intervals...")
    
    # First check
    is_connected_1 = client.is_connected()
    print(f"First health check: {is_connected_1}")
    
    # Immediate second check (should use cached result)
    is_connected_2 = client.is_connected()
    print(f"Immediate second check: {is_connected_2}")
    
    # Simulate time passing (would trigger new health check in real scenario)
    client.last_health_check = 0  # Force health check
    is_connected_3 = client.is_connected()
    print(f"Forced health check: {is_connected_3}")
    
    return True


if __name__ == "__main__":
    print("🚀 Testing MCP Client Manager")
    print("=" * 60)
    
    try:
        test_mcp_client_basic()
        print()
        test_mcp_client_mock()
        print()
        test_connection_resilience()
        
        print("=" * 60)
        print("✅ MCP Client Manager tests completed!")
        print("Note: Some tests may show connection failures if MCP server isn't running - this is expected.")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()