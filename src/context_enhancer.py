#!/usr/bin/env python3
"""Context enhancement system for integrating AWS documentation with LLM queries."""

import re
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from .mcp_client_manager import MCPClientManager, MCPResponse


@dataclass
class EnhancedContext:
    """Enhanced context with AWS documentation."""
    original_query: str
    enhanced_prompt: str
    documentation_summary: str
    sources: List[str]
    confidence_score: float
    processing_time: float


class ContextEnhancer:
    """Enhances user queries with AWS documentation context."""
    
    def __init__(self, mcp_manager: MCPClientManager):
        """
        Initialize context enhancer.
        
        Args:
            mcp_manager: MCP client manager for retrieving documentation
        """
        self.mcp_manager = mcp_manager
        self.max_context_length = 2000  # Maximum characters for context
        self.max_docs_per_query = 3     # Maximum documentation entries to include
    
    def enhance_query(self, original_query: str, aws_services: List[str] = None) -> EnhancedContext:
        """
        Enhance a query with AWS documentation context.
        
        Args:
            original_query: The original user query
            aws_services: List of detected AWS services (optional)
            
        Returns:
            EnhancedContext with documentation and enhanced prompt
        """
        start_time = time.time()
        
        # Query MCP server for documentation
        mcp_response = self.mcp_manager.query_documentation(original_query, aws_services)
        
        if not mcp_response.success:
            # Return original query if no documentation available
            return EnhancedContext(
                original_query=original_query,
                enhanced_prompt=original_query,
                documentation_summary="No AWS documentation available",
                sources=[],
                confidence_score=0.0,
                processing_time=time.time() - start_time
            )
        
        # Format documentation for LLM consumption
        formatted_docs = self.format_documentation(mcp_response)
        
        # Create enhanced prompt
        enhanced_prompt = self.create_enhanced_prompt(original_query, formatted_docs)
        
        # Create documentation summary
        doc_summary = self.create_documentation_summary(mcp_response.documentation)
        
        # Calculate confidence score based on documentation quality
        confidence_score = self.calculate_confidence_score(mcp_response)
        
        processing_time = time.time() - start_time
        
        return EnhancedContext(
            original_query=original_query,
            enhanced_prompt=enhanced_prompt,
            documentation_summary=doc_summary,
            sources=mcp_response.sources,
            confidence_score=confidence_score,
            processing_time=processing_time
        )
    
    def format_documentation(self, mcp_response: MCPResponse) -> str:
        """
        Format AWS documentation for LLM consumption.
        
        Args:
            mcp_response: Response from MCP server with documentation
            
        Returns:
            Formatted documentation string
        """
        if not mcp_response.documentation:
            return ""
        
        formatted_sections = []
        
        # Sort documentation by relevance score if available
        sorted_docs = sorted(
            mcp_response.documentation[:self.max_docs_per_query],
            key=lambda x: x.get('relevance_score', 0.5),
            reverse=True
        )
        
        for i, doc in enumerate(sorted_docs, 1):
            title = doc.get('title', 'AWS Documentation')
            content = doc.get('content', '')
            service = doc.get('service', 'general')
            url = doc.get('url', '')
            
            # Clean and truncate content
            cleaned_content = self.clean_documentation_content(content)
            
            # Format as a numbered section
            section = f"""
{i}. {title} ({service.upper()})
{cleaned_content}
Source: {url}
"""
            formatted_sections.append(section.strip())
        
        return "\n\n".join(formatted_sections)
    
    def clean_documentation_content(self, content: str) -> str:
        """
        Clean and format documentation content for LLM consumption.
        
        Args:
            content: Raw documentation content
            
        Returns:
            Cleaned and formatted content
        """
        if not content:
            return "No content available"
        
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content.strip())
        
        # Remove HTML tags if present
        content = re.sub(r'<[^>]+>', '', content)
        
        # Remove URLs that are too long (keep domain only)
        content = re.sub(r'https?://[^\s]+', '[URL]', content)
        
        # Truncate if too long
        max_content_length = self.max_context_length // self.max_docs_per_query
        if len(content) > max_content_length:
            content = content[:max_content_length - 3] + "..."
        
        return content
    
    def create_enhanced_prompt(self, original_query: str, formatted_docs: str) -> str:
        """
        Create an enhanced prompt combining the original query with AWS documentation.
        
        Args:
            original_query: The original user query
            formatted_docs: Formatted AWS documentation
            
        Returns:
            Enhanced prompt for the LLM
        """
        if not formatted_docs.strip():
            return original_query
        
        enhanced_prompt = f"""Please answer the following question using both your knowledge and the official AWS documentation provided below.

User Question: {original_query}

Official AWS Documentation:
{formatted_docs}

Instructions:
- Use the official AWS documentation as the primary source for technical details
- Supplement with your general knowledge where appropriate
- If the documentation doesn't fully answer the question, clearly indicate what information is missing
- Provide practical, actionable advice when possible
- Include relevant AWS service names and concepts from the documentation

Answer:"""
        
        return enhanced_prompt
    
    def create_documentation_summary(self, documentation: List[Dict[str, Any]]) -> str:
        """
        Create a brief summary of the documentation sources used.
        
        Args:
            documentation: List of documentation entries
            
        Returns:
            Summary string describing the documentation
        """
        if not documentation:
            return "No documentation sources"
        
        services = set()
        titles = []
        
        for doc in documentation[:self.max_docs_per_query]:
            service = doc.get('service', 'general')
            title = doc.get('title', 'AWS Documentation')
            
            services.add(service.upper())
            titles.append(title[:50] + "..." if len(title) > 50 else title)
        
        services_str = ", ".join(sorted(services))
        summary = f"Retrieved {len(documentation)} AWS documentation entries"
        
        if services:
            summary += f" covering {services_str}"
        
        return summary
    
    def calculate_confidence_score(self, mcp_response: MCPResponse) -> float:
        """
        Calculate confidence score based on documentation quality and relevance.
        
        Args:
            mcp_response: Response from MCP server
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        if not mcp_response.success or not mcp_response.documentation:
            return 0.0
        
        score = 0.0
        
        # Base score for having documentation
        score += 0.3
        
        # Score based on number of documentation entries
        num_docs = len(mcp_response.documentation)
        score += min(num_docs * 0.2, 0.4)  # Max 0.4 for quantity
        
        # Score based on content quality
        total_content_length = 0
        for doc in mcp_response.documentation:
            content = doc.get('content', '')
            if content and len(content.strip()) > 50:  # Meaningful content
                score += 0.1
                total_content_length += len(content)
        
        # Bonus for substantial content
        if total_content_length > 500:
            score += 0.1
        
        # Score based on response time (faster is better)
        if mcp_response.query_time < 1.0:
            score += 0.1
        elif mcp_response.query_time < 2.0:
            score += 0.05
        
        # Ensure score is between 0.0 and 1.0
        return min(max(score, 0.0), 1.0)
    
    def get_enhancement_stats(self, enhanced_context: EnhancedContext) -> Dict[str, Any]:
        """
        Get statistics about the context enhancement.
        
        Args:
            enhanced_context: The enhanced context to analyze
            
        Returns:
            Dictionary with enhancement statistics
        """
        original_length = len(enhanced_context.original_query)
        enhanced_length = len(enhanced_context.enhanced_prompt)
        
        return {
            "original_query_length": original_length,
            "enhanced_prompt_length": enhanced_length,
            "enhancement_ratio": enhanced_length / original_length if original_length > 0 else 0,
            "documentation_sources": len(enhanced_context.sources),
            "confidence_score": enhanced_context.confidence_score,
            "processing_time": enhanced_context.processing_time,
            "documentation_summary": enhanced_context.documentation_summary
        }
    
    def preview_enhancement(self, query: str, aws_services: List[str] = None) -> str:
        """
        Get a preview of how a query would be enhanced without full processing.
        
        Args:
            query: The query to preview
            aws_services: List of AWS services (optional)
            
        Returns:
            Preview string showing enhancement approach
        """
        preview = f"Original Query: {query}\n"
        preview += f"Detected Services: {', '.join(aws_services) if aws_services else 'None'}\n"
        preview += f"Enhancement Approach: Query AWS documentation for {', '.join(aws_services) if aws_services else 'general AWS topics'}\n"
        preview += f"Expected Context: Official AWS documentation will be retrieved and formatted for LLM consumption\n"
        
        return preview