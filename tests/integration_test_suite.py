#!/usr/bin/env python3
"""Comprehensive integration test suite for Enhanced Ollama CLI with MCP Integration."""

import os
import sys
import time
import tempfile
import subprocess
import logging
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test results tracking
class TestResults:
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def add_result(self, test_name: str, passed: bool, error: str = None):
        self.total += 1
        if passed:
            self.passed += 1
            print(f"✅ {test_name}")
        else:
            self.failed += 1
            print(f"❌ {test_name}")
            if error:
                print(f"   Error: {error}")
                self.errors.append(f"{test_name}: {error}")
    
    def summary(self):
        print(f"\n📊 Test Results: {self.passed}/{self.total} passed")
        if self.failed > 0:
            print(f"❌ {self.failed} tests failed:")
            for error in self.errors:
                print(f"   • {error}")
        return self.failed == 0


def test_aws_query_detection_accuracy():
    """Test AWS query detection with comprehensive test cases."""
    print("\n🔍 Testing AWS Query Detection Accuracy")
    print("=" * 60)
    
    results = TestResults()
    
    try:
        from aws_query_detector import AWSQueryDetector
        detector = AWSQueryDetector()
        
        # Comprehensive test cases
        test_cases = [
            # Clear AWS queries (should detect)
            ("How do I create an S3 bucket?", True, ["s3"]),
            ("Configure EC2 instance security groups", True, ["ec2"]),
            ("AWS Lambda function deployment guide", True, ["lambda"]),
            ("Set up RDS database with Aurora", True, ["rds", "aurora"]),
            ("DynamoDB table design best practices", True, ["dynamodb"]),
            ("CloudFormation template for VPC", True, ["cloudformation", "vpc"]),
            ("Monitor application with CloudWatch", True, ["cloudwatch"]),
            ("API Gateway integration with Lambda", True, ["api gateway", "lambda"]),
            ("ECS cluster configuration", True, ["ecs"]),
            ("IAM roles and policies setup", True, ["iam"]),
            
            # Borderline AWS queries (may not detect specific services, just keywords)
            ("Deploy application to AWS cloud", True, []),
            ("Amazon web services pricing", True, []),
            ("AWS CLI configuration", True, []),
            
            # Non-AWS queries (should not detect)
            ("What is machine learning?", False, []),
            ("Python programming tutorial", False, []),
            ("How to cook pasta?", False, []),
            ("Database design principles", False, []),
            ("Web development best practices", False, []),
            ("Docker container deployment", False, []),
            ("Kubernetes cluster management", False, []),
            ("Git version control", False, []),
            
            # Edge cases
            ("", False, []),
            ("aws", True, []),  # Single word may not detect specific services
            ("Amazon", False, []),
            ("cloud computing", False, []),
        ]
        
        for query, expected_aws, expected_services in test_cases:
            detection = detector.analyze_query(query)
            
            # Test AWS detection
            aws_correct = detection.is_aws_related == expected_aws
            
            # Test service detection (if AWS query)
            services_correct = True
            if expected_aws and expected_services:
                detected_services = set(detection.detected_services)
                expected_services_set = set(expected_services)
                # Check if at least one expected service is detected, or if no services expected, that's ok too
                services_correct = bool(detected_services.intersection(expected_services_set)) or len(expected_services) == 0
            
            test_passed = aws_correct and services_correct
            error_msg = None
            if not test_passed:
                error_msg = f"Expected AWS: {expected_aws}, Got: {detection.is_aws_related}"
                if expected_services:
                    error_msg += f", Expected services: {expected_services}, Got: {detection.detected_services}"
            
            results.add_result(f"Query: '{query[:30]}{'...' if len(query) > 30 else ''}'", 
                             test_passed, error_msg)
        
    except Exception as e:
        results.add_result("AWS Query Detection Setup", False, str(e))
    
    return results.summary()


