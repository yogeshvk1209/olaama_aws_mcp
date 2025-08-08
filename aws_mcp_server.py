#!/usr/bin/env python3
"""AWS MCP server launcher with logging."""

import sys
import signal
from config import MCPConfig, create_mcp_parser
from logging_utils import setup_mcp_logging
from mcp_server_manager import MCPServerManager
from server_status import display_server_status


def display_startup_info(config: MCPConfig, logger):
    """Display startup information to user and log."""
    print("=" * 60)
    print("🚀 AWS Knowledge MCP Server Launcher")
    print("=" * 60)
    print(f"Command: {config.command} {' '.join(config.args)}")
    print(f"Log file: {config.log_file}")
    if config.working_directory:
        print(f"Working directory: {config.working_directory}")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    print()


def setup_signal_handlers(server_manager, logger):
    """Set up signal handlers for graceful shutdown."""
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, initiating shutdown")
        print(f"\n🛑 Received signal {signum}, shutting down AWS MCP server...")
        if server_manager and server_manager.is_running():
            server_manager.stop_server()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def main():
    """Main entry point for AWS MCP server launcher."""
    parser = create_mcp_parser()
    args = parser.parse_args()
    
    config = MCPConfig.from_env_and_args(args)
    
    # Set up logging
    logger = setup_mcp_logging(config.log_file)
    
    logger.info("AWS MCP server launcher starting")
    logger.info(f"Command: {config.command} {' '.join(config.args)}")
    logger.info(f"Logging to: {config.log_file}")
    if config.working_directory:
        logger.info(f"Working directory: {config.working_directory}")
    
    # Display startup information
    display_startup_info(config, logger)
    
    server_manager = None
    
    try:
        # Create MCP server manager
        server_manager = MCPServerManager(config, logger)
        
        # Set up signal handlers for graceful shutdown
        setup_signal_handlers(server_manager, logger)
        
        logger.info("Starting MCP server process...")
        print("🚀 Starting AWS Knowledge MCP server...")
        
        # Start the server (this will block until completion)
        server_manager.start_server()
        
        # Display final status
        display_server_status(config, logger)
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down")
        print("\n🛑 Shutting down AWS MCP server...")
        if server_manager:
            server_manager.stop_server()
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    finally:
        logger.info("AWS MCP server launcher finished")
        print("👋 AWS MCP server launcher finished")


if __name__ == "__main__":
    main()