#!/usr/bin/env python3
"""MCP client manager for communicating with AWS Knowledge MCP server."""

import json
import os
import time
import subprocess
import logging
import asyncio
import select
import sys
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class MCPResponse:
    """Response from MCP server query."""
    success: bool
    documentation: List[Dict[str, Any]]
    sources: List[str]
    query_time: float
    error_message: Optional[str] = None


@dataclass
class DocumentationEntry:
    """Single documentation entry from MCP server."""
    title: str
    content: str
    url: str
    service: str
    relevance_score: float = 1.0


class MCPClientManager:
    """Manages communication with AWS Knowledge MCP server via subprocess."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize MCP client manager.
        
        Args:
            logger: Logger instance for logging operations
        """
        self.logger = logger or logging.getLogger(__name__)
        self.connected = False
        self.last_health_check = 0
        self.health_check_interval = 30  # seconds
        
        # MCP server process reference
        self.server_process = None
        self.server_script_path = Path("aws_mcp_server.py")
    
    def connect(self) -> bool:
        """
        Check if MCP server process is running and healthy.
        
        Returns:
            True if server process is running, False otherwise
        """
        try:
            # Check if we have a running process
            if self.server_process and self.server_process.poll() is None:
                self.connected = True
                self.last_health_check = time.time()
                self.logger.debug("MCP server process is running")
                return True
            else:
                self.connected = False
                self.logger.debug("MCP server process is not running")
                return False
                
        except Exception as e:
            self.logger.warning(f"Error checking MCP server status: {e}")
            self.connected = False
            return False
    
    def is_connected(self) -> bool:
        """
        Check if connected to MCP server with periodic health checks.
        
        Returns:
            True if connected and healthy, False otherwise
        """
        current_time = time.time()
        
        # Perform health check if enough time has passed
        if current_time - self.last_health_check > self.health_check_interval:
            self.logger.debug("Performing periodic health check")
            return self.connect()
        
        return self.connected
    
    def _send_mcp_request(self, method: str, params: Dict[str, Any] = None, timeout: float = 10.0) -> Dict[str, Any]:
        """
        Send a JSON-RPC request to the MCP server via stdin/stdout with timeout.
        
        Args:
            method: The MCP method to call
            params: Parameters for the method
            timeout: Timeout in seconds for the request
            
        Returns:
            The response from the MCP server
        """
        if not self.server_process or self.server_process.poll() is not None:
            raise Exception("MCP server process is not running")
        
        # Create JSON-RPC request
        request_id = int(time.time() * 1000)  # Use timestamp as ID
        request = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params or {}
        }
        
        # Send request to server stdin
        request_json = json.dumps(request) + "\n"
        self.logger.debug(f"Sending MCP request: {request_json.strip()}")
        
        try:
            self.server_process.stdin.write(request_json)
            self.server_process.stdin.flush()
            
            # Read response with timeout
            response_line = self._read_with_timeout(timeout)
            self.logger.debug(f"Received MCP response: {response_line}")
            
            if not response_line:
                raise Exception("No response received from MCP server")
            
            response = json.loads(response_line)
            
            # Check for JSON-RPC errors
            if "error" in response:
                error = response["error"]
                error_msg = error.get('message', 'Unknown error')
                error_code = error.get('code', 'Unknown code')
                error_data = error.get('data', {})
                
                self.logger.error(f"MCP server error - Code: {error_code}, Message: {error_msg}")
                if error_data:
                    self.logger.error(f"Error data: {error_data}")
                
                raise Exception(f"MCP server error: {error_msg}")
            
            return response.get("result", {})
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON response from MCP server: {response_line}")
            raise Exception(f"Invalid JSON response from MCP server: {e}")
        except Exception as e:
            self.logger.error(f"MCP communication error: {e}")
            raise

    def _read_with_timeout(self, timeout: float) -> str:
        """
        Read a line from the MCP server stdout with timeout.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            The response line from the server
        """
        if sys.platform == "win32":
            # Windows doesn't support select on pipes, use a simpler approach
            start_time = time.time()
            while time.time() - start_time < timeout:
                if self.server_process.stdout.readable():
                    try:
                        line = self.server_process.stdout.readline()
                        if line:
                            return line.strip()
                    except:
                        pass
                time.sleep(0.1)
            raise Exception(f"Timeout waiting for MCP server response after {timeout}s")
        else:
            # Unix/Linux/macOS - use select for proper timeout
            ready, _, _ = select.select([self.server_process.stdout], [], [], timeout)
            if ready:
                line = self.server_process.stdout.readline()
                return line.strip() if line else ""
            else:
                raise Exception(f"Timeout waiting for MCP server response after {timeout}s")

    def _initialize_mcp_session(self) -> bool:
        """
        Initialize the MCP session with the server.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self.logger.info("Initializing MCP session...")
            
            # Send initialize request with minimal required parameters
            init_params = {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "ollama-mcp-client",
                    "version": "1.0.0"
                }
            }
            
            response = self._send_mcp_request("initialize", init_params, timeout=5.0)
            self.logger.info(f"MCP session initialized successfully: {response}")
            
            # Send initialized notification (no response expected)
            try:
                # For notifications, we don't expect a response, so use a different method
                self._send_mcp_notification("notifications/initialized")
            except Exception as e:
                self.logger.warning(f"Failed to send initialized notification: {e}")
                # Continue anyway as this might not be critical
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize MCP session: {e}")
            return False

    def _send_mcp_notification(self, method: str, params: Dict[str, Any] = None) -> None:
        """
        Send a JSON-RPC notification to the MCP server (no response expected).
        
        Args:
            method: The MCP method to call
            params: Parameters for the method
        """
        if not self.server_process or self.server_process.poll() is not None:
            raise Exception("MCP server process is not running")
        
        # Create JSON-RPC notification (no id field)
        notification = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {}
        }
        
        # Send notification to server stdin
        notification_json = json.dumps(notification) + "\n"
        self.logger.debug(f"Sending MCP notification: {notification_json.strip()}")
        
        try:
            self.server_process.stdin.write(notification_json)
            self.server_process.stdin.flush()
        except Exception as e:
            self.logger.error(f"MCP notification error: {e}")
            raise

    def query_documentation(self, query: str, services: List[str] = None) -> MCPResponse:
        """
        Query the MCP server for AWS documentation.
        
        Args:
            query: The query string to search for
            services: Optional list of AWS services to focus on
            
        Returns:
            MCPResponse with documentation results
        """
        start_time = time.time()
        
        if not self.is_connected():
            # Try to start server if not connected
            if not self.start_server_if_needed():
                return MCPResponse(
                    success=False,
                    documentation=[],
                    sources=[],
                    query_time=time.time() - start_time,
                    error_message="MCP server is not running and could not be started"
                )
        
        try:
            self.logger.info(f"Querying MCP server for: {query}")
            
            # First, list available tools to understand their schemas
            self.logger.info("Listing available MCP tools...")
            tools_response = self._send_mcp_request("tools/list", {})
            tools = tools_response.get("tools", [])
            
            self.logger.info(f"Found {len(tools)} available tools:")
            for tool in tools:
                self.logger.info(f"  - {tool.get('name')}: {tool.get('description', 'No description')}")
                if 'inputSchema' in tool:
                    self.logger.info(f"    Schema: {tool['inputSchema']}")
            
            # Look for search-related tools first
            search_tool = None
            for tool in tools:
                tool_name = tool.get("name", "").lower()
                if any(keyword in tool_name for keyword in ["search", "query", "find"]):
                    search_tool = tool
                    self.logger.info(f"Found search tool: {tool['name']}")
                    break
            
            # If no search tool, look for documentation tools that might work differently
            if not search_tool:
                for tool in tools:
                    tool_name = tool.get("name", "").lower()
                    description = tool.get("description", "").lower()
                    if any(keyword in tool_name or keyword in description for keyword in ["doc", "documentation", "aws"]):
                        search_tool = tool
                        self.logger.info(f"Found documentation tool: {tool['name']}")
                        break
            
            if not search_tool and tools:
                # Use the first available tool as last resort
                search_tool = tools[0]
                self.logger.info(f"Using first available tool as fallback: {search_tool.get('name')}")
            
            if not search_tool:
                raise Exception("No tools available from MCP server")
            
            # Analyze the tool schema to build correct arguments
            tool_name = search_tool["name"]
            input_schema = search_tool.get("inputSchema", {})
            properties = input_schema.get("properties", {})
            required_fields = input_schema.get("required", [])
            
            self.logger.info(f"Tool '{tool_name}' schema - Required: {required_fields}, Properties: {list(properties.keys())}")
            
            # Build arguments based on the actual schema
            arguments = {}
            
            # Handle different tool types
            if "url" in required_fields:
                # This tool requires a URL - try to construct appropriate AWS docs URLs
                aws_docs_urls = self._get_aws_docs_urls(query, services)
                
                # Try each URL until one works
                for url in aws_docs_urls:
                    try:
                        arguments = {"url": url}
                        if "query" in properties:
                            arguments["query"] = query
                        
                        self.logger.info(f"Trying URL: {url}")
                        tool_params = {
                            "name": tool_name,
                            "arguments": arguments
                        }
                        
                        result = self._send_mcp_request("tools/call", tool_params)
                        
                        # If successful, break out of the loop
                        break
                        
                    except Exception as url_error:
                        self.logger.debug(f"URL {url} failed: {url_error}")
                        continue
                else:
                    # If all URLs failed, raise the last error
                    raise Exception(f"All AWS documentation URLs failed for query: {query}")
            elif "query" in properties or "search" in properties:
                # This is a search tool
                arguments["query"] = query
                if services and "services" in properties:
                    arguments["services"] = services
            else:
                # Try to map our query to available parameters
                for prop_name in properties.keys():
                    if prop_name.lower() in ["query", "search", "term", "text"]:
                        arguments[prop_name] = query
                        break
                
                # If no suitable parameter found, use the first required field
                if not arguments and required_fields:
                    arguments[required_fields[0]] = query
            
            self.logger.info(f"Calling tool '{tool_name}' with arguments: {arguments}")
            
            tool_params = {
                "name": tool_name,
                "arguments": arguments
            }
            
            result = self._send_mcp_request("tools/call", tool_params)
            
            # Log the raw result to understand the format
            self.logger.info(f"Raw MCP tool result: {json.dumps(result, indent=2)}")
            
            # Parse the tool result
            documentation = self._parse_tool_result(result, query)
            
            query_time = time.time() - start_time
            sources = [doc.get("url", "") for doc in documentation if doc.get("url")]
            
            self.logger.info(f"Retrieved {len(documentation)} documentation entries in {query_time:.2f}s")
            
            return MCPResponse(
                success=True,
                documentation=documentation,
                sources=sources,
                query_time=query_time
            )
            
        except Exception as e:
            query_time = time.time() - start_time
            error_msg = f"MCP query failed: {e}"
            self.logger.error(error_msg)
            
            return MCPResponse(
                success=False,
                documentation=[],
                sources=[],
                query_time=query_time,
                error_message=error_msg
            )

    def _parse_tool_result(self, result: Dict[str, Any], query: str) -> List[Dict[str, Any]]:
        """
        Parse the tool result from MCP server into documentation format.
        
        Args:
            result: The result from the MCP tool call
            query: The original query for context
            
        Returns:
            List of documentation entries
        """
        documentation = []
        
        try:
            self.logger.debug(f"Parsing tool result: {result}")
            
            # Handle MCP tool response format - check for content array
            content = result.get("content", [])
            
            if isinstance(content, list) and content:
                for i, item in enumerate(content):
                    self.logger.debug(f"Processing content item {i}: {item}")
                    
                    if isinstance(item, dict):
                        # MCP content format: {"type": "text", "text": "content"}
                        if item.get("type") == "text" and "text" in item:
                            text_content = item["text"]
                            doc_entry = {
                                "title": f"AWS Documentation: {query[:50]}",
                                "content": text_content,
                                "url": "https://docs.aws.amazon.com/",
                                "service": self._extract_service_from_content(text_content),
                                "relevance_score": 0.9
                            }
                            documentation.append(doc_entry)
                        
                        # Handle other possible formats
                        elif "text" in item:
                            text_content = item["text"]
                            doc_entry = {
                                "title": f"AWS Documentation: {query[:50]}",
                                "content": text_content,
                                "url": item.get("url", "https://docs.aws.amazon.com/"),
                                "service": self._extract_service_from_content(text_content),
                                "relevance_score": 0.9
                            }
                            documentation.append(doc_entry)
                        
                        # Handle direct content in dict
                        elif "content" in item:
                            text_content = item["content"]
                            doc_entry = {
                                "title": f"AWS Documentation: {query[:50]}",
                                "content": text_content,
                                "url": item.get("url", "https://docs.aws.amazon.com/"),
                                "service": self._extract_service_from_content(text_content),
                                "relevance_score": 0.9
                            }
                            documentation.append(doc_entry)
                    
                    elif isinstance(item, str):
                        # Simple string content
                        doc_entry = {
                            "title": f"AWS Documentation: {query[:50]}",
                            "content": item,
                            "url": "https://docs.aws.amazon.com/",
                            "service": self._extract_service_from_content(item),
                            "relevance_score": 0.9
                        }
                        documentation.append(doc_entry)
            
            # Handle single content string
            elif isinstance(content, str):
                doc_entry = {
                    "title": f"AWS Documentation: {query[:50]}",
                    "content": content,
                    "url": "https://docs.aws.amazon.com/",
                    "service": self._extract_service_from_content(content),
                    "relevance_score": 0.9
                }
                documentation.append(doc_entry)
            
            # Handle direct text in result (fallback)
            elif "text" in result:
                doc_entry = {
                    "title": f"AWS Documentation: {query[:50]}",
                    "content": result["text"],
                    "url": "https://docs.aws.amazon.com/",
                    "service": self._extract_service_from_content(result["text"]),
                    "relevance_score": 0.9
                }
                documentation.append(doc_entry)
            
            # If still no content, create a basic entry with available info
            elif not documentation:
                # Try to extract any text from the result
                result_str = json.dumps(result)
                if len(result_str) > 50:  # Has some content
                    doc_entry = {
                        "title": f"AWS Documentation: {query[:50]}",
                        "content": f"Retrieved AWS documentation for: {query}",
                        "url": "https://docs.aws.amazon.com/",
                        "service": self._extract_service_from_content(query),
                        "relevance_score": 0.5
                    }
                    documentation.append(doc_entry)
            
            self.logger.info(f"Parsed {len(documentation)} documentation entries")
            
        except Exception as e:
            self.logger.error(f"Error parsing tool result: {e}")
            self.logger.error(f"Result was: {result}")
            # Return a basic entry even if parsing fails
            documentation = [{
                "title": f"AWS Documentation: {query[:50]}",
                "content": f"Documentation retrieved for: {query} (parsing error occurred)",
                "url": "https://docs.aws.amazon.com/",
                "service": self._extract_service_from_content(query),
                "relevance_score": 0.3
            }]
            
        return documentation

    def _extract_service_from_content(self, content: str) -> str:
        """
        Extract AWS service name from content.
        
        Args:
            content: The content to analyze
            
        Returns:
            The detected AWS service name or 'general'
        """
        content_lower = content.lower()
        
        # Common AWS services
        services = {
            "s3": ["s3", "simple storage", "bucket"],
            "ec2": ["ec2", "elastic compute", "instance"],
            "lambda": ["lambda", "serverless", "function"],
            "rds": ["rds", "relational database", "mysql", "postgres"],
            "iam": ["iam", "identity", "access management", "role", "policy"],
            "cloudformation": ["cloudformation", "template", "stack"],
            "vpc": ["vpc", "virtual private cloud", "subnet"],
            "cloudwatch": ["cloudwatch", "monitoring", "logs", "metrics"],
            "api gateway": ["api gateway", "rest api", "http api"],
            "dynamodb": ["dynamodb", "nosql", "table"]
        }
        
        for service, keywords in services.items():
            if any(keyword in content_lower for keyword in keywords):
                return service
                
        return "general"

    def _get_aws_docs_urls(self, query: str, services: List[str] = None) -> List[str]:
        """
        Generate likely AWS documentation URLs based on the query and services.
        
        Args:
            query: The user's query
            services: List of AWS services (optional)
            
        Returns:
            List of AWS documentation URLs to try
        """
        urls = []
        
        # Service-specific URLs
        if services:
            for service in services:
                service_lower = service.lower()
                if service_lower == "s3":
                    urls.extend([
                        "https://docs.aws.amazon.com/s3/",
                        "https://docs.aws.amazon.com/AmazonS3/latest/userguide/",
                        "https://docs.aws.amazon.com/AmazonS3/latest/dev/"
                    ])
                elif service_lower == "lambda":
                    urls.extend([
                        "https://docs.aws.amazon.com/lambda/",
                        "https://docs.aws.amazon.com/lambda/latest/dg/"
                    ])
                elif service_lower == "ec2":
                    urls.extend([
                        "https://docs.aws.amazon.com/ec2/",
                        "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/"
                    ])
                elif service_lower == "iam":
                    urls.extend([
                        "https://docs.aws.amazon.com/iam/",
                        "https://docs.aws.amazon.com/IAM/latest/UserGuide/"
                    ])
                elif service_lower == "rds":
                    urls.extend([
                        "https://docs.aws.amazon.com/rds/",
                        "https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/"
                    ])
                elif service_lower == "cloudformation":
                    urls.extend([
                        "https://docs.aws.amazon.com/cloudformation/",
                        "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/"
                    ])
                elif service_lower == "dynamodb":
                    urls.extend([
                        "https://docs.aws.amazon.com/dynamodb/",
                        "https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/"
                    ])
                elif service_lower == "ssm":
                    urls.extend([
                        "https://docs.aws.amazon.com/systems-manager/",
                        "https://docs.aws.amazon.com/systems-manager/latest/userguide/"
                    ])
        
        # Query-based URL detection
        query_lower = query.lower()
        if "parameter store" in query_lower or "ssm" in query_lower:
            urls.extend([
                "https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html",
                "https://docs.aws.amazon.com/systems-manager/latest/userguide/"
            ])
        elif "best practices" in query_lower:
            urls.append("https://docs.aws.amazon.com/wellarchitected/")
        
        # General fallback URLs
        urls.extend([
            "https://docs.aws.amazon.com/",
            "https://aws.amazon.com/documentation/",
            "https://docs.aws.amazon.com/general/latest/gr/"
        ])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_urls = []
        for url in urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)
        
        return unique_urls
    
    def start_server_if_needed(self) -> bool:
        """
        Start AWS MCP server if it's not running.
        
        Returns:
            True if server is running (was already running or successfully started)
        """
        # First check if server is already running
        if self.connect():
            self.logger.info("MCP server is already running")
            return True
        
        self.logger.info("MCP server not running, attempting to start...")
        
        try:
            # Use uvx to run the AWS MCP server
            self.logger.info("Starting AWS MCP server with uvx...")
            self.server_process = subprocess.Popen(
                ["uvx", "awslabs.aws-documentation-mcp-server@latest"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0  # Unbuffered for real-time communication
            )
            
            self.logger.info(f"Started AWS MCP server process with PID: {self.server_process.pid}")
            
            # Wait a moment for the server to start
            time.sleep(1.0)
            
            # Check if process is still running
            if self.server_process.poll() is not None:
                stdout, stderr = self.server_process.communicate()
                self.logger.error("MCP server process terminated immediately")
                self.logger.error(f"Stdout: {stdout}")
                self.logger.error(f"Stderr: {stderr}")
                return False
            
            # Initialize MCP session
            self.logger.info("Attempting to initialize MCP session...")
            if self._initialize_mcp_session():
                self.connected = True
                self.last_health_check = time.time()
                self.logger.info("MCP server started and initialized successfully")
                return True
            else:
                self.logger.error("Failed to initialize MCP session")
                # Get any error output
                if self.server_process.poll() is not None:
                    stdout, stderr = self.server_process.communicate()
                    self.logger.error(f"Server stdout: {stdout}")
                    self.logger.error(f"Server stderr: {stderr}")
                return False
            
        except FileNotFoundError:
            self.logger.error("uvx command not found. Please install uv/uvx first.")
            return False
        except Exception as e:
            self.logger.error(f"Failed to start MCP server: {e}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from MCP server and cleanup."""
        self.logger.info("Disconnecting from MCP server")
        self.connected = False
        
        # Optionally stop the server process if we started it
        if self.server_process and self.server_process.poll() is None:
            self.logger.info("Stopping MCP server process")
            self.server_process.terminate()
            
            # Wait for graceful shutdown
            try:
                self.server_process.wait(timeout=5)
                self.logger.info("MCP server process stopped gracefully")
            except subprocess.TimeoutExpired:
                self.logger.warning("MCP server process didn't stop gracefully, killing it")
                self.server_process.kill()
                self.server_process.wait()
            
            self.server_process = None
    
    def get_server_info(self) -> Dict[str, Any]:
        """
        Get information about the MCP server.
        
        Returns:
            Dictionary with server information
        """
        if not self.is_connected():
            return {"status": "disconnected", "error": "MCP server process not running"}
        
        return {
            "status": "running",
            "pid": self.server_process.pid if self.server_process else None,
            "script_path": str(self.server_script_path),
            "uptime": time.time() - self.last_health_check if self.last_health_check else 0
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to MCP server with detailed diagnostics.
        
        Returns:
            Dictionary with connection test results
        """
        result = {
            "server_script": str(self.server_script_path),
            "script_exists": self.server_script_path.exists(),
            "connected": False,
            "server_info": None,
            "error": None
        }
        
        try:
            # Test if we can connect/check server status
            connected = self.connect()
            result["connected"] = connected
            
            if connected:
                result["server_info"] = self.get_server_info()
            else:
                result["error"] = "MCP server process is not running"
                
        except Exception as e:
            result["error"] = str(e)
        
        return result