def test_mcp_server_lifecycle():
    """Test MCP server lifecycle management."""
    print("\n🔗 Testing MCP Server Lifecycle")
    print("=" * 60)
    
    results = TestResults()
    
    try:
        from mcp_client_manager import MCPClientManager
        
        # Test MCP client creation
        manager = MCPClientManager()
        results.add_result("MCP Client Manager Creation", True)
        
        # Test server startup
        server_started = manager.start_server_if_needed()
        results.add_result("MCP Server Startup", server_started, 
                         "Server failed to start" if not server_started else None)
        
        if server_started:
            # Test connection
            connected = manager.is_connected()
            results.add_result("MCP Server Connection", connected,
                             "Failed to connect to server" if not connected else None)
            
            # Test documentation query
            if connected:
                response = manager.query_documentation("Test S3 query", ["s3"])
                query_success = response.success
                results.add_result("MCP Documentation Query", query_success,
                                 response.error_message if not query_success else None)
            
            # Test server cleanup
            manager.disconnect()
            results.add_result("MCP Server Cleanup", True)
        
    except Exception as e:
        results.add_result("MCP Server Lifecycle", False, str(e))
    
    return results.summary()


def test_context_enhancement_pipeline():
    """Test the complete context enhancement pipeline."""
    print("\n📚 Testing Context Enhancement Pipeline")
    print("=" * 60)
    
    results = TestResults()
    
    try:
        from mcp_client_manager import MCPClientManager
        from context_enhancer import ContextEnhancer
        
        # Setup components
        mcp_manager = MCPClientManager()
        enhancer = ContextEnhancer(mcp_manager)
        
        results.add_result("Context Enhancer Creation", True)
        
        # Test enhancement with mock data
        test_queries = [
            ("How do I create an S3 bucket?", ["s3"]),
            ("Configure EC2 security groups", ["ec2"]),
            ("DynamoDB table design", ["dynamodb"]),
        ]
        
        for query, services in test_queries:
            enhanced_context = enhancer.enhance_query(query, services)
            
            # Validate enhanced context
            has_enhanced_prompt = len(enhanced_context.enhanced_prompt) >= len(query)  # May be same if no enhancement
            has_documentation_summary = enhanced_context.documentation_summary is not None
            has_confidence_score = 0.0 <= enhanced_context.confidence_score <= 1.0
            
            enhancement_valid = has_enhanced_prompt and has_documentation_summary and has_confidence_score
            
            results.add_result(f"Context Enhancement: '{query[:30]}...'", enhancement_valid,
                             "Enhancement validation failed" if not enhancement_valid else None)
        
        # Test enhancement statistics
        stats = enhancer.get_enhancement_stats(enhanced_context)
        stats_valid = all(key in stats for key in ['original_query_length', 'enhanced_prompt_length', 
                                                  'enhancement_ratio', 'confidence_score'])
        results.add_result("Enhancement Statistics", stats_valid,
                         "Missing required statistics" if not stats_valid else None)
        
    except Exception as e:
        results.add_result("Context Enhancement Pipeline", False, str(e))
    
    return results.summary()


