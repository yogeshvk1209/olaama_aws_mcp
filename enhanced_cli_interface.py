#!/usr/bin/env python3
"""Enhanced CLI interface with MCP integration support."""

import logging
from typing import Optional, Dict, Any
from enhanced_ollama_client import EnhancedOllamaClient, EnhancedResponse
from config import OllamaConfig
from config_utils import display_config_summary, validate_ollama_config


class EnhancedCLI:
    """Enhanced command-line interface with MCP integration."""
    
    def __init__(self, client: EnhancedOllamaClient, config: OllamaConfig, 
                 logger: Optional[logging.Logger] = None):
        """
        Initialize enhanced CLI interface.
        
        Args:
            client: EnhancedOllamaClient instance for LLM communication
            config: Configuration object
            logger: Logger instance for logging user interactions
        """
        self.client = client
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        # CLI commands
        self.commands = {
            'help': self.show_help,
            'status': self.show_status,
            'config': self.show_config,
            'stats': self.show_stats,
            'mcp': self.mcp_commands,
            'quit': self.quit_session,
            'exit': self.quit_session,
            'q': self.quit_session,
        }
    
    def run(self) -> None:
        """
        Run the interactive CLI session with MCP integration.
        """
        self.logger.info("Starting enhanced CLI session with MCP integration")
        self.display_welcome()
        self.interactive_session()
        self.logger.info("Enhanced CLI session ended")
    
    def display_welcome(self) -> None:
        """Display enhanced welcome message with MCP status."""
        print("=" * 70)
        print("🤖 Enhanced Ollama CLI with AWS MCP Integration")
        print("=" * 70)
        
        # Basic connection info
        print(f"🔗 Connected to: {self.client.base_url}")
        print(f"🧠 Using model: {self.client.model}")
        print(f"📝 Logging to: {self.config.log_file}")
        
        # MCP status
        mcp_status = self.client.get_mcp_status()
        if mcp_status['mcp_enabled']:
            print(f"🔍 AWS MCP Integration: ✅ Enabled")
            print(f"   Detection threshold: {mcp_status['aws_detection_threshold']}")
            server_status = "🟢 Connected" if mcp_status['mcp_server_connected'] else "🔴 Disconnected"
            print(f"   MCP Server: {server_status}")
        else:
            print(f"🔍 AWS MCP Integration: ❌ Disabled")
        
        print("\n📋 Available Commands:")
        print("  • Type your question to chat with the AI")
        print("  • 'help' - Show detailed help and commands")
        print("  • 'status' - Show current system status")
        print("  • 'config' - Show configuration details")
        print("  • 'stats' - Show session statistics")
        print("  • 'mcp <command>' - MCP-specific commands")
        print("  • 'quit', 'exit', or 'q' - End session")
        print("=" * 70)
        print()
    
    def interactive_session(self) -> None:
        """Run the interactive session loop."""
        while True:
            try:
                user_input = input("🤖 You: ").strip()
                
                if not user_input:
                    continue
                
                # Check if it's a command
                if self.handle_command(user_input):
                    continue
                
                # Process as regular query
                self.process_query(user_input)
                
            except KeyboardInterrupt:
                self.logger.info("Session interrupted by user")
                print("\n👋 Session interrupted. Goodbye!")
                break
            except EOFError:
                self.logger.info("Session ended by EOF")
                print("\n👋 Session ended. Goodbye!")
                break
            except Exception as e:
                self.logger.error(f"Error during session: {e}")
                print(f"❌ Error: {e}")
                continue
    
    def handle_command(self, user_input: str) -> bool:
        """
        Handle CLI commands.
        
        Args:
            user_input: User input to check for commands
            
        Returns:
            True if input was handled as a command, False otherwise
        """
        # Split input into command and arguments
        parts = user_input.lower().split()
        if not parts:
            return False
        
        command = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        if command in self.commands:
            try:
                if command == 'mcp':
                    self.commands[command](args)
                elif command in ['quit', 'exit', 'q']:
                    self.commands[command]()
                    return True  # Signal to exit
                else:
                    self.commands[command]()
                return True
            except Exception as e:
                print(f"❌ Error executing command '{command}': {e}")
                return True
        
        return False
    
    def process_query(self, query: str) -> None:
        """
        Process a user query with MCP integration.
        
        Args:
            query: User query to process
        """
        print()  # Add spacing
        
        # Send query with MCP integration
        enhanced_response = self.client.send_message_with_mcp(query)
        
        # Display the enhanced response
        self.display_enhanced_response(enhanced_response)
    
    def display_enhanced_response(self, response: EnhancedResponse) -> None:
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
                    # Show first few sources
                    for i, source in enumerate(response.enhanced_context.sources[:2]):
                        print(f"   • {source}")
                    if len(response.enhanced_context.sources) > 2:
                        print(f"   • ... and {len(response.enhanced_context.sources) - 2} more")
        elif response.aws_detection.is_aws_related:
            if response.fallback_reason:
                print(f"⚠️  AWS query detected but using fallback: {response.fallback_reason}")
            else:
                print("ℹ️  AWS query detected but MCP enhancement not used")
                print(f"   Confidence: {response.aws_detection.confidence_score:.2f}")
        
        # Show the LLM response
        print(f"\n🤖 Assistant: {response.llm_response}")
        
        # Show processing time and confidence
        if response.mcp_used and response.enhanced_context:
            print(f"\n⏱️  Response time: {response.processing_time:.2f}s "
                  f"(enhancement confidence: {response.enhanced_context.confidence_score:.2f})")
        else:
            print(f"\n⏱️  Response time: {response.processing_time:.2f}s")
        
        print("-" * 50)
    
    def show_help(self) -> None:
        """Show detailed help information."""
        print("\n📖 Enhanced Ollama CLI Help")
        print("=" * 50)
        print("This CLI provides an enhanced chat experience with AWS MCP integration.")
        print("\n🔧 Available Commands:")
        print("  help     - Show this help message")
        print("  status   - Show current system and MCP status")
        print("  config   - Show current configuration")
        print("  stats    - Show session statistics")
        print("  mcp      - MCP-specific commands:")
        print("    mcp status    - Show MCP server status")
        print("    mcp enable    - Enable MCP integration")
        print("    mcp disable   - Disable MCP integration")
        print("    mcp restart   - Restart MCP server")
        print("    mcp test      - Test MCP connection")
        print("  quit/exit/q - End the session")
        
        print("\n🔍 AWS Query Detection:")
        print("  The system automatically detects AWS-related queries and enhances")
        print("  them with official AWS documentation when MCP is enabled.")
        
        print(f"\n⚙️  Current Settings:")
        print(f"  MCP Enabled: {'✅' if self.config.mcp_config.enabled else '❌'}")
        print(f"  AWS Detection Threshold: {self.config.mcp_config.aws_detection_threshold}")
        print(f"  Max Documentation Entries: {self.config.mcp_config.max_documentation_entries}")
        
        print("\n💡 Tips:")
        print("  • Ask AWS-specific questions to see MCP enhancement in action")
        print("  • Use 'status' to check if MCP server is running")
        print("  • Use 'stats' to see your session statistics")
        print("=" * 50)
    
    def show_status(self) -> None:
        """Show current system status."""
        print("\n📊 System Status")
        print("=" * 40)
        
        # Ollama status
        print("🤖 Ollama Client:")
        print(f"   Model: {self.client.model}")
        print(f"   URL: {self.client.base_url}")
        
        # MCP status
        mcp_status = self.client.get_mcp_status()
        print("\n🔍 MCP Integration:")
        print(f"   Enabled: {'✅ Yes' if mcp_status['mcp_enabled'] else '❌ No'}")
        
        if mcp_status['mcp_enabled']:
            print(f"   AWS Detection Threshold: {mcp_status['aws_detection_threshold']}")
            print(f"   Server Connected: {'✅ Yes' if mcp_status['mcp_server_connected'] else '❌ No'}")
            
            if 'mcp_server_info' in mcp_status and mcp_status['mcp_server_info']:
                server_info = mcp_status['mcp_server_info']
                if 'pid' in server_info and server_info['pid']:
                    print(f"   Server PID: {server_info['pid']}")
        
        # Session statistics
        stats = mcp_status.get('statistics', {})
        if stats.get('total_queries', 0) > 0:
            print(f"\n📈 Session Statistics:")
            print(f"   Total Queries: {stats['total_queries']}")
            print(f"   AWS Queries: {stats['aws_queries_detected']}")
            print(f"   MCP Enhanced: {stats['mcp_queries_successful']}")
            print(f"   Fallbacks: {stats['fallback_queries']}")
        
        print("=" * 40)
    
    def show_config(self) -> None:
        """Show current configuration."""
        print("\n🔧 Current Configuration")
        print("=" * 50)
        display_config_summary(self.config)
        
        # Validate configuration
        errors = validate_ollama_config(self.config)
        if errors:
            print("⚠️  Configuration Issues:")
            for error in errors:
                print(f"   • {error}")
        else:
            print("✅ Configuration is valid")
        print()
    
    def show_stats(self) -> None:
        """Show detailed session statistics."""
        mcp_status = self.client.get_mcp_status()
        stats = mcp_status.get('statistics', {})
        
        print("\n📊 Detailed Session Statistics")
        print("=" * 45)
        
        total = stats.get('total_queries', 0)
        aws_detected = stats.get('aws_queries_detected', 0)
        mcp_successful = stats.get('mcp_queries_successful', 0)
        mcp_failed = stats.get('mcp_queries_failed', 0)
        fallbacks = stats.get('fallback_queries', 0)
        
        print(f"Total Queries: {total}")
        print(f"AWS Queries Detected: {aws_detected}")
        print(f"MCP Enhancements Successful: {mcp_successful}")
        print(f"MCP Enhancements Failed: {mcp_failed}")
        print(f"Fallback Queries: {fallbacks}")
        
        if total > 0:
            aws_rate = (aws_detected / total) * 100
            print(f"\nAWS Detection Rate: {aws_rate:.1f}%")
            
            if aws_detected > 0:
                success_rate = (mcp_successful / aws_detected) * 100
                print(f"MCP Success Rate: {success_rate:.1f}%")
        
        print("=" * 45)
    
    def mcp_commands(self, args: list) -> None:
        """
        Handle MCP-specific commands.
        
        Args:
            args: Command arguments
        """
        if not args:
            print("\n🔍 MCP Commands:")
            print("  mcp status   - Show MCP server status")
            print("  mcp enable   - Enable MCP integration")
            print("  mcp disable  - Disable MCP integration")
            print("  mcp restart  - Restart MCP server")
            print("  mcp test     - Test MCP connection")
            return
        
        command = args[0].lower()
        
        if command == 'status':
            self.mcp_status()
        elif command == 'enable':
            self.mcp_enable()
        elif command == 'disable':
            self.mcp_disable()
        elif command == 'restart':
            self.mcp_restart()
        elif command == 'test':
            self.mcp_test()
        else:
            print(f"❌ Unknown MCP command: {command}")
            print("Use 'mcp' without arguments to see available commands.")
    
    def mcp_status(self) -> None:
        """Show detailed MCP status."""
        print("\n🔍 MCP Server Status")
        print("=" * 30)
        
        if not self.client.mcp_manager:
            print("❌ MCP integration is disabled")
            return
        
        # Test connection
        connection_result = self.client.mcp_manager.test_connection()
        
        print(f"Script Path: {connection_result['server_script']}")
        print(f"Script Exists: {'✅' if connection_result['script_exists'] else '❌'}")
        print(f"Server Connected: {'✅' if connection_result['connected'] else '❌'}")
        
        if connection_result['error']:
            print(f"Error: {connection_result['error']}")
        
        if connection_result['server_info']:
            info = connection_result['server_info']
            if 'pid' in info and info['pid']:
                print(f"Server PID: {info['pid']}")
        
        print("=" * 30)
    
    def mcp_enable(self) -> None:
        """Enable MCP integration."""
        self.client.configure_mcp(enabled=True)
        self.config.mcp_config.enabled = True
        print("✅ MCP integration enabled")
    
    def mcp_disable(self) -> None:
        """Disable MCP integration."""
        self.client.configure_mcp(enabled=False)
        self.config.mcp_config.enabled = False
        print("❌ MCP integration disabled")
    
    def mcp_restart(self) -> None:
        """Restart MCP server."""
        if not self.client.mcp_manager:
            print("❌ MCP integration is disabled")
            return
        
        print("🔄 Restarting MCP server...")
        
        # Disconnect current server
        self.client.mcp_manager.disconnect()
        
        # Start new server
        success = self.client.mcp_manager.start_server_if_needed()
        
        if success:
            print("✅ MCP server restarted successfully")
        else:
            print("❌ Failed to restart MCP server")
    
    def mcp_test(self) -> None:
        """Test MCP connection and functionality."""
        if not self.client.mcp_manager:
            print("❌ MCP integration is disabled")
            return
        
        print("🧪 Testing MCP connection...")
        
        # Test connection
        connection_result = self.client.mcp_manager.test_connection()
        
        if connection_result['connected']:
            print("✅ MCP server connection successful")
            
            # Test documentation query
            print("🧪 Testing documentation query...")
            response = self.client.mcp_manager.query_documentation("S3 bucket test", ["s3"])
            
            if response.success:
                print(f"✅ Documentation query successful ({response.query_time:.2f}s)")
                print(f"   Retrieved {len(response.documentation)} entries")
            else:
                print(f"❌ Documentation query failed: {response.error_message}")
        else:
            print(f"❌ MCP server connection failed: {connection_result['error']}")
    
    def quit_session(self) -> None:
        """Handle session quit."""
        print("\n📊 Final Session Statistics:")
        self.show_stats()
        
        # Cleanup
        self.client.cleanup()
        
        print("\n👋 Thank you for using Enhanced Ollama CLI with MCP Integration!")
        print("Goodbye!")
        
        # This will be caught by the main loop to exit
        raise KeyboardInterrupt()