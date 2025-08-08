#!/usr/bin/env python3
"""Enhanced Ollama CLI client with AWS MCP integration."""

import sys
import signal
from src.config import OllamaConfig, create_ollama_parser
from src.config_utils import validate_ollama_config, display_config_summary
from src.logging_utils import setup_ollama_logging
from src.enhanced_ollama_client import EnhancedOllamaClient
from src.enhanced_cli_interface import EnhancedCLI


def setup_signal_handlers(client: EnhancedOllamaClient, logger):
    """Set up signal handlers for graceful shutdown."""
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, initiating graceful shutdown")
        print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
        
        # Cleanup MCP resources
        if client:
            client.cleanup()
        
        print("👋 Goodbye!")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def validate_and_display_config(config: OllamaConfig, logger) -> bool:
    """
    Validate configuration and display any issues.
    
    Args:
        config: Configuration to validate
        logger: Logger instance
        
    Returns:
        True if configuration is valid, False otherwise
    """
    errors = validate_ollama_config(config)
    
    if errors:
        logger.error("Configuration validation failed")
        print("❌ Configuration Error:")
        for error in errors:
            print(f"   • {error}")
        print("\nPlease fix the configuration issues and try again.")
        return False
    
    logger.info("Configuration validation passed")
    return True


def display_startup_banner(config: OllamaConfig):
    """Display startup banner with configuration info."""
    print("🚀 Enhanced Ollama CLI with AWS MCP Integration")
    print("=" * 60)
    print(f"Version: 2.0.0")
    print(f"Model: {config.model}")
    print(f"Ollama URL: {config.ollama_url}")
    
    if config.mcp_config.enabled:
        print(f"MCP Integration: ✅ Enabled")
        print(f"AWS Detection Threshold: {config.mcp_config.aws_detection_threshold}")
    else:
        print(f"MCP Integration: ❌ Disabled")
    
    print("=" * 60)
    print()


def main():
    """Main entry point for Enhanced Ollama CLI with MCP integration."""
    try:
        # Parse command line arguments
        parser = create_ollama_parser()
        args = parser.parse_args()
        
        # Load configuration from environment and arguments
        config = OllamaConfig.from_env_and_args(args)
        
        # Set up logging
        logger = setup_ollama_logging(config.log_file)
        
        logger.info("=" * 60)
        logger.info("Enhanced Ollama CLI with MCP Integration starting")
        logger.info("=" * 60)
        logger.info(f"Model: {config.model}")
        logger.info(f"Ollama URL: {config.ollama_url}")
        logger.info(f"Log file: {config.log_file}")
        logger.info(f"MCP enabled: {config.mcp_config.enabled}")
        
        if config.mcp_config.enabled:
            logger.info(f"AWS detection threshold: {config.mcp_config.aws_detection_threshold}")
            logger.info(f"Max documentation entries: {config.mcp_config.max_documentation_entries}")
            logger.info(f"Connection timeout: {config.mcp_config.connection_timeout}s")
            logger.info(f"Fallback on error: {config.mcp_config.fallback_on_error}")
            logger.info(f"Auto-start server: {config.mcp_config.auto_start_server}")
        
        # Validate configuration
        if not validate_and_display_config(config, logger):
            sys.exit(1)
        
        # Display startup banner
        display_startup_banner(config)
        
        # Create enhanced Ollama client with MCP integration
        logger.info("Initializing enhanced Ollama client with MCP integration")
        client = EnhancedOllamaClient(
            base_url=config.ollama_url,
            model=config.model,
            logger=logger,
            mcp_enabled=config.mcp_config.enabled,
            aws_detection_threshold=config.mcp_config.aws_detection_threshold,
            auto_start_mcp=config.mcp_config.start_mcp_immediately
        )
        
        # Configure MCP settings
        if config.mcp_config.enabled:
            # Update context enhancer settings if available
            if client.context_enhancer:
                client.context_enhancer.max_context_length = 2000
                client.context_enhancer.max_docs_per_query = config.mcp_config.max_documentation_entries
            
            logger.info("MCP integration configured successfully")
        
        # Set up signal handlers for graceful shutdown
        setup_signal_handlers(client, logger)
        
        # Create enhanced CLI interface
        logger.info("Initializing enhanced CLI interface")
        cli = EnhancedCLI(client, config, logger)
        
        # Start the enhanced CLI session
        logger.info("Starting enhanced CLI session")
        cli.run()
        
    except KeyboardInterrupt:
        print("\n👋 Session interrupted. Goodbye!")
        sys.exit(0)
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        if 'logger' in locals():
            logger.error(f"Fatal error in main: {e}")
            import traceback
            logger.error(traceback.format_exc())
        sys.exit(1)
    
    finally:
        if 'client' in locals():
            client.cleanup()
        if 'logger' in locals():
            logger.info("Enhanced Ollama CLI session ended")
            logger.info("=" * 60)


if __name__ == "__main__":
    main()