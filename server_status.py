#!/usr/bin/env python3
"""Server status utilities for MCP server monitoring."""

import os
import time
from typing import Optional
from pathlib import Path


def check_log_file_activity(log_file_path: str, timeout_seconds: int = 30) -> bool:
    """
    Check if the log file shows recent activity.
    
    Args:
        log_file_path: Path to the log file to monitor
        timeout_seconds: How long to consider activity as "recent"
    
    Returns:
        True if log file has recent activity, False otherwise
    """
    try:
        log_path = Path(log_file_path)
        if not log_path.exists():
            return False
        
        # Get last modification time
        last_modified = log_path.stat().st_mtime
        current_time = time.time()
        
        # Check if modified within timeout period
        return (current_time - last_modified) <= timeout_seconds
        
    except Exception:
        return False


def get_log_file_size(log_file_path: str) -> Optional[int]:
    """
    Get the size of the log file in bytes.
    
    Args:
        log_file_path: Path to the log file
    
    Returns:
        File size in bytes, or None if file doesn't exist
    """
    try:
        log_path = Path(log_file_path)
        if log_path.exists():
            return log_path.stat().st_size
        return None
    except Exception:
        return None


def tail_log_file(log_file_path: str, lines: int = 10) -> list:
    """
    Get the last N lines from the log file.
    
    Args:
        log_file_path: Path to the log file
        lines: Number of lines to retrieve from the end
    
    Returns:
        List of last N lines from the log file
    """
    try:
        log_path = Path(log_file_path)
        if not log_path.exists():
            return []
        
        with open(log_path, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            return all_lines[-lines:] if len(all_lines) >= lines else all_lines
            
    except Exception:
        return []


def display_server_status(config, logger):
    """Display current server status information."""
    print("\n📊 Server Status:")
    print("-" * 40)
    
    # Check log file activity
    has_activity = check_log_file_activity(config.log_file)
    activity_status = "🟢 Active" if has_activity else "🔴 Inactive"
    print(f"Activity: {activity_status}")
    
    # Check log file size
    file_size = get_log_file_size(config.log_file)
    if file_size is not None:
        print(f"Log size: {file_size} bytes")
    else:
        print("Log size: File not found")
    
    # Show recent log entries
    recent_logs = tail_log_file(config.log_file, 3)
    if recent_logs:
        print("\nRecent log entries:")
        for line in recent_logs:
            print(f"  {line.strip()}")
    
    print("-" * 40)