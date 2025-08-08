#!/usr/bin/env python3
"""Configuration utilities for MCP integration."""

import os
from typing import Dict, Any, List
from config import OllamaConfig, MCPConfig, MCPIntegrationConfig


def validate_mcp_config(mcp_config: MCPIntegrationConfig) -> List[str]:
    """
    Validate MCP integration configuration.
    
    Args:
        mcp_config: MCP configuration to validate
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    # Validate AWS detection threshold
    if not 0.0 <= mcp_config.aws_detection_threshold <= 1.0:
        errors.append(f"AWS detection threshold must be between 0.0 and 1.0, got {mcp_config.aws_detection_threshold}")
    
    # Validate max documentation entries
    if mcp_config.max_documentation_entries < 1 or mcp_config.max_documentation_entries > 10:
        errors.append(f"Max documentation entries must be between 1 and 10, got {mcp_config.max_documentation_entries}")
    
    # Validate connection timeout
    if mcp_config.connection_timeout < 1 or mcp_config.connection_timeout > 60:
        errors.append(f"Connection timeout must be between 1 and 60 seconds, got {mcp_config.connection_timeout}")
    
    return errors


def validate_ollama_config(config: OllamaConfig) -> List[str]:
    """
    Validate complete Ollama configuration.
    
    Args:
        config: Ollama configuration to validate
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    # Validate basic Ollama settings
    if not config.model or not config.model.strip():
        errors.append("Ollama model cannot be empty")
    
    if not config.ollama_url or not config.ollama_url.strip():
        errors.append("Ollama URL cannot be empty")
    
    if not config.ollama_url.startswith(('http://', 'https://')):
        errors.append(f"Ollama URL must start with http:// or https://, got {config.ollama_url}")
    
    # Validate log file path
    if not config.log_file or not config.log_file.strip():
        errors.append("Log file path cannot be empty")
    
    # Validate MCP configuration
    if config.mcp_config:
        mcp_errors = validate_mcp_config(config.mcp_config)
        errors.extend(mcp_errors)
    
    return errors


def display_config_summary(config: OllamaConfig) -> None:
    """
    Display a summary of the current configuration.
    
    Args:
        config: Configuration to display
    """
    print("🔧 Configuration Summary")
    print("=" * 50)
    
    # Basic Ollama settings
    print("Ollama Settings:")
    print(f"  Model: {config.model}")
    print(f"  URL: {config.ollama_url}")
    print(f"  Log File: {config.log_file}")
    print()
    
    # MCP Integration settings
    if config.mcp_config:
        mcp = config.mcp_config
        print("MCP Integration:")
        print(f"  Enabled: {'✅ Yes' if mcp.enabled else '❌ No'}")
        
        if mcp.enabled:
            print(f"  AWS Detection Threshold: {mcp.aws_detection_threshold}")
            print(f"  Max Documentation Entries: {mcp.max_documentation_entries}")
            print(f"  Connection Timeout: {mcp.connection_timeout}s")
            print(f"  Fallback on Error: {'✅ Yes' if mcp.fallback_on_error else '❌ No'}")
            print(f"  Auto-start Server: {'✅ Yes' if mcp.auto_start_server else '❌ No'}")
    else:
        print("MCP Integration: ❌ Not configured")
    
    print("=" * 50)


def get_config_dict(config: OllamaConfig) -> Dict[str, Any]:
    """
    Convert configuration to dictionary for serialization.
    
    Args:
        config: Configuration to convert
        
    Returns:
        Dictionary representation of configuration
    """
    config_dict = {
        "ollama": {
            "model": config.model,
            "url": config.ollama_url,
            "log_file": config.log_file
        }
    }
    
    if config.mcp_config:
        config_dict["mcp_integration"] = {
            "enabled": config.mcp_config.enabled,
            "aws_detection_threshold": config.mcp_config.aws_detection_threshold,
            "max_documentation_entries": config.mcp_config.max_documentation_entries,
            "connection_timeout": config.mcp_config.connection_timeout,
            "fallback_on_error": config.mcp_config.fallback_on_error,
            "auto_start_server": config.mcp_config.auto_start_server
        }
    
    return config_dict