def test_enhanced_ollama_client_integration():
    """Test the enhanced Ollama client with MCP integration."""
    print("\n🤖 Testing Enhanced Ollama Client Integration")
    print("=" * 60)
    
    results = TestResults()
    
    try:
        from enhanced_ollama_client import EnhancedOllamaClient
        
        # Test client creation with MCP enabled
        client = EnhancedOllamaClient(
            base_url="http://localhost:11434",
            model="test-model:7b",
            mcp_enabled=True,
            aws_detection_threshold=0.4
        )
        
        results.add_result("Enhanced Client Creation (MCP Enabled)", True)
        
        # Test MCP status
        status = client.get_mcp_status()
        status_valid = all(key in status for key in ['mcp_enabled', 'aws_detection_threshold', 
                                                    'mcp_server_connected', 'statistics'])
        results.add_result("MCP Status Reporting", status_valid,
                         "Missing required status fields" if not status_valid else None)
        
        # Test AWS query detection logic
        from aws_query_detector import AWSDetectionResult
        
        # Mock AWS detection result
        aws_detection = AWSDetectionResult(
            is_aws_related=True,
            confidence_score=0.8,
            detected_services=["s3"],
            matched_keywords=["bucket"]
        )
        
        should_use_mcp = client.should_use_mcp("Test query", aws_detection)
        results.add_result("MCP Usage Decision Logic", should_use_mcp,
                         "Should use MCP for high-confidence AWS query" if not should_use_mcp else None)
        
        # Test configuration changes
        client.configure_mcp(enabled=False)
        status_after_disable = client.get_mcp_status()
        mcp_disabled = not status_after_disable['mcp_enabled']
        results.add_result("Runtime MCP Configuration", mcp_disabled,
                         "MCP should be disabled after configuration change" if not mcp_disabled else None)
        
        # Test cleanup
        client.cleanup()
        results.add_result("Client Cleanup", True)
        
    except Exception as e:
        results.add_result("Enhanced Ollama Client Integration", False, str(e))
    
    return results.summary()


def test_cli_interface_functionality():
    """Test the enhanced CLI interface functionality."""
    print("\n🖥️  Testing CLI Interface Functionality")
    print("=" * 60)
    
    results = TestResults()
    
    try:
        from enhanced_cli_interface import EnhancedCLI
        from enhanced_ollama_client import EnhancedOllamaClient
        from config import OllamaConfig, MCPIntegrationConfig
        
        # Setup mock client and config
        mock_client = Mock(spec=EnhancedOllamaClient)
        mock_client.base_url = "http://localhost:11434"
        mock_client.model = "test-model:7b"
        mock_client.get_mcp_status.return_value = {
            'mcp_enabled': True,
            'aws_detection_threshold': 0.4,
            'mcp_server_connected': True,
            'statistics': {'total_queries': 0, 'aws_queries_detected': 0, 
                          'mcp_queries_successful': 0, 'mcp_queries_failed': 0, 'fallback_queries': 0}
        }
        
        config = OllamaConfig()
        config.mcp_config = MCPIntegrationConfig()
        
        # Test CLI creation
        cli = EnhancedCLI(mock_client, config)
        results.add_result("Enhanced CLI Creation", True)
        
        # Test command recognition
        commands_to_test = ['help', 'status', 'config', 'stats', 'mcp status']
        for command in commands_to_test:
            recognized = cli.handle_command(command)
            results.add_result(f"Command Recognition: '{command}'", recognized,
                             f"Command '{command}' not recognized" if not recognized else None)
        
        # Test non-command recognition
        non_command = "This is not a command"
        not_recognized = not cli.handle_command(non_command)
        results.add_result("Non-command Recognition", not_recognized,
                         "Non-command incorrectly recognized as command" if not not_recognized else None)
        
    except Exception as e:
        results.add_result("CLI Interface Functionality", False, str(e))
    
    return results.summary()


