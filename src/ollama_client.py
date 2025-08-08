#!/usr/bin/env python3
"""Ollama client for HTTP communication with local Ollama server."""

import json
import requests
import logging
from typing import Dict, Any, Optional


class OllamaClient:
    """Client for communicating with Ollama LLM server."""
    
    def __init__(self, base_url: str, model: str, logger: Optional[logging.Logger] = None):
        """
        Initialize Ollama client.
        
        Args:
            base_url: Base URL of Ollama server (e.g., http://localhost:11434)
            model: Model name to use for generation
            logger: Logger instance for logging requests/responses
        """
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.logger = logger or logging.getLogger(__name__)
        self.generate_url = f"{self.base_url}/api/generate"
    
    def send_message(self, message: str) -> str:
        """
        Send a message to the LLM and return the response.
        
        Args:
            message: User message to send to the LLM
            
        Returns:
            LLM response as string
        """
        self.logger.info(f"Sending message to {self.model}: {message[:100]}...")
        
        payload = {
            "model": self.model,
            "prompt": message,
            "stream": False
        }
        
        response = requests.post(
            self.generate_url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        response.raise_for_status()
        result = response.json()
        
        llm_response = result.get("response", "")
        self.logger.info(f"Received response from {self.model}: {llm_response[:100]}...")
        
        return llm_response
    
    def start_conversation(self) -> None:
        """
        Start an interactive conversation loop with the LLM.
        """
        self.logger.info(f"Starting conversation with {self.model}")
        print(f"\nStarting conversation with {self.model}")
        print("Type 'quit', 'exit', or 'q' to end the conversation.\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    self.logger.info("User ended conversation")
                    print("Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                response = self.send_message(user_input)
                print(f"Assistant: {response}\n")
                
            except KeyboardInterrupt:
                self.logger.info("Conversation interrupted by user")
                print("\nGoodbye!")
                break
            except Exception as e:
                self.logger.error(f"Error during conversation: {e}")
                print(f"Error: {e}")
                continue