def create_config_from_dict(config_dict: Dict[str, Any]) -> OllamaConfig:
    """
    Create configuration from dictionary.
    
    Args:
        config_dict: Dictionary with configuration values
        
    Returns:
        OllamaConfig instance
    """
    config = OllamaConfig()
    
    # Load Ollama settings
    if "ollama" in config_dict:
        ollama_settings = config_dict["ollama"]
        config.model = ollama_settings.get("model", config.model)
        config.ollama_url = ollama_settings.get("url", config.ollama_url)
        config.log_file = ollama_settings.get("log_file", config.log_file)
    
    # Load MCP settings
    if "mcp_integration" in config_dict:
        mcp_settings = config_dict["mcp_integration"]
        mcp_config = MCPIntegrationConfig()
        
        mcp_config.enabled = mcp_settings.get("enabled", mcp_config.enabled)
        mcp_config.aws_detection_threshold = mcp_settings.get("aws_detection_threshold", mcp_config.aws_detection_threshold)
        mcp_config.max_documentation_entries = mcp_settings.get("max_documentation_entries", mcp_config.max_documentation_entries)
        mcp_config.connection_timeout = mcp_settings.get("connection_timeout", mcp_config.connection_timeout)
        mcp_config.fallback_on_error = mcp_settings.get("fallback_on_error", mcp_config.fallback_on_error)
        mcp_config.auto_start_server = mcp_settings.get("auto_start_server", mcp_config.auto_start_server)
        
        config.mcp_config = mcp_config
    
    return config


def get_environment_config_info() -> Dict[str, str]:
    """
    Get information about configuration from environment variables.
    
    Returns:
        Dictionary with environment variable information
    """
    env_vars = {
        # Basic Ollama settings
        "OLLAMA_MODEL": os.getenv("OLLAMA_MODEL", "Not set"),
        "OLLAMA_URL": os.getenv("OLLAMA_URL", "Not set"),
        "LOG_DIR": os.getenv("LOG_DIR", "Not set"),
        "OLLAMA_LOG_FILE": os.getenv("OLLAMA_LOG_FILE", "Not set"),
        
        # MCP Integration settings
        "MCP_INTEGRATION_ENABLED": os.getenv("MCP_INTEGRATION_ENABLED", "Not set"),
        "AWS_DETECTION_THRESHOLD": os.getenv("AWS_DETECTION_THRESHOLD", "Not set"),
        "MAX_DOCUMENTATION_ENTRIES": os.getenv("MAX_DOCUMENTATION_ENTRIES", "Not set"),
        "MCP_CONNECTION_TIMEOUT": os.getenv("MCP_CONNECTION_TIMEOUT", "Not set"),
        "MCP_FALLBACK_ON_ERROR": os.getenv("MCP_FALLBACK_ON_ERROR", "Not set"),
        "MCP_AUTO_START_SERVER": os.getenv("MCP_AUTO_START_SERVER", "Not set"),
    }
    
    return env_vars


def display_environment_info() -> None:
    """Display current environment variable configuration."""
    print("🌍 Environment Variables")
    print("=" * 50)
    
    env_info = get_environment_config_info()
    
    print("Basic Settings:")
    for key in ["OLLAMA_MODEL", "OLLAMA_URL", "LOG_DIR", "OLLAMA_LOG_FILE"]:
        value = env_info[key]
        status = "✅" if value != "Not set" else "❌"
        print(f"  {status} {key}: {value}")
    
    print("\nMCP Integration:")
    for key in ["MCP_INTEGRATION_ENABLED", "AWS_DETECTION_THRESHOLD", "MAX_DOCUMENTATION_ENTRIES", 
                "MCP_CONNECTION_TIMEOUT", "MCP_FALLBACK_ON_ERROR", "MCP_AUTO_START_SERVER"]:
        value = env_info[key]
        status = "✅" if value != "Not set" else "❌"
        print(f"  {status} {key}: {value}")
    
    print("=" * 50)


def suggest_optimal_config() -> Dict[str, Any]:
    """
    Suggest optimal configuration based on common use cases.
    
    Returns:
        Dictionary with suggested configuration
    """
    return {
        "description": "Recommended configuration for AWS development",
        "ollama": {
            "model": "qwen3:14b",  # Good balance of capability and speed
            "url": "http://localhost:11434",
            "log_file": "./logs/ollama-cli.log"  # Local logging for development
        },
        "mcp_integration": {
            "enabled": True,
            "aws_detection_threshold": 0.4,  # Balanced sensitivity
            "max_documentation_entries": 3,  # Good context without overwhelming
            "connection_timeout": 10,  # Reasonable timeout
            "fallback_on_error": True,  # Always provide some response
            "auto_start_server": True  # Convenience for development
        }
    }