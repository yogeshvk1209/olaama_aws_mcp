#!/usr/bin/env python3
"""Configuration management for Ollama CLI and AWS MCP server scripts."""

import os
import argparse
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path


@dataclass
class MCPIntegrationConfig:
    """Configuration for MCP integration."""
    enabled: bool = True
    aws_detection_threshold: float = 0.4
    max_documentation_entries: int = 3
    connection_timeout: int = 10
    fallback_on_error: bool = True
    auto_start_server: bool = True
    start_mcp_immediately: bool = False

    @classmethod
    def from_env_and_args(cls, args: Optional[argparse.Namespace] = None) -> 'MCPIntegrationConfig':
        """Create MCP configuration from environment variables and command line arguments."""
        config = cls()
        
        # Environment variables
        config.enabled = os.getenv('MCP_INTEGRATION_ENABLED', 'true').lower() == 'true'
        config.aws_detection_threshold = float(os.getenv('AWS_DETECTION_THRESHOLD', str(config.aws_detection_threshold)))
        config.max_documentation_entries = int(os.getenv('MAX_DOCUMENTATION_ENTRIES', str(config.max_documentation_entries)))
        config.connection_timeout = int(os.getenv('MCP_CONNECTION_TIMEOUT', str(config.connection_timeout)))
        config.fallback_on_error = os.getenv('MCP_FALLBACK_ON_ERROR', 'true').lower() == 'true'
        config.auto_start_server = os.getenv('MCP_AUTO_START_SERVER', 'true').lower() == 'true'
        config.start_mcp_immediately = os.getenv('MCP_START_IMMEDIATELY', 'false').lower() == 'true'
        
        # Command line arguments override environment variables
        if args:
            if hasattr(args, 'mcp_enabled') and args.mcp_enabled is not None:
                config.enabled = args.mcp_enabled
            if hasattr(args, 'aws_threshold') and args.aws_threshold is not None:
                config.aws_detection_threshold = args.aws_threshold
            if hasattr(args, 'max_docs') and args.max_docs is not None:
                config.max_documentation_entries = args.max_docs
            if hasattr(args, 'connection_timeout') and args.connection_timeout is not None:
                config.connection_timeout = args.connection_timeout
            if hasattr(args, 'no_fallback') and args.no_fallback:
                config.fallback_on_error = False
            if hasattr(args, 'no_auto_start') and args.no_auto_start:
                config.auto_start_server = False
            if hasattr(args, 'start_mcp_now') and args.start_mcp_now:
                config.start_mcp_immediately = True
                
        return config


@dataclass
class OllamaConfig:
    """Configuration for Ollama CLI client."""
    model: str = "qwen3:14b"
    log_file: str = "/var/log/custom-aws-mcp/ollama-cli.log"
    ollama_url: str = "http://localhost:11434"
    mcp_config: MCPIntegrationConfig = None

    def __post_init__(self):
        if self.mcp_config is None:
            self.mcp_config = MCPIntegrationConfig()

    @classmethod
    def from_env_and_args(cls, args: Optional[argparse.Namespace] = None) -> 'OllamaConfig':
        """Create configuration from environment variables and command line arguments."""
        config = cls()
        
        # Environment variables
        config.model = os.getenv('OLLAMA_MODEL', config.model)
        config.ollama_url = os.getenv('OLLAMA_URL', config.ollama_url)
        
        # Handle log file path - check for central log directory first
        log_dir = os.getenv('LOG_DIR', '/var/log/custom-aws-mcp')
        default_log_file = str(Path(log_dir) / 'ollama-cli.log')
        config.log_file = os.getenv('OLLAMA_LOG_FILE', default_log_file)
        
        # Load MCP configuration
        config.mcp_config = MCPIntegrationConfig.from_env_and_args(args)
        
        # Command line arguments override environment variables
        if args:
            if hasattr(args, 'model') and args.model:
                config.model = args.model
            if hasattr(args, 'log_dir') and args.log_dir:
                config.log_file = str(Path(args.log_dir) / 'ollama-cli.log')
            elif hasattr(args, 'log_file') and args.log_file:
                config.log_file = args.log_file
            if hasattr(args, 'ollama_url') and args.ollama_url:
                config.ollama_url = args.ollama_url
                
        return config


@dataclass
class MCPConfig:
    """Configuration for AWS MCP server launcher."""
    log_file: str = "/var/log/custom-aws-mcp/aws-mcp-server.log"
    command: str = "npx"
    args: List[str] = None
    working_directory: Optional[str] = None

    def __post_init__(self):
        if self.args is None:
            self.args = ["mcp-remote", "https://knowledge-mcp.global.api.aws"]

    @classmethod
    def from_env_and_args(cls, args: Optional[argparse.Namespace] = None) -> 'MCPConfig':
        """Create configuration from environment variables and command line arguments."""
        config = cls()
        
        # Environment variables
        config.command = os.getenv('MCP_COMMAND', config.command)
        config.working_directory = os.getenv('MCP_WORKING_DIR', config.working_directory)
        
        # Handle log file path - check for central log directory first
        log_dir = os.getenv('LOG_DIR', '/var/log/custom-aws-mcp')
        default_log_file = str(Path(log_dir) / 'aws-mcp-server.log')
        config.log_file = os.getenv('MCP_LOG_FILE', default_log_file)
        
        # Command line arguments override environment variables
        if args:
            if hasattr(args, 'log_dir') and args.log_dir:
                config.log_file = str(Path(args.log_dir) / 'aws-mcp-server.log')
            elif hasattr(args, 'log_file') and args.log_file:
                config.log_file = args.log_file
            if hasattr(args, 'command') and args.command:
                config.command = args.command
            if hasattr(args, 'working_dir') and args.working_dir:
                config.working_directory = args.working_dir
                
        return config


