#!/usr/bin/env python3
"""
Utility functions for OSM to Gazebo World conversion and optimization.
"""

import os
import subprocess
import sys
from pathlib import Path


# Color output constants
try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init()
except ImportError:
    # Create mock color objects if colorama is not available
    class DummyColor:
        def __getattr__(self, name):
            return ""
    Fore = Style = DummyColor()


def print_info(message: str) -> None:
    """Print an info message with color"""
    print(f"{Fore.BLUE}[INFO]{Style.RESET_ALL} {message}")


def print_success(message: str) -> None:
    """Print a success message with color"""
    print(f"{Fore.GREEN}[OK]{Style.RESET_ALL} {message}")


def print_warn(message: str) -> None:
    """Print a warning message with color"""
    print(f"{Fore.YELLOW}[WARN]{Style.RESET_ALL} {message}")


def print_error(message: str) -> None:
    """Print an error message with color"""
    print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {message}", file=sys.stderr)


def ensure_osm2world_path() -> Path:
    """Find the OSM2World JAR file path"""
    # Default install path inside the container
    default_path = Path("/opt/osm2world/OSM2World.jar")
    env_path = Path(os.environ.get("OSM2WORLD_JAR", default_path.as_posix()))
    
    if env_path.exists():
        return env_path
    
    # Debian/Ubuntu package path
    deb_path = Path("/usr/share/osm2world/OSM2World.jar")
    if deb_path.exists():
        return deb_path
    
    # Fallback: try local project dir
    local_path = Path("OSM2World.jar")
    if local_path.exists():
        return local_path
    
    raise FileNotFoundError(
        "OSM2World.jar not found. Ensure it exists at /opt/osm2world/OSM2World.jar or set OSM2WORLD_JAR."
    )


def run_script(script_path: Path, args: list, description: str) -> bool:
    """Run a Python script with arguments and handle errors"""
    try:
        print_info(f"{description}...")
        result = subprocess.run(
            [sys.executable, script_path.as_posix()] + args,
            check=True, 
            capture_output=True, 
            text=True
        )
        
        # Print any output from the script
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    print(f"  {line}")
        
        print_success(f"{description} completed")
        return True
        
    except subprocess.CalledProcessError as e:
        print_error(f"{description} failed: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        print_error(f"Unexpected error in {description}: {e}")
        return False


def run_process(cmd: list, description: str) -> subprocess.CompletedProcess:
    """Run a process with error handling"""
    try:
        print_info(f"{description}...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print_success(f"{description} completed")
        return result
    except subprocess.CalledProcessError as e:
        print_error(f"{description} failed with exit code {e.returncode}")
        if e.stderr:
            print_error(f"Error details: {e.stderr}")
        raise e