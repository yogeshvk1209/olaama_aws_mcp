#!/usr/bin/env python3
"""Logging utilities for Ollama CLI and AWS MCP server scripts."""

import os
import logging
from pathlib import Path
from typing import Optional


def setup_logging(log_file_path: str, script_name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Set up logging configuration for a script.
    
    Args:
        log_file_path: Path to the log file
        script_name: Name of the script for logger identification
        level: Logging level (default: INFO)
    
    Returns:
        Configured logger instance
    """
    # Ensure log directory exists
    log_dir = Path(log_file_path).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(script_name)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create file handler
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(level)
    
    # Create console handler for immediate feedback
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Set formatter for handlers
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def setup_ollama_logging(log_file_path: str) -> logging.Logger:
    """Set up logging specifically for Ollama CLI script."""
    return setup_logging(log_file_path, "ollama-cli")


def setup_mcp_logging(log_file_path: str) -> logging.Logger:
    """Set up logging specifically for AWS MCP server script."""
    return setup_logging(log_file_path, "aws-mcp-server")