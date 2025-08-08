#!/usr/bin/env python3
"""AWS query detection system for identifying AWS-related queries."""

import re
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class AWSDetectionResult:
    """Result of AWS query detection."""
    is_aws_related: bool
    confidence_score: float
    detected_services: List[str]
    matched_keywords: List[str]


class AWSQueryDetector:
    """Detects AWS-related queries and extracts relevant AWS services."""
    
    def __init__(self):
        """Initialize the AWS query detector with comprehensive AWS terminology."""
        self.aws_services = {
            # Compute
            'ec2', 'lambda', 'ecs', 'eks', 'fargate', 'batch', 'lightsail',
            'elastic compute cloud', 'elastic container service', 'elastic kubernetes service',
            
            # Storage
            's3', 'ebs', 'efs', 'fsx', 'glacier', 'storage gateway',
            'simple storage service', 'elastic block store', 'elastic file system',
            
            # Database
            'rds', 'dynamodb', 'redshift', 'aurora', 'documentdb', 'neptune',
            'elasticache', 'timestream', 'keyspaces', 'qldb',
            'relational database service',
            
            # Networking
            'vpc', 'cloudfront', 'route53', 'api gateway', 'direct connect',
            'elastic load balancer', 'elb', 'alb', 'nlb', 'transit gateway',
            'virtual private cloud',
            
            # Security
            'iam', 'cognito', 'secrets manager', 'kms', 'acm', 'waf', 'shield',
            'identity and access management', 'key management service',
            'certificate manager', 'web application firewall',
            
            # Monitoring & Management
            'cloudwatch', 'cloudtrail', 'config', 'systems manager', 'cloudformation',
            'cdk', 'x-ray', 'personal health dashboard', 'trusted advisor',
            
            # Analytics
            'athena', 'emr', 'kinesis', 'quicksight', 'glue', 'data pipeline',
            'elastic mapreduce', 'elasticsearch service', 'opensearch',
            
            # Machine Learning
            'sagemaker', 'rekognition', 'comprehend', 'translate', 'polly',
            'lex', 'textract', 'transcribe', 'personalize', 'forecast',
            
            # Developer Tools
            'codecommit', 'codebuild', 'codedeploy', 'codepipeline', 'codestar',
            'cloud9', 'x-ray', 'cloudshell',
            
            # Integration
            'sns', 'sqs', 'eventbridge', 'step functions', 'mq', 'appflow',
            'simple notification service', 'simple queue service',
            
            # Content Delivery
            'cloudfront', 'global accelerator', 'route 53',
        }
        
        self.aws_keywords = {
            # General AWS terms
            'aws', 'amazon web services', 'amazon', 'cloud',
            
            # Common AWS concepts
            'region', 'availability zone', 'az', 'vpc', 'subnet', 'security group',
            'arn', 'resource', 'policy', 'role', 'user', 'group', 'permission',
            'bucket', 'instance', 'cluster', 'node', 'endpoint', 'console',
            
            # AWS-specific actions
            'deploy', 'provision', 'configure', 'setup', 'create', 'launch',
            'terminate', 'scale', 'monitor', 'backup', 'restore',
            
            # AWS pricing and billing
            'pricing', 'cost', 'billing', 'free tier', 'reserved instance',
            'spot instance', 'on-demand', 'savings plan',
            
            # AWS CLI and tools
            'aws cli', 'cloudformation', 'terraform', 'cdk', 'sam', 'amplify',
        }
        
        # Compile regex patterns for efficient matching
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for efficient matching."""
        # Create patterns for services (case-insensitive, word boundaries)
        service_patterns = []
        for service in self.aws_services:
            # Handle multi-word services
            if ' ' in service:
                pattern = r'\b' + re.escape(service) + r'\b'
            else:
                pattern = r'\b' + re.escape(service) + r'\b'
            service_patterns.append(pattern)
        
        self.service_regex = re.compile('|'.join(service_patterns), re.IGNORECASE)
        
        # Create patterns for keywords
        keyword_patterns = []
        for keyword in self.aws_keywords:
            if ' ' in keyword:
                pattern = r'\b' + re.escape(keyword) + r'\b'
            else:
                pattern = r'\b' + re.escape(keyword) + r'\b'
            keyword_patterns.append(pattern)
        
        self.keyword_regex = re.compile('|'.join(keyword_patterns), re.IGNORECASE)
    
    def is_aws_related(self, query: str) -> bool:
        """
        Check if a query is AWS-related.
        
        Args:
            query: The user query to analyze
            
        Returns:
            True if the query appears to be AWS-related
        """
        result = self.analyze_query(query)
        return result.is_aws_related
    
    def extract_aws_services(self, query: str) -> List[str]:
        """
        Extract AWS services mentioned in the query.
        
        Args:
            query: The user query to analyze
            
        Returns:
            List of AWS services found in the query
        """
        result = self.analyze_query(query)
        return result.detected_services
    
    def get_confidence_score(self, query: str) -> float:
        """
        Get confidence score for AWS-related query detection.
        
        Args:
            query: The user query to analyze
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        result = self.analyze_query(query)
        return result.confidence_score
    
    def analyze_query(self, query: str) -> AWSDetectionResult:
        """
        Perform comprehensive analysis of the query for AWS content.
        
        Args:
            query: The user query to analyze
            
        Returns:
            AWSDetectionResult with detailed analysis
        """
        if not query or not query.strip():
            return AWSDetectionResult(False, 0.0, [], [])
        
        query_lower = query.lower().strip()
        
        # Find AWS services
        service_matches = self.service_regex.findall(query)
        detected_services = list(set([match.lower() for match in service_matches]))
        
        # Find AWS keywords
        keyword_matches = self.keyword_regex.findall(query)
        matched_keywords = list(set([match.lower() for match in keyword_matches]))
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence(
            query_lower, detected_services, matched_keywords
        )
        
        # Determine if AWS-related (threshold: 0.4 for better precision)
        is_aws_related = confidence_score >= 0.4
        
        return AWSDetectionResult(
            is_aws_related=is_aws_related,
            confidence_score=confidence_score,
            detected_services=detected_services,
            matched_keywords=matched_keywords
        )
    
    def _calculate_confidence(self, query: str, services: List[str], keywords: List[str]) -> float:
        """
        Calculate confidence score based on detected services and keywords.
        
        Args:
            query: The original query (lowercase)
            services: List of detected AWS services
            keywords: List of detected AWS keywords
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        score = 0.0
        
        # Base score for AWS services (high weight)
        if services:
            service_score = min(len(services) * 0.4, 0.8)  # Max 0.8 for services
            score += service_score
        
        # Score for AWS keywords (medium weight)
        if keywords:
            # Reduce weight for generic terms like 'cloud'
            weighted_keywords = []
            for keyword in keywords:
                if keyword in ['cloud']:
                    weighted_keywords.append(0.1)  # Lower weight for generic terms
                else:
                    weighted_keywords.append(0.2)  # Normal weight
            
            keyword_score = min(sum(weighted_keywords), 0.6)  # Max 0.6 for keywords
            score += keyword_score
        
        # Bonus for explicit AWS mentions
        if 'aws' in query or 'amazon web services' in query:
            score += 0.3
        
        # Bonus for cloud-related context (only if other AWS indicators present)
        if services or any(keyword in ['aws', 'amazon web services'] for keyword in keywords):
            cloud_terms = ['cloud', 'deploy', 'provision', 'configure', 'setup']
            cloud_mentions = sum(1 for term in cloud_terms if term in query)
            if cloud_mentions > 0:
                score += min(cloud_mentions * 0.1, 0.2)
        
        # Penalty for very short queries (less reliable)
        if len(query.split()) < 3:
            score *= 0.8
        
        # Ensure score is between 0.0 and 1.0
        return min(max(score, 0.0), 1.0)
    
    def get_detection_summary(self, query: str) -> str:
        """
        Get a human-readable summary of the detection results.
        
        Args:
            query: The user query to analyze
            
        Returns:
            Summary string describing the detection results
        """
        result = self.analyze_query(query)
        
        if not result.is_aws_related:
            return "No AWS content detected"
        
        summary_parts = []
        summary_parts.append(f"AWS query detected (confidence: {result.confidence_score:.2f})")
        
        if result.detected_services:
            services_str = ", ".join(result.detected_services[:3])  # Show max 3 services
            if len(result.detected_services) > 3:
                services_str += f" and {len(result.detected_services) - 3} more"
            summary_parts.append(f"Services: {services_str}")
        
        if result.matched_keywords:
            keywords_str = ", ".join(result.matched_keywords[:3])  # Show max 3 keywords
            if len(result.matched_keywords) > 3:
                keywords_str += f" and {len(result.matched_keywords) - 3} more"
            summary_parts.append(f"Keywords: {keywords_str}")
        
        return " | ".join(summary_parts)