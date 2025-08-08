#!/usr/bin/env python3
"""Test AWS query detection functionality."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aws_query_detector import AWSQueryDetector


def test_aws_detection():
    """Test AWS query detection with various query types."""
    detector = AWSQueryDetector()
    
    # Test cases: (query, expected_aws_related, min_confidence)
    test_cases = [
        # Clear AWS queries
        ("How do I create an S3 bucket?", True, 0.5),
        ("Configure EC2 instance with security groups", True, 0.6),
        ("AWS Lambda function deployment", True, 0.7),
        ("Set up RDS database on Amazon Web Services", True, 0.8),
        
        # AWS with context
        ("I need help with DynamoDB table design", True, 0.4),
        ("CloudFormation template for VPC setup", True, 0.6),
        ("Monitor my application using CloudWatch", True, 0.5),
        
        # Borderline cases
        ("Deploy my application to the cloud", False, 0.4),
        ("Database configuration help", False, 0.2),
        ("How to scale my web application?", False, 0.2),
        
        # Non-AWS queries
        ("What is machine learning?", False, 0.1),
        ("Python programming tutorial", False, 0.1),
        ("How to cook pasta?", False, 0.0),
        
        # Edge cases
        ("", False, 0.0),
        ("aws", True, 0.4),
        ("Amazon", False, 0.2),  # Just "Amazon" without context
    ]
    
    print("🧪 Testing AWS Query Detection")
    print("=" * 60)
    
    passed = 0
    total = len(test_cases)
    
    for query, expected_aws, min_confidence in test_cases:
        result = detector.analyze_query(query)
        
        # Check if detection matches expectation
        detection_correct = result.is_aws_related == expected_aws
        
        # Check if confidence meets minimum threshold
        confidence_ok = result.confidence_score >= min_confidence if expected_aws else True
        
        test_passed = detection_correct and confidence_ok
        
        status = "✅" if test_passed else "❌"
        print(f"{status} Query: '{query}'")
        print(f"   Expected AWS: {expected_aws}, Got: {result.is_aws_related}")
        print(f"   Confidence: {result.confidence_score:.2f} (min: {min_confidence})")
        
        if result.detected_services:
            print(f"   Services: {', '.join(result.detected_services)}")
        if result.matched_keywords:
            print(f"   Keywords: {', '.join(result.matched_keywords)}")
        
        print(f"   Summary: {detector.get_detection_summary(query)}")
        print()
        
        if test_passed:
            passed += 1
    
    print("=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All AWS detection tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Check the detection logic.")
        return False


def test_service_extraction():
    """Test AWS service extraction functionality."""
    detector = AWSQueryDetector()
    
    print("\n🔍 Testing AWS Service Extraction")
    print("=" * 60)
    
    test_queries = [
        "How do I connect S3 to Lambda?",
        "Set up RDS with EC2 and CloudWatch monitoring",
        "DynamoDB and API Gateway integration",
        "Use CloudFormation to deploy ECS cluster",
        "Configure VPC with multiple subnets and security groups"
    ]
    
    for query in test_queries:
        result = detector.analyze_query(query)
        print(f"Query: '{query}'")
        print(f"Services: {', '.join(result.detected_services) if result.detected_services else 'None'}")
        print(f"Confidence: {result.confidence_score:.2f}")
        print()


if __name__ == "__main__":
    success = test_aws_detection()
    test_service_extraction()
    
    if success:
        print("✅ AWS Query Detector is ready!")
    else:
        print("❌ AWS Query Detector needs improvements.")