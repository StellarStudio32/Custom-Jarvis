"""
File Operations Action Module
Create, read, and append files with sandbox validation.
All operations are restricted to the workspace directory.
"""

from pathlib import Path
import config


def _validate_path(filename: str) -> Path:
    """
    Validate that the given filename is within the workspace directory.
    Prevents directory traversal attacks.
    
    Args:
        filename: Filename or relative path
        
    Returns:
        Validated absolute Path object
        
    Raises:
        ValueError: If path escapes the workspace directory
    """
    try:
        # Resolve the path relative to workspace
        requested_path = (config.WORKSPACE_DIR / filename).resolve()
        workspace_resolved = config.WORKSPACE_DIR.resolve()
        
        # Check if requested path is within workspace
        try:
            requested_path.relative_to(workspace_resolved)
        except ValueError:
            raise ValueError(f"Path {filename} is outside workspace directory {config.WORKSPACE_DIR}")
        
        return requested_path
    except Exception as e:
        raise ValueError(f"Invalid path: {e}")


def create_file(filename: str, content: str) -> str:
    """
    Create a file in the workspace directory with the given content.
    
    Args:
        filename: Filename or relative path within workspace
        content: File content to write
        
    Returns:
        Confirmation message
        
    Raises:
        ValueError: If path is invalid or outside workspace
    """
    try:
        path = _validate_path(filename)
        # Create parent directories if needed
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return f"Created file: {filename}"
    except ValueError as e:
        raise
    except Exception as e:
        print(f"Error creating file {filename}: {e}")
        raise ValueError(f"Failed to create file: {e}")


def read_file(filename: str) -> str:
    """
    Read and return the contents of a file in the workspace.
    
    Args:
        filename: Filename or relative path within workspace
        
    Returns:
        File contents as string
        
    Raises:
        ValueError: If path is invalid or file doesn't exist
    """
    try:
        path = _validate_path(filename)
        if not path.exists():
            raise ValueError(f"File not found: {filename}")
        return path.read_text()
    except ValueError:
        raise
    except Exception as e:
        print(f"Error reading file {filename}: {e}")
        raise ValueError(f"Failed to read file: {e}")


def append_file(filename: str, content: str) -> str:
    """
    Append content to an existing file in the workspace.
    Creates the file if it doesn't exist.
    
    Args:
        filename: Filename or relative path within workspace
        content: Content to append
        
    Returns:
        Confirmation message
        
    Raises:
        ValueError: If path is invalid or outside workspace
    """
    try:
        path = _validate_path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        # Append to file (or create if doesn't exist)
        with path.open("a") as f:
            f.write(content)
        return f"Appended to file: {filename}"
    except ValueError:
        raise
    except Exception as e:
        print(f"Error appending to file {filename}: {e}")
        raise ValueError(f"Failed to append to file: {e}")