def create_ollama_parser() -> argparse.ArgumentParser:
    """Create argument parser for Ollama CLI script."""
    parser = argparse.ArgumentParser(
        description='Ollama CLI client with AWS MCP integration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment Variables:
  LOG_DIR                    Central log directory (default: /var/log/custom-aws-mcp)
  OLLAMA_MODEL              Ollama model to use (default: qwen3:14b)
  OLLAMA_LOG_FILE           Full log file path (overrides LOG_DIR)
  OLLAMA_URL                Ollama server URL (default: http://localhost:11434)
  
  MCP Integration:
  MCP_INTEGRATION_ENABLED   Enable MCP integration (default: true)
  AWS_DETECTION_THRESHOLD   AWS detection threshold (default: 0.4)
  MAX_DOCUMENTATION_ENTRIES Max docs per query (default: 3)
  MCP_CONNECTION_TIMEOUT    Connection timeout in seconds (default: 10)
  MCP_FALLBACK_ON_ERROR     Fallback on MCP errors (default: true)
  MCP_AUTO_START_SERVER     Auto-start MCP server (default: true)
  MCP_START_IMMEDIATELY     Start MCP server at startup (default: false)

Examples:
  %(prog)s                                    # Use defaults with MCP
  %(prog)s --model llama2:7b                  # Use specific model
  %(prog)s --no-mcp                           # Disable MCP integration
  %(prog)s --aws-threshold 0.6                # Higher AWS detection threshold
  %(prog)s --start-mcp-now                    # Start MCP server immediately (shows connected)
  %(prog)s --log-dir ./logs                   # Custom log directory
  MCP_INTEGRATION_ENABLED=false %(prog)s      # Disable via environment
        """
    )
    
    # Basic Ollama options
    parser.add_argument(
        '--model', 
        help='Ollama model to use (default: qwen3:14b, env: OLLAMA_MODEL)'
    )
    parser.add_argument(
        '--log-dir', 
        help='Log directory path - will create ollama-cli.log inside (env: LOG_DIR)'
    )
    parser.add_argument(
        '--log-file', 
        help='Full log file path (overrides --log-dir, env: OLLAMA_LOG_FILE)'
    )
    parser.add_argument(
        '--ollama-url', 
        help='Ollama server URL (default: http://localhost:11434, env: OLLAMA_URL)'
    )
    
    # MCP Integration options
    mcp_group = parser.add_argument_group('MCP Integration Options')
    mcp_group.add_argument(
        '--mcp-enabled', 
        action='store_true',
        help='Enable MCP integration (default: enabled, env: MCP_INTEGRATION_ENABLED)'
    )
    mcp_group.add_argument(
        '--no-mcp', 
        dest='mcp_enabled',
        action='store_false',
        help='Disable MCP integration'
    )
    mcp_group.add_argument(
        '--aws-threshold', 
        type=float,
        help='AWS detection threshold 0.0-1.0 (default: 0.4, env: AWS_DETECTION_THRESHOLD)'
    )
    mcp_group.add_argument(
        '--max-docs', 
        type=int,
        help='Maximum documentation entries per query (default: 3, env: MAX_DOCUMENTATION_ENTRIES)'
    )
    mcp_group.add_argument(
        '--connection-timeout', 
        type=int,
        help='MCP connection timeout in seconds (default: 10, env: MCP_CONNECTION_TIMEOUT)'
    )
    mcp_group.add_argument(
        '--no-fallback', 
        action='store_true',
        help='Disable fallback on MCP errors (default: fallback enabled)'
    )
    mcp_group.add_argument(
        '--no-auto-start', 
        action='store_true',
        help='Disable auto-start of MCP server (default: auto-start enabled)'
    )
    mcp_group.add_argument(
        '--start-mcp-now', 
        action='store_true',
        help='Start MCP server immediately during initialization (shows connected status)'
    )
    
    parser.add_argument(
        '--version', 
        action='version', 
        version='Ollama CLI with MCP Integration 2.0.0'
    )
    
    # Set default for mcp_enabled to None so we can detect if it was explicitly set
    parser.set_defaults(mcp_enabled=None)
    
    return parser


def create_mcp_parser() -> argparse.ArgumentParser:
    """Create argument parser for AWS MCP server script."""
    parser = argparse.ArgumentParser(
        description='AWS Knowledge MCP server launcher with logging',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment Variables:
  LOG_DIR           Central log directory (default: /var/log/custom-aws-mcp)
  MCP_LOG_FILE      Full log file path (overrides LOG_DIR)
  MCP_COMMAND       Command to run (default: npx)
  MCP_WORKING_DIR   Working directory for the process

Examples:
  %(prog)s                                    # Use defaults
  %(prog)s --log-dir ./logs                   # Logs to ./logs/aws-mcp-server.log
  %(prog)s --log-file ./custom.log            # Custom full log path
  %(prog)s --working-dir /tmp                 # Custom working directory
  LOG_DIR=./logs %(prog)s                     # Use environment variable
        """
    )
    parser.add_argument(
        '--log-dir', 
        help='Log directory path - will create aws-mcp-server.log inside (env: LOG_DIR)'
    )
    parser.add_argument(
        '--log-file', 
        help='Full log file path (overrides --log-dir, env: MCP_LOG_FILE)'
    )
    parser.add_argument(
        '--command', 
        help='Command to run (default: npx, env: MCP_COMMAND)'
    )
    parser.add_argument(
        '--working-dir', 
        help='Working directory for the process (env: MCP_WORKING_DIR)'
    )
    parser.add_argument(
        '--version', 
        action='version', 
        version='AWS MCP Server Launcher 1.0.0'
    )
    return parser