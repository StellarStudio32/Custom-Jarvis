"""
Shell Operations Action Module
Execute whitelisted shell commands only.
"""

import subprocess

# Frozenset of allowed commands
ALLOWED_COMMANDS = frozenset({"ls", "pwd", "git", "echo", "python", "pip", "open"})


def run_command(cmd: str) -> str:
    """
    Execute a shell command from the allowlist.
    
    Args:
        cmd: Shell command string (e.g., "pwd", "git status")
        
    Returns:
        Command output (stdout)
        
    Raises:
        ValueError: If command is not in allowlist
    """
    try:
        # Extract base command (first word)
        base_cmd = cmd.split()[0].lower() if cmd.strip() else ""
        
        # Check against allowlist
        if base_cmd not in ALLOWED_COMMANDS:
            raise ValueError(f"Command '{base_cmd}' is not in allowlist. Allowed: {', '.join(ALLOWED_COMMANDS)}")
        
        # Execute command safely
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Return stdout, or stderr if command failed
        if result.returncode == 0:
            return result.stdout if result.stdout else "(command executed)"
        else:
            return f"Error: {result.stderr}"
    
    except ValueError:
        raise
    except subprocess.TimeoutExpired:
        raise ValueError("Command execution timed out (10s limit)")
    except Exception as e:
        print(f"Error executing command: {e}")
        raise ValueError(f"Command execution failed: {e}")
