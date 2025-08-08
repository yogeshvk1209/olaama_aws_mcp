#!/usr/bin/env python3
"""MCP server management for AWS Knowledge MCP server."""

import subprocess
import logging
import threading
import os
from typing import Optional, List
from config import MCPConfig


class MCPServerManager:
    """Manager for AWS Knowledge MCP server process."""
    
    def __init__(self, config: MCPConfig, logger: Optional[logging.Logger] = None):
        """
        Initialize MCP server manager.
        
        Args:
            config: MCPConfig instance with server configuration
            logger: Logger instance for logging server activity
        """
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.process = None
        self.log_file_handle = None
    
    def setup_logging(self) -> None:
        """Set up log file for server output redirection."""
        # Ensure log directory exists
        log_dir = os.path.dirname(self.config.log_file)
        os.makedirs(log_dir, exist_ok=True)
        
        # Open log file for writing
        self.log_file_handle = open(self.config.log_file, 'a', encoding='utf-8')
        self.logger.info(f"Server output will be logged to: {self.config.log_file}")
    
    def start_server(self) -> None:
        """
        Start the AWS Knowledge MCP server process.
        """
        self.logger.info("Starting AWS Knowledge MCP server")
        self.logger.info(f"Command: {self.config.command} {' '.join(self.config.args)}")
        
        # Set up logging
        self.setup_logging()
        
        # Start the process
        self.process = subprocess.Popen(
            [self.config.command] + self.config.args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            cwd=self.config.working_directory
        )
        
        self.logger.info(f"MCP server started with PID: {self.process.pid}")
        
        # Start output monitoring in a separate thread
        self._start_output_monitoring()
        
        # Wait for process to complete
        self._wait_for_completion()
    
    def _start_output_monitoring(self) -> None:
        """Start monitoring server output in a separate thread."""
        def monitor_output():
            """Monitor and log server output."""
            if self.process and self.process.stdout:
                for line in iter(self.process.stdout.readline, ''):
                    if line:
                        # Write to log file
                        if self.log_file_handle:
                            self.log_file_handle.write(line)
                            self.log_file_handle.flush()
                        
                        # Log through logger as well
                        self.logger.info(f"MCP Server: {line.strip()}")
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=monitor_output, daemon=True)
        monitor_thread.start()
        self.logger.info("Started output monitoring thread")
    
    def _wait_for_completion(self) -> None:
        """Wait for the server process to complete."""
        try:
            # Wait for process to complete
            return_code = self.process.wait()
            self.logger.info(f"MCP server process completed with return code: {return_code}")
            
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal, stopping MCP server")
            self.stop_server()
            
        finally:
            self._cleanup()
    
    def stop_server(self) -> None:
        """Stop the MCP server process."""
        if self.process:
            self.logger.info("Stopping MCP server process")
            self.process.terminate()
            
            # Wait a bit for graceful shutdown
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.logger.warning("Process didn't terminate gracefully, killing it")
                self.process.kill()
                self.process.wait()
            
            self.logger.info("MCP server process stopped")
    
    def _cleanup(self) -> None:
        """Clean up resources."""
        if self.log_file_handle:
            self.log_file_handle.close()
            self.log_file_handle = None
        
        self.process = None
        self.logger.info("Cleanup completed")
    
    def is_running(self) -> bool:
        """
        Check if the MCP server process is running.
        
        Returns:
            True if process is running, False otherwise
        """
        return self.process is not None and self.process.poll() is None