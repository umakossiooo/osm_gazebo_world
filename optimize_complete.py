#!/usr/bin/env python3
"""
Complete optimization pipeline for OSM-generated Gazebo worlds.
This script automates all the optimization steps needed after OSM conversion.
"""

import argparse
import sys
import subprocess
from pathlib import Path


def print_status(message: str, status: str = "INFO") -> None:
    colors = {
        "INFO": "\033[0;34m",
        "SUCCESS": "\033[0;32m", 
        "WARN": "\033[1;33m",
        "ERROR": "\033[0;31m"
    }
    reset = "\033[0m"
    print(f"{colors.get(status, colors['INFO'])}[{status}]{reset} {message}")


def run_script(script_path: Path, args: list, description: str) -> bool:
    """Run a Python script with arguments and handle errors."""
    try:
        print_status(f"{description}...")
        result = subprocess.run([
            sys.executable, 
            script_path.as_posix()
        ] + args, check=True, capture_output=True, text=True)
        
        # Print any output from the script
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    print(f"  {line}")
        
        print_status(f"{description} completed", "SUCCESS")
        return True
        
    except subprocess.CalledProcessError as e:
        print_status(f"{description} failed: {e}", "ERROR")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        print_status(f"Unexpected error in {description}: {e}", "ERROR")
        return False


def optimize_complete_world(world_path: Path, auto_launch: bool = False) -> None:
    """
    Complete optimization pipeline for a Gazebo world file.
    
    Steps:
    1. Fix mesh normals 
    2. Optimize world file
    3. Fix mesh orientation
    4. Update world to use fixed mesh
    5. Optionally launch Gazebo
    """
    
    if not world_path.exists():
        print_status(f"World file not found: {world_path}", "ERROR")
        return
    
    print_status(f"Starting complete optimization for: {world_path}")
    
    # Determine paths
    world_dir = world_path.parent
    world_stem = world_path.stem
    meshes_dir = world_dir / "meshes"
    
    # Find the corresponding mesh file
    mesh_path = meshes_dir / f"{world_stem}.obj"
    if not mesh_path.exists():
        print_status(f"Mesh file not found: {mesh_path}", "ERROR")
        return
    
    # Define output paths
    fixed_mesh_path = meshes_dir / f"{world_stem}_fixed.obj"
    optimized_world_path = world_dir / f"{world_stem}_optimized.world"
    
    script_dir = Path(__file__).parent
    success_count = 0
    total_steps = 4
    
    # Step 1: Fix mesh normals
    if run_script(
        script_dir / "fix_mesh_normals.py",
        [mesh_path.as_posix(), "-o", fixed_mesh_path.as_posix()],
        "Fixing mesh normals"
    ):
        success_count += 1
    
    # Step 2: Optimize world file  
    if run_script(
        script_dir / "optimize_world.py", 
        [world_path.as_posix(), "-o", optimized_world_path.as_posix()],
        "Optimizing world configuration"
    ):
        success_count += 1
    
    # Step 3: Fix orientation in optimized world
    if optimized_world_path.exists():
        if run_script(
            script_dir / "fix_orientation.py",
            [optimized_world_path.as_posix()],
            "Fixing mesh orientation"
        ):
            success_count += 1
    
    # Step 4: Update world to use fixed mesh
    if optimized_world_path.exists() and fixed_mesh_path.exists():
        try:
            print_status("Updating world to use fixed mesh...")
            content = optimized_world_path.read_text()
            
            # Replace mesh references
            old_mesh_ref = f"meshes/{world_stem}.obj"
            new_mesh_ref = f"meshes/{world_stem}_fixed.obj"
            
            if old_mesh_ref in content:
                content = content.replace(old_mesh_ref, new_mesh_ref)
                optimized_world_path.write_text(content)
                print_status("Updated world to use fixed mesh", "SUCCESS")
                success_count += 1
            else:
                print_status(f"No mesh reference found: {old_mesh_ref}", "WARN")
                
        except Exception as e:
            print_status(f"Failed to update world file: {e}", "ERROR")
    
    # Summary
    print_status(f"Optimization complete: {success_count}/{total_steps} steps successful")
    
    if success_count == total_steps:
        print_status("🎉 All optimizations applied successfully!", "SUCCESS")
        print()
        print_status("Generated files:")
        print(f"  📄 Optimized world: {optimized_world_path}")
        print(f"  🎯 Fixed mesh: {fixed_mesh_path}")
        print()
        print_status("Ready to launch:")
        print(f"  export GAZEBO_MODEL_PATH=$PWD/maps:$GAZEBO_MODEL_PATH")
        print(f"  gz sim {optimized_world_path}")
        
        if auto_launch:
            print()
            print_status("Auto-launching Gazebo...")
            try:
                subprocess.run([
                    "bash", "-c", 
                    f"export GAZEBO_MODEL_PATH=$PWD/maps:$GAZEBO_MODEL_PATH && gz sim {optimized_world_path}"
                ])
            except Exception as e:
                print_status(f"Failed to launch Gazebo: {e}", "ERROR")
    
    else:
        print_status("Some optimizations failed. Check the errors above.", "WARN")


def main():
    parser = argparse.ArgumentParser(
        description="Complete optimization pipeline for OSM-generated Gazebo worlds"
    )
    parser.add_argument("world_file", help="Path to the .world file to optimize")
    parser.add_argument("--launch", action="store_true", 
                       help="Automatically launch Gazebo after optimization")
    
    args = parser.parse_args()
    
    world_path = Path(args.world_file)
    optimize_complete_world(world_path, args.launch)


if __name__ == "__main__":
    main()