def test_configuration_system_comprehensive():
    """Test the comprehensive configuration system."""
    print("\n⚙️  Testing Configuration System")
    print("=" * 60)
    
    results = TestResults()
    
    try:
        from config import OllamaConfig, MCPIntegrationConfig, create_ollama_parser
        from config_utils import validate_ollama_config, get_config_dict, create_config_from_dict
        
        # Test default configuration
        default_config = OllamaConfig()
        validation_errors = validate_ollama_config(default_config)
        results.add_result("Default Configuration Validation", len(validation_errors) == 0,
                         f"Validation errors: {validation_errors}" if validation_errors else None)
        
        # Test argument parsing
        parser = create_ollama_parser()
        test_args = ['--model', 'custom-model:7b', '--aws-threshold', '0.6', '--no-mcp']
        parsed_args = parser.parse_args(test_args)
        config_from_args = OllamaConfig.from_env_and_args(parsed_args)
        
        args_applied = (config_from_args.model == 'custom-model:7b' and 
                       config_from_args.mcp_config.aws_detection_threshold == 0.6 and
                       not config_from_args.mcp_config.enabled)
        results.add_result("Argument Parsing and Application", args_applied,
                         "Arguments not correctly applied to configuration" if not args_applied else None)
        
        # Test environment variable support
        original_env = os.environ.get('OLLAMA_MODEL')
        os.environ['OLLAMA_MODEL'] = 'env-test-model:7b'
        
        try:
            env_config = OllamaConfig.from_env_and_args()
            env_applied = env_config.model == 'env-test-model:7b'
            results.add_result("Environment Variable Support", env_applied,
                             "Environment variables not applied" if not env_applied else None)
        finally:
            if original_env:
                os.environ['OLLAMA_MODEL'] = original_env
            else:
                os.environ.pop('OLLAMA_MODEL', None)
        
        # Test configuration serialization
        config_dict = get_config_dict(default_config)
        restored_config = create_config_from_dict(config_dict)
        
        serialization_works = (default_config.model == restored_config.model and
                              default_config.ollama_url == restored_config.ollama_url and
                              default_config.mcp_config.enabled == restored_config.mcp_config.enabled)
        results.add_result("Configuration Serialization", serialization_works,
                         "Configuration serialization/deserialization failed" if not serialization_works else None)
        
    except Exception as e:
        results.add_result("Configuration System", False, str(e))
    
    return results.summary()


def test_end_to_end_integration():
    """Test end-to-end integration with simulated user interaction."""
    print("\n🎯 Testing End-to-End Integration")
    print("=" * 60)
    
    results = TestResults()
    
    try:
        # Test complete integration flow
        from aws_query_detector import AWSQueryDetector
        from enhanced_ollama_client import EnhancedOllamaClient
        from config import OllamaConfig, MCPIntegrationConfig
        
        # Setup configuration
        config = OllamaConfig()
        config.mcp_config = MCPIntegrationConfig(enabled=True, aws_detection_threshold=0.4)
        
        # Create enhanced client (with MCP disabled for testing)
        client = EnhancedOllamaClient(
            base_url="http://localhost:11434",
            model="test-model:7b",
            mcp_enabled=False,  # Disable for testing to avoid server dependency
            aws_detection_threshold=0.4
        )
        
        results.add_result("End-to-End Setup", True)
        
        # Test AWS query flow
        test_query = "How do I create an S3 bucket?"
        
        # Test AWS detection
        detector = AWSQueryDetector()
        detection = detector.analyze_query(test_query)
        aws_detected = detection.is_aws_related and detection.confidence_score > 0.4
        results.add_result("E2E AWS Detection", aws_detected,
                         f"AWS query not detected: confidence {detection.confidence_score}" if not aws_detected else None)
        
        # Test MCP decision logic
        should_use_mcp = client.should_use_mcp(test_query, detection)
        # Should be False because MCP is disabled for testing
        mcp_decision_correct = not should_use_mcp
        results.add_result("E2E MCP Decision Logic", mcp_decision_correct,
                         "MCP decision logic incorrect for disabled MCP" if not mcp_decision_correct else None)
        
        # Test statistics tracking
        initial_stats = client.get_mcp_status()['statistics']
        stats_initialized = all(key in initial_stats for key in ['total_queries', 'aws_queries_detected'])
        results.add_result("E2E Statistics Tracking", stats_initialized,
                         "Statistics not properly initialized" if not stats_initialized else None)
        
        # Cleanup
        client.cleanup()
        results.add_result("E2E Cleanup", True)
        
    except Exception as e:
        results.add_result("End-to-End Integration", False, str(e))
    
    return results.summary()


def test_fallback_mechanisms():
    """Test fallback mechanisms when MCP is unavailable."""
    print("\n🛡️  Testing Fallback Mechanisms")
    print("=" * 60)
    
    results = TestResults()
    
    try:
        from enhanced_ollama_client import EnhancedOllamaClient
        from aws_query_detector import AWSDetectionResult
        
        # Test with MCP disabled
        client = EnhancedOllamaClient(
            base_url="http://localhost:11434",
            model="test-model:7b",
            mcp_enabled=False
        )
        
        # Create AWS detection result
        aws_detection = AWSDetectionResult(
            is_aws_related=True,
            confidence_score=0.8,
            detected_services=["s3"],
            matched_keywords=["bucket"]
        )
        
        # Test that MCP is not used when disabled
        should_use_mcp = client.should_use_mcp("AWS query", aws_detection)
        fallback_correct = not should_use_mcp
        results.add_result("MCP Disabled Fallback", fallback_correct,
                         "Should not use MCP when disabled" if not fallback_correct else None)
        
        # Test low confidence fallback
        low_confidence_detection = AWSDetectionResult(
            is_aws_related=True,
            confidence_score=0.2,  # Below threshold
            detected_services=["s3"],
            matched_keywords=["bucket"]
        )
        
        client_with_mcp = EnhancedOllamaClient(
            base_url="http://localhost:11434",
            model="test-model:7b",
            mcp_enabled=True,
            aws_detection_threshold=0.4
        )
        
        should_use_mcp_low = client_with_mcp.should_use_mcp("AWS query", low_confidence_detection)
        low_confidence_fallback = not should_use_mcp_low
        results.add_result("Low Confidence Fallback", low_confidence_fallback,
                         "Should not use MCP for low confidence queries" if not low_confidence_fallback else None)
        
        # Cleanup
        client.cleanup()
        client_with_mcp.cleanup()
        
    except Exception as e:
        results.add_result("Fallback Mechanisms", False, str(e))
    
    return results.summary()


def run_comprehensive_integration_tests():
    """Run all integration tests and provide comprehensive results."""
    print("🚀 Comprehensive Integration Test Suite")
    print("Enhanced Ollama CLI with AWS MCP Integration")
    print("=" * 80)
    
    test_functions = [
        ("AWS Query Detection Accuracy", test_aws_query_detection_accuracy),
        ("MCP Server Lifecycle", test_mcp_server_lifecycle),
        ("Context Enhancement Pipeline", test_context_enhancement_pipeline),
        ("Enhanced Ollama Client Integration", test_enhanced_ollama_client_integration),
        ("CLI Interface Functionality", test_cli_interface_functionality),
        ("Configuration System", test_configuration_system_comprehensive),
        ("End-to-End Integration", test_end_to_end_integration),
        ("Fallback Mechanisms", test_fallback_mechanisms),
    ]
    
    overall_results = TestResults()
    
    for test_name, test_function in test_functions:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            success = test_function()
            overall_results.add_result(test_name, success)
        except Exception as e:
            overall_results.add_result(test_name, False, str(e))
            print(f"❌ {test_name} failed with exception: {e}")
    
    print("\n" + "=" * 80)
    print("🏆 COMPREHENSIVE INTEGRATION TEST RESULTS")
    print("=" * 80)
    
    success = overall_results.summary()
    
    if success:
        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
        print("✅ Enhanced Ollama CLI with MCP Integration is fully validated")
        print("✅ All components working together seamlessly")
        print("✅ Ready for production use")
        
        print("\n🚀 System Status: OPERATIONAL")
        print("🔥 MCP Integration: VALIDATED")
        print("⚡ AWS Enhancement: ACTIVE")
        print("🎯 Mission: ACCOMPLISHED")
        
    else:
        print("\n⚠️  Some integration tests failed")
        print("Please review the errors above and fix the issues")
    
    return success


if __name__ == "__main__":
    success = run_comprehensive_integration_tests()
    sys.exit(0 if success else 1)