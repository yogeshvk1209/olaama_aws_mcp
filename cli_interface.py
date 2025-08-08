#!/usr/bin/env python3
"""CLI interface components for Ollama and MCP scripts."""

import logging
from typing import Optional
from ollama_client import OllamaClient


class CLI:
    """Command-line interface for Ollama client."""
    
    def __init__(self, client: OllamaClient, logger: Optional[logging.Logger] = None):
        """
        Initialize CLI interface.
        
        Args:
            client: OllamaClient instance for LLM communication
            logger: Logger instance for logging user interactions
        """
        self.client = client
        self.logger = logger or logging.getLogger(__name__)
    
    def run(self) -> None:
        """
        Run the interactive CLI session.
        """
        self.logger.info("Starting CLI session")
        self.display_welcome()
        self.client.start_conversation()
        self.logger.info("CLI session ended")
    
    def display_welcome(self) -> None:
        """Display welcome message to user."""
        print("=" * 60)
        print("🤖 Ollama CLI Client")
        print("=" * 60)
        print(f"Connected to: {self.client.base_url}")
        print(f"Using model: {self.client.model}")
        print("\nCommands:")
        print("  - Type your message and press Enter")
        print("  - Type 'quit', 'exit', or 'q' to end")
        print("  - Press Ctrl+C to interrupt")
        print("=" * 60)
    
    def get_user_input(self) -> str:
        """
        Get input from user with prompt.
        
        Returns:
            User input string
        """
        return input("You: ").strip()
    
    def display_response(self, response: str) -> None:
        """
        Display LLM response to user.
        
        Args:
            response: Response text from LLM
        """
        print(f"Assistant: {response}\n")
        self.logger.info(f"Displayed response: {response[:100]}...")
    
    def display_error(self, error: str) -> None:
        """
        Display error message to user.
        
        Args:
            error: Error message to display
        """
        print(f"❌ Error: {error}")
        self.logger.error(f"Displayed error: {error}")
    
    def display_info(self, message: str) -> None:
        """
        Display informational message to user.
        
        Args:
            message: Info message to display
        """
        print(f"ℹ️  {message}")
        self.logger.info(f"Displayed info: {message}")