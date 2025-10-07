#!/usr/bin/env python3
"""
Integrated OSM to Gazebo workflow - Complete pipeline with data cleaning
This script combines data cleaning with the conversion and optimization steps
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Import utility functions if available or define them
try:
    from utils import print_info, print_success, print_warn, print_error
except ImportError:
    # Fallback if utils.py is not available
    try:
        from colorama import Fore, Style, init as colorama_init
        colorama_init(autoreset=True)
    except ImportError:  # pragma: no cover - color is optional
        class _Dummy:
            def __getattr__(self, name):
                return ""
    
        def colorama_init(*_args, **_kwargs):
            return None
    
        Fore = Style = _Dummy()  # type: ignore
    
    def print_info(message: str) -> None:
        print(f"{Fore.BLUE}[INFO]{Style.RESET_ALL} {message}")
    
    def print_success(message: str) -> None:
        print(f"{Fore.GREEN}[OK]{Style.RESET_ALL} {message}")
    
    def print_warn(message: str) -> None:
        print(f"{Fore.YELLOW}[WARN]{Style.RESET_ALL} {message}")
    
    def print_error(message: str) -> None:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {message}", file=sys.stderr)


def check_dependencies():
    """Check if required tools and scripts are available."""
    missing = []
    script_dir = Path(__file__).parent
    
    # Check for GDAL/OGR
    try:
        subprocess.run(["ogr2ogr", "--version"], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE, 
                      check=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        missing.append("GDAL/OGR (install with: apt-get install gdal-bin python3-gdal)")
    
    # Check for Java (required for OSM2World)
    try:
        subprocess.run(["java", "-version"], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE, 
                      check=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        missing.append("Java (install with: apt-get install default-jre)")
    
    # Check for required scripts
    required_scripts = [
        "clean_osm_data.py",
        "convert_osm_to_gazebo.py",
        "optimize_complete.py"
    ]
    
    for script in required_scripts:
        if not (script_dir / script).exists():
            missing.append(f"Script {script} not found")
    
    return missing


def run_step(command, description, critical=True):
    """Run a command and handle errors."""
    print_info(description)
    
    try:
        result = subprocess.run(command, 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               text=True, 
                               check=True)
        
        print_success(f"{description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"{description} failed with code {e.returncode}")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print_error(e.stderr)
        
        if critical:
            sys.exit(e.returncode)
        return False
    except Exception as e:
        print_error(f"Error during {description}: {e}")
        if critical:
            sys.exit(1)
        return False


def integrated_workflow(input_osm, output_dir=None, scale=1.0, auto_launch=False, simple_mode=False):
    """Run the complete integrated workflow."""
    script_dir = Path(__file__).parent
    input_path = Path(input_osm)
    
    # Determine output directory
    if output_dir:
        output_dir = Path(output_dir)
    else:
        # Keep the original directory structure, preserving the parent folder(s)
        # Example: maps/roma/map.osm -> maps/roma/
        parent_dir = input_path.parent
        output_dir = parent_dir
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Define file paths
    cleaned_osm = output_dir / f"{input_path.stem}_cleaned.osm"
    world_path = output_dir / f"{input_path.stem}.world"
    optimized_world = output_dir / f"{input_path.stem}_optimized.world"
    
    # Create meshes directory
    mesh_dir = output_dir / "meshes"
    mesh_dir.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Clean OSM data using GDAL/OGR
    run_step(
        [sys.executable, script_dir / "clean_osm_data.py", input_path, cleaned_osm],
        "Cleaning OSM data with GDAL/OGR"
    )
    
    # Step 2: Convert cleaned OSM to Gazebo world
    cmd = [
        sys.executable, 
        script_dir / "convert_osm_to_gazebo.py", 
        cleaned_osm, 
        world_path,
        "--scale", str(scale)
    ]
    
    # Add simple mode if requested
    if simple_mode:
        cmd.append("--simple")
        
    run_step(cmd, "Converting OSM to Gazebo world")
    
    # Step 3: Optimize world
    run_step(
        [
            sys.executable,
            script_dir / "optimize_complete.py",
            world_path
        ],
        "Optimizing world"
    )
    
    # Print success
    print_success("\nIntegrated workflow completed successfully!")
    print_success(f"- Cleaned OSM: {cleaned_osm}")
    print_success(f"- Gazebo world: {world_path}")
    print_success(f"- Optimized world: {optimized_world}")
    print_success(f"- 3D meshes: {output_dir}/meshes/")
    
    # Launch Gazebo if requested
    if auto_launch:
        env = os.environ.copy()
        env["GAZEBO_MODEL_PATH"] = f"{os.getcwd()}/maps:{env.get('GAZEBO_MODEL_PATH', '')}"
        
        print_info("\nLaunching Gazebo with optimized world...")
        try:
            subprocess.Popen(["gz", "sim", optimized_world], env=env)
        except Exception as e:
            print_error(f"Failed to launch Gazebo: {e}")
    else:
        print_info("\nTo launch Gazebo with the optimized world:")
        print(f"  export GAZEBO_MODEL_PATH=$PWD/maps:$GAZEBO_MODEL_PATH")
        print(f"  gz sim {optimized_world}")


def main():
    parser = argparse.ArgumentParser(
        description="Integrated OSM to Gazebo workflow with data cleaning and optimization"
    )
    parser.add_argument("input_osm", help="Path to input .osm file")
    parser.add_argument(
        "--output", "-o",
        help="Path to output directory (default: maps/NAME)"
    )
    parser.add_argument(
        "--scale", type=float, default=1.0,
        help="Scale factor for the model (default: 1.0)"
    )
    parser.add_argument(
        "--launch", action="store_true",
        help="Automatically launch Gazebo after conversion"
    )
    parser.add_argument(
        "--simple", action="store_true",
        help="Use simple mode with fewer details to avoid geometry errors in complex OSM files"
    )
    
    args = parser.parse_args()
    
    # Check dependencies
    missing_deps = check_dependencies()
    if missing_deps:
        print_error("Missing dependencies:")
        for dep in missing_deps:
            print(f"  - {dep}")
        sys.exit(1)
    
    # Run the workflow
    integrated_workflow(
        args.input_osm,
        args.output,
        args.scale,
        args.launch,
        args.simple
    )


if __name__ == "__main__":
    main()