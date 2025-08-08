#!/usr/bin/env python3
"""Enhanced Ollama client with MCP integration for AWS documentation."""

import logging
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass

from .ollama_client import OllamaClient
from .aws_query_detector import AWSQueryDetector, AWSDetectionResult
from .mcp_client_manager import MCPClientManager
from .context_enhancer import ContextEnhancer, EnhancedContext


@dataclass
class EnhancedResponse:
    """Enhanced response with MCP integration details."""
    llm_response: str
    mcp_used: bool
    aws_detection: AWSDetectionResult
    enhanced_context: Optional[EnhancedContext]
    processing_time: float
    fallback_reason: Optional[str] = None


class EnhancedOllamaClient(OllamaClient):
    """Enhanced Ollama client with AWS MCP integration."""
    
    def __init__(self, base_url: str, model: str, logger: Optional[logging.Logger] = None,
                 mcp_enabled: bool = True, aws_detection_threshold: float = 0.4,
                 auto_start_mcp: bool = False):
        """
        Initialize enhanced Ollama client.
        
        Args:
            base_url: Ollama server URL
            model: Model name to use
            logger: Logger instance
            mcp_enabled: Whether to enable MCP integration
            aws_detection_threshold: Threshold for AWS query detection
            auto_start_mcp: Whether to start MCP server during initialization
        """
        super().__init__(base_url, model, logger)
        
        self.mcp_enabled = mcp_enabled
        self.aws_detection_threshold = aws_detection_threshold
        
        # Initialize components
        self.aws_detector = AWSQueryDetector()
        self.mcp_manager = MCPClientManager(logger=logger) if mcp_enabled else None
        self.context_enhancer = ContextEnhancer(self.mcp_manager) if mcp_enabled else None
        
        # Statistics
        self.stats = {
            "total_queries": 0,
            "aws_queries_detected": 0,
            "mcp_queries_successful": 0,
            "mcp_queries_failed": 0,
            "fallback_queries": 0
        }
        
        # Auto-start MCP server if requested
        if auto_start_mcp and self.mcp_manager:
            self.logger.info("Auto-starting MCP server during initialization")
            try:
                server_started = self.mcp_manager.start_server_if_needed()
                if server_started:
                    self.logger.info("MCP server auto-started successfully")
                else:
                    self.logger.warning("MCP server auto-start failed")
            except Exception as e:
                self.logger.error(f"MCP server auto-start error: {e}")
        
        self.logger.info(f"Enhanced Ollama client initialized (MCP enabled: {mcp_enabled})")
    
    def send_message_with_mcp(self, message: str) -> EnhancedResponse:
        """
        Send message with MCP integration for AWS queries.
        
        Args:
            message: User message
            
        Returns:
            EnhancedResponse with MCP integration details
        """
        start_time = time.time()
        
        self.stats["total_queries"] += 1
        
        # Detect if this is an AWS-related query
        aws_detection = self.aws_detector.analyze_query(message)
        
        self.logger.info(f"Query analysis: AWS={aws_detection.is_aws_related}, "
                        f"confidence={aws_detection.confidence_score:.2f}")
        
        # Determine if we should use MCP
        should_use_mcp = self.should_use_mcp(message, aws_detection)
        
        if should_use_mcp:
            return self._send_with_mcp_enhancement(message, aws_detection, start_time)
        else:
            return self._send_regular_message_enhanced(message, aws_detection, start_time)
    
    def should_use_mcp(self, message: str, aws_detection: AWSDetectionResult) -> bool:
        """
        Determine if MCP should be used for this query.
        
        Args:
            message: User message
            aws_detection: AWS detection results
            
        Returns:
            True if MCP should be used
        """
        if not self.mcp_enabled:
            return False
        
        if not aws_detection.is_aws_related:
            return False
        
        if aws_detection.confidence_score < self.aws_detection_threshold:
            return False
        
        return True
    
    def _send_with_mcp_enhancement(self, message: str, aws_detection: AWSDetectionResult, 
                                  start_time: float) -> EnhancedResponse:
        """
        Send message with MCP enhancement.
        
        Args:
            message: User message
            aws_detection: AWS detection results
            start_time: Start time for processing
            
        Returns:
            EnhancedResponse with MCP integration
        """
        self.stats["aws_queries_detected"] += 1
        
        try:
            # Ensure MCP server is running
            if not self.mcp_manager.is_connected():
                self.logger.info("Starting MCP server for AWS query")
                server_started = self.mcp_manager.start_server_if_needed()
                
                if not server_started:
                    self.logger.warning("Failed to start MCP server, falling back to regular query")
                    return self._send_fallback_response(message, aws_detection, start_time, 
                                                      "MCP server failed to start")
            
            # Enhance query with AWS documentation
            self.logger.info("Enhancing query with AWS documentation")
            enhanced_context = self.context_enhancer.enhance_query(
                message, aws_detection.detected_services
            )
            
            if enhanced_context.confidence_score < 0.3:
                self.logger.warning("Low confidence in documentation enhancement, using regular query")
                return self._send_fallback_response(message, aws_detection, start_time,
                                                  "Low documentation confidence")
            
            # Send enhanced query to LLM
            self.logger.info("Sending enhanced query to LLM")
            llm_response = super().send_message(enhanced_context.enhanced_prompt)
            
            self.stats["mcp_queries_successful"] += 1
            processing_time = time.time() - start_time
            
            self.logger.info(f"MCP-enhanced query completed in {processing_time:.2f}s")
            
            return EnhancedResponse(
                llm_response=llm_response,
                mcp_used=True,
                aws_detection=aws_detection,
                enhanced_context=enhanced_context,
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"MCP enhancement failed: {e}")
            self.stats["mcp_queries_failed"] += 1
            return self._send_fallback_response(message, aws_detection, start_time, str(e))
    
    def _send_regular_message_enhanced(self, message: str, aws_detection: AWSDetectionResult,
                                     start_time: float) -> EnhancedResponse:
        """
        Send regular message without MCP enhancement.
        
        Args:
            message: User message
            aws_detection: AWS detection results
            start_time: Start time for processing
            
        Returns:
            EnhancedResponse without MCP integration
        """
        self.logger.info("Sending regular query to LLM (no MCP enhancement)")
        
        llm_response = super().send_message(message)
        processing_time = time.time() - start_time
        
        return EnhancedResponse(
            llm_response=llm_response,
            mcp_used=False,
            aws_detection=aws_detection,
            enhanced_context=None,
            processing_time=processing_time
        )
    
    def _send_fallback_response(self, message: str, aws_detection: AWSDetectionResult,
                               start_time: float, fallback_reason: str) -> EnhancedResponse:
        """
        Send fallback response when MCP enhancement fails.
        
        Args:
            message: User message
            aws_detection: AWS detection results
            start_time: Start time for processing
            fallback_reason: Reason for fallback
            
        Returns:
            EnhancedResponse with fallback information
        """
        self.stats["fallback_queries"] += 1
        
        self.logger.info(f"Falling back to regular query: {fallback_reason}")
        
        llm_response = super().send_message(message)
        processing_time = time.time() - start_time
        
        return EnhancedResponse(
            llm_response=llm_response,
            mcp_used=False,
            aws_detection=aws_detection,
            enhanced_context=None,
            processing_time=processing_time,
            fallback_reason=fallback_reason
        )
    
    def send_regular_message(self, message: str) -> str:
        """
        Send regular message without any MCP integration.
        
        Args:
            message: User message
            
        Returns:
            LLM response string
        """
        return super().send_message(message)
    
    def start_conversation_with_mcp(self) -> None:
        """
        Start an interactive conversation with MCP integration.
        """
        self.logger.info(f"Starting MCP-enhanced conversation with {self.model}")
        print(f"\n🤖 Starting MCP-enhanced conversation with {self.model}")
        print("🔍 AWS queries will be automatically enhanced with official documentation")
        print("Type 'quit', 'exit', 'q', or 'stats' to end/view statistics.\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    self.logger.info("User ended MCP-enhanced conversation")
                    self._display_session_stats()
                    print("Goodbye!")
                    break
                
                if user_input.lower() == 'stats':
                    self._display_session_stats()
                    continue
                
                if not user_input:
                    continue
                
                # Send message with MCP integration
                enhanced_response = self.send_message_with_mcp(user_input)
                
                # Display response with MCP information
                self._display_enhanced_response(enhanced_response)
                
            except KeyboardInterrupt:
                self.logger.info("MCP-enhanced conversation interrupted by user")
                self._display_session_stats()
                print("\nGoodbye!")
                break
            except Exception as e:
                self.logger.error(f"Error during MCP-enhanced conversation: {e}")
                print(f"Error: {e}")
                continue
    
    def _display_enhanced_response(self, response: EnhancedResponse) -> None:
        """
        Display enhanced response with MCP integration information.
        
        Args:
            response: Enhanced response to display
        """
        # Show MCP status indicators
        if response.mcp_used:
            print("🔍 AWS query detected - enhanced with official documentation")
            if response.enhanced_context:
                print(f"📚 {response.enhanced_context.documentation_summary}")
                if response.enhanced_context.sources:
                    print(f"🔗 Sources: {len(response.enhanced_context.sources)} AWS documentation pages")
        elif response.aws_detection.is_aws_related:
            if response.fallback_reason:
                print(f"⚠️  AWS query detected but using fallback: {response.fallback_reason}")
            else:
                print("ℹ️  AWS query detected but MCP enhancement not used")
        
        # Show the LLM response
        print(f"Assistant: {response.llm_response}")
        
        # Show processing time and confidence
        if response.mcp_used and response.enhanced_context:
            print(f"⏱️  Response time: {response.processing_time:.2f}s "
                  f"(confidence: {response.enhanced_context.confidence_score:.2f})")
        else:
            print(f"⏱️  Response time: {response.processing_time:.2f}s")
        
        print()
    
    def _display_session_stats(self) -> None:
        """Display session statistics."""
        print("\n📊 Session Statistics:")
        print(f"   Total queries: {self.stats['total_queries']}")
        print(f"   AWS queries detected: {self.stats['aws_queries_detected']}")
        print(f"   MCP enhancements successful: {self.stats['mcp_queries_successful']}")
        print(f"   MCP enhancements failed: {self.stats['mcp_queries_failed']}")
        print(f"   Fallback queries: {self.stats['fallback_queries']}")
        
        if self.stats['total_queries'] > 0:
            aws_rate = (self.stats['aws_queries_detected'] / self.stats['total_queries']) * 100
            print(f"   AWS detection rate: {aws_rate:.1f}%")
            
            if self.stats['aws_queries_detected'] > 0:
                success_rate = (self.stats['mcp_queries_successful'] / self.stats['aws_queries_detected']) * 100
                print(f"   MCP success rate: {success_rate:.1f}%")
        print()
    
    def get_mcp_status(self) -> Dict[str, Any]:
        """
        Get current MCP integration status.
        
        Returns:
            Dictionary with MCP status information
        """
        status = {
            "mcp_enabled": self.mcp_enabled,
            "aws_detection_threshold": self.aws_detection_threshold,
            "mcp_server_connected": False,
            "statistics": self.stats.copy()
        }
        
        if self.mcp_manager:
            status["mcp_server_connected"] = self.mcp_manager.is_connected()
            status["mcp_server_info"] = self.mcp_manager.get_server_info()
        
        return status
    
    def configure_mcp(self, enabled: bool = None, threshold: float = None) -> None:
        """
        Configure MCP integration settings.
        
        Args:
            enabled: Enable/disable MCP integration
            threshold: AWS detection threshold
        """
        if enabled is not None:
            self.mcp_enabled = enabled
            self.logger.info(f"MCP integration {'enabled' if enabled else 'disabled'}")
        
        if threshold is not None:
            self.aws_detection_threshold = threshold
            self.logger.info(f"AWS detection threshold set to {threshold}")
    
    def cleanup(self) -> None:
        """Cleanup MCP resources."""
        if self.mcp_manager:
            self.mcp_manager.disconnect()
        self.logger.info("Enhanced Ollama client cleanup completed")