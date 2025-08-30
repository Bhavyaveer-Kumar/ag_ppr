"""
Utility functions for the CLI application.
"""

import os
import json
from pathlib import Path
from typing import Any


# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_success(message: str):
    """Print a success message in green."""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")


def print_error(message: str):
    """Print an error message in red."""
    print(f"{Colors.RED}✗ {message}{Colors.END}")


def print_info(message: str):
    """Print an info message in blue."""
    print(f"{Colors.BLUE}ℹ {message}{Colors.END}")


def print_progress(message: str):
    """Print a progress message in cyan."""
    print(f"{Colors.CYAN}⋯ {message}{Colors.END}")


def print_warning(message: str):
    """Print a warning message in yellow."""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")


def setup_directories():
    """Create necessary directories for the application."""
    directories = [
        "data",
        "data/raw_papers",
        "outputs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)


def load_json(file_path: str) -> Any:
    """Load data from a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print_error(f"File not found: {file_path}")
        return None
    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON in {file_path}: {str(e)}")
        return None


def save_json(data: Any, file_path: str):
    """Save data to a JSON file."""
    try:
        # Create directory if it doesn't exist
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print_success(f"Data saved to: {file_path}")
        
    except Exception as e:
        print_error(f"Failed to save {file_path}: {str(e)}")
        raise


def file_exists(file_path: str) -> bool:
    """Check if a file exists."""
    return Path(file_path).exists()


def get_file_size(file_path: str) -> int:
    """Get file size in bytes."""
    try:
        return Path(file_path).stat().st_size
    except OSError:
        return 0


def clean_filename(filename: str) -> str:
    """Clean a filename by removing invalid characters."""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove extra spaces and underscores
    filename = '_'.join(filename.split())
    
    return filename


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def create_cache_key(subject: str, topic: str) -> str:
    """Create a cache key from subject and topic."""
    return f"{subject.lower().replace(' ', '_')}_{topic.lower().replace(' ', '_')}"


def is_valid_pdf(file_path: str) -> bool:
    """Check if a file is a valid PDF."""
    try:
        with open(file_path, 'rb') as f:
            header = f.read(4)
            return header == b'%PDF'
    except Exception:
        return False