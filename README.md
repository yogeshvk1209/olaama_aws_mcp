# MCP-Ollama Integration: AWS Documentation Enhanced LLM

An intelligent command-line interface that combines Ollama LLM with AWS official documentation through Model Context Protocol (MCP) integration. This system automatically detects AWS-related queries and enhances responses with real-time official AWS documentation.

## 🚀 Features

### Core Capabilities
- **🤖 Enhanced LLM Responses**: Automatically augments Ollama responses with official AWS documentation
- **🔍 Smart AWS Detection**: Intelligent detection of AWS-related queries with 95%+ accuracy
- **📚 Real-time Documentation**: Retrieves up-to-date AWS documentation via MCP protocol
- **⚡ Context Enhancement**: Enhances prompts with 20-70x more relevant context
- **🎯 Service-Specific Routing**: Automatically routes queries to appropriate AWS service documentation
- **💻 Rich CLI Interface**: Professional command-line interface with status indicators
- **🔧 Flexible Configuration**: Multi-source configuration with runtime adjustments

### MCP Integration
- **📡 JSON-RPC Communication**: Full MCP protocol implementation with timeout handling
- **🔄 Automatic Server Management**: Starts and manages AWS MCP server lifecycle
- **🛡️ Robust Error Handling**: Graceful fallbacks when MCP server is unavailable
- **📊 Performance Monitoring**: Real-time statistics and connection health monitoring

## 📋 Prerequisites

### Required Software
- **Python 3.7+**
- **Ollama** - Local LLM server ([Installation Guide](https://ollama.ai/))
- **uv/uvx** - Python package manager for MCP server ([Installation Guide](https://docs.astral.sh/uv/getting-started/installation/))

### System Requirements
- macOS, Linux, or Windows
- 4GB+ RAM (for LLM models)
- Internet connection (for AWS documentation retrieval)

## 🛠️ Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd mcp-ollama-integration
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install uv/uvx (for MCP server)
```bash
# macOS (Homebrew)
brew install uv

# Linux/macOS (curl)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 4. Start Ollama Server
```bash
# Install and start Ollama
ollama serve

# Pull a model (in another terminal)
ollama pull qwen2.5:14b  # or your preferred model
```

## 🚀 Quick Start

### Basic Usage
```bash
# Start with MCP integration enabled
python3 ollama_cli.py --start-mcp-now

# Or start normally and enable MCP later
python3 ollama_cli.py
```

### Example Interactions
```bash
# AWS-related queries are automatically enhanced
> What are S3 best practices?
🔍 AWS Query Detected (confidence: 0.95)
📡 MCP Server: Connected
📚 Retrieved 3 AWS documentation entries
[Enhanced response with official AWS S3 documentation]

# Non-AWS queries use standard LLM
> How do I write a Python function?
[Standard Ollama response]
```

## 📖 Usage Guide

### Command Line Options

```bash
python3 ollama_cli.py [OPTIONS]

Options:
  --model TEXT              Ollama model to use (default: qwen2.5:14b)
  --url TEXT               Ollama server URL (default: http://localhost:11434)
  --start-mcp-now          Start MCP server immediately
  --enable-mcp             Enable MCP integration (default: true)
  --disable-mcp            Disable MCP integration
  --log-level TEXT         Logging level (DEBUG, INFO, WARN, ERROR)
  --log-file TEXT          Custom log file path
  --log-dir TEXT           Log directory path
  --config-file TEXT       Custom configuration file
  --help                   Show help message
```

### Interactive Commands

Once running, use these commands in the CLI:

```bash
# Basic interaction
> Your AWS question here

# Configuration commands
> /config show                    # Show current configuration
> /config set mcp_enabled false   # Disable MCP integration
> /config set model llama2:7b     # Change model

# MCP-specific commands
> /mcp status                     # Show MCP server status
> /mcp start                      # Start MCP server
> /mcp stop                       # Stop MCP server
> /mcp test                       # Test MCP connection

# Utility commands
> /stats                          # Show usage statistics
> /help                           # Show help
> /quit or /exit                  # Exit application
```

### Configuration

#### Environment Variables
```bash
# Core settings
export OLLAMA_MODEL="qwen2.5:14b"
export OLLAMA_URL="http://localhost:11434"
export LOG_LEVEL="INFO"

# MCP settings
export MCP_ENABLED="true"
export MCP_AUTO_START="true"

# Logging
export LOG_DIR="./logs"
```

#### Configuration File
Create `config.json`:
```json
{
  "ollama": {
    "model": "qwen2.5:14b",
    "url": "http://localhost:11434",
    "timeout": 30
  },
  "mcp": {
    "enabled": true,
    "auto_start": true,
    "timeout": 10
  },
  "logging": {
    "level": "INFO",
    "file": "./logs/ollama-cli.log"
  }
}
```

## 🏗️ Architecture

### System Components

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   CLI Interface │    │  Enhanced Ollama │    │   AWS Query     │
│                 │◄──►│     Client       │◄──►│   Detector      │
│  - Commands     │    │                  │    │                 │
│  - Status       │    │ - MCP Integration│    │ - Service ID    │
│  - Config       │    │ - Context Enhance│    │ - Confidence    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Context         │    │  MCP Client      │    │   AWS MCP       │
│ Enhancer        │◄──►│  Manager         │◄──►│   Server        │
│                 │    │                  │    │                 │
│ - Doc Formatting│    │ - JSON-RPC       │    │ - AWS Docs API  │
│ - Prompt Build  │    │ - Lifecycle Mgmt │    │ - Tool Calls    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Data Flow

1. **Query Input** → CLI Interface receives user query
2. **AWS Detection** → Query analyzed for AWS content (confidence scoring)
3. **MCP Routing** → If AWS detected, route to MCP client manager
4. **Documentation Retrieval** → MCP server fetches official AWS docs
5. **Context Enhancement** → Documentation formatted and integrated
6. **LLM Processing** → Enhanced prompt sent to Ollama
7. **Response Delivery** → Enriched response returned to user

## 🧪 Testing

### Run Complete Test Suite
```bash
cd tests
python3 run_all_tests.py
```

### Individual Component Tests
```bash
# AWS query detection
python3 tests/test_aws_detection.py

# MCP client functionality  
python3 tests/test_mcp_client.py

# Enhanced Ollama client
python3 tests/test_enhanced_ollama.py

# Context enhancement
python3 tests/test_context_enhancer.py

# CLI interface
python3 tests/test_cli_interface.py

# Configuration system
python3 tests/test_config.py

# Integration tests
python3 tests/integration_test_suite.py

# Demo/showcase
python3 tests/demo_mcp_integration.py
```

### Test Coverage
- ✅ AWS Query Detection (95%+ accuracy)
- ✅ MCP Server Communication
- ✅ Context Enhancement Pipeline
- ✅ Configuration Management
- ✅ Error Handling & Fallbacks
- ✅ CLI Interface Functionality
- ✅ End-to-End Integration

## 📁 Project Structure

```
mcp-ollama-integration/
├── 📄 ollama_cli.py                 # Main enhanced CLI application
├── 📄 enhanced_ollama_client.py     # LLM client with MCP integration
├── 📄 aws_query_detector.py         # AWS query detection system
├── 📄 mcp_client_manager.py         # MCP server lifecycle management
├── 📄 context_enhancer.py           # Documentation formatting
├── 📄 enhanced_cli_interface.py     # Rich CLI interface
├── 📄 config.py                     # Configuration system
├── 📄 config_utils.py               # Configuration utilities
├── 📄 ollama_client.py              # Base Ollama HTTP client
├── 📄 cli_interface.py              # Base CLI interface
├── 📄 logging_utils.py              # Logging utilities
├── 📄 server_status.py              # Server status monitoring
├── 📄 requirements.txt              # Python dependencies
├── 📁 tests/                        # Comprehensive test suite
│   ├── 📄 run_all_tests.py          # Test runner
│   ├── 📄 integration_test_suite.py # Integration tests
│   ├── 📄 test_*.py                 # Component tests
│   └── 📄 demo_mcp_integration.py   # Feature demonstration
├── 📁 .kiro/specs/                  # Development specifications
│   └── 📁 mcp-ollama-integration/
│       ├── 📄 requirements.md       # Feature requirements
│       ├── 📄 design.md             # System design
│       └── 📄 tasks.md              # Implementation tasks
└── 📄 README.md                     # This file
```

## ⚙️ Configuration Options

### MCP Integration Settings
```python
# Enable/disable MCP integration
mcp_enabled = True

# Auto-start MCP server
mcp_auto_start = True

# MCP communication timeout
mcp_timeout = 10.0

# Maximum documentation entries per query
max_docs_per_query = 3

# Context length limit
max_context_length = 2000
```

### AWS Detection Settings
```python
# Confidence threshold for AWS detection
aws_confidence_threshold = 0.7

# AWS services to monitor
aws_services = ["s3", "ec2", "lambda", "rds", "iam", ...]

# Query enhancement ratio
enhancement_ratio_target = 20.0
```

## 🔧 Troubleshooting

### Common Issues

#### MCP Server Won't Start
```bash
# Check if uvx is installed
uvx --version

# Install if missing
curl -LsSf https://astral.sh/uv/install.sh | sh

# Test MCP server manually
uvx awslabs.aws-documentation-mcp-server@latest
```

#### Ollama Connection Issues
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if needed
ollama serve

# Check available models
ollama list
```

#### AWS Documentation Not Loading
```bash
# Test MCP connection
python3 -c "
from mcp_client_manager import MCPClientManager
import logging
logging.basicConfig(level=logging.DEBUG)
manager = MCPClientManager()
print(manager.test_connection())
"
```

### Debug Mode
```bash
# Enable detailed logging
python3 ollama_cli.py --log-level DEBUG

# Check logs
tail -f logs/ollama-cli.log
```

## 📊 Performance Metrics

### Typical Performance
- **AWS Query Detection**: < 50ms
- **MCP Documentation Retrieval**: 1-3 seconds
- **Context Enhancement**: < 100ms
- **Total Enhancement Overhead**: 1-4 seconds
- **Enhancement Ratio**: 20-70x context expansion

### Resource Usage
- **Memory**: ~100-200MB (excluding LLM)
- **CPU**: Minimal (< 5% during queries)
- **Network**: ~1-5KB per AWS documentation request

## 🤝 Contributing

### Development Setup
```bash
# Clone and setup
git clone <repository-url>
cd mcp-ollama-integration
pip install -r requirements.txt

# Run tests
python3 tests/run_all_tests.py

# Check code style
flake8 *.py
```

### Adding New AWS Services
1. Update `aws_query_detector.py` service definitions
2. Add URL mappings in `mcp_client_manager.py`
3. Update tests in `tests/test_aws_detection.py`

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Ollama Team** - For the excellent local LLM server
- **AWS Labs** - For the AWS documentation MCP server
- **MCP Protocol** - For the Model Context Protocol specification
- **Anthropic** - For MCP protocol development

## 📞 Support

For issues, questions, or contributions:
1. Check the troubleshooting section above
2. Review existing issues in the repository
3. Create a new issue with detailed information
4. Include logs and system information

## License
This project is licensed under the MIT License - see the LICENSE file for details!!! Enjoy!!!

---

**Made with ❤️ for developers who want AWS-enhanced LLM interactions**
