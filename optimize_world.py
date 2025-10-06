#!/usr/bin/env python3
"""
Optimize Gazebo world files for better performance and stability.
This helps prevent crashes and rendering issues with large OSM meshes.
"""

import argparse
import sys
from pathlib import Path


def optimize_world_for_performance(world_path: Path, output_path: Path = None) -> None:
    """
    Optimize a Gazebo world file for better performance with large meshes.
    """
    if output_path is None:
        output_path = world_path.parent / f"{world_path.stem}_optimized{world_path.suffix}"
    
    print(f"Optimizing world file: {world_path}")
    
    content = world_path.read_text()
    
    # Performance optimizations
    optimizations = [
        # Reduce physics accuracy for better performance
        ("<max_step_size>0.004</max_step_size>", "<max_step_size>0.01</max_step_size>"),
        ("<real_time_update_rate>250</real_time_update_rate>", "<real_time_update_rate>100</real_time_update_rate>"),
        ("<iters>10</iters>", "<iters>5</iters>"),
        
        # Disable shadows for performance (can cause issues with large meshes)
        ("<shadows>1</shadows>", "<shadows>0</shadows>"),
        ("<cast_shadows>1</cast_shadows>", "<cast_shadows>0</cast_shadows>"),
        ("<cast_shadows>false</cast_shadows>", "<cast_shadows>false</cast_shadows>"),  # Keep existing false
        
        # Optimize collision detection
        ("<contact_surface_layer>0.001</contact_surface_layer>", "<contact_surface_layer>0.01</contact_surface_layer>"),
    ]
    
    for old, new in optimizations:
        content = content.replace(old, new)
    
    # Add performance-focused physics engine settings
    if '<physics name="default_physics"' in content and 'max_contacts' not in content:
        content = content.replace(
            '<ode>',
            '''<ode>
        <max_contacts>10</max_contacts>'''
        )
    
    # Simplify collision geometry by removing it for visual-only elements
    # This prevents physics calculations on complex building meshes
    collision_section = '''        <collision name="osm_collision">
          <geometry>
            <mesh>
              <uri>meshes/'''
    
    visual_only_replacement = '''        <!-- Collision disabled for performance - use simplified collision if needed
        <collision name="osm_collision">
          <geometry>
            <box>
              <size>1000 1000 0.1</size>
            </box>
          </geometry>
        </collision>
        -->'''
    
    # Comment out complex mesh collision to prevent physics issues
    if collision_section in content:
        # Find and replace the entire collision section
        start = content.find(collision_section)
        if start != -1:
            end = content.find('</collision>', start) + len('</collision>')
            if end != -1:
                collision_block = content[start:end]
                content = content.replace(collision_block, visual_only_replacement)
    
    output_path.write_text(content)
    print(f"Optimized world written to: {output_path}")
    
    # Print optimization tips
    print("\nOptimizations applied:")
    print("- Reduced physics update rate and iterations for better performance")
    print("- Disabled shadows to prevent rendering issues with large meshes")
    print("- Commented out complex mesh collision (prevents physics crashes)")
    print("- Increased contact surface layer for more stable physics")
    
    print("\nAdditional tips to prevent crashes:")
    print("1. Set environment variables before running Gazebo:")
    print("   export LIBGL_ALWAYS_SOFTWARE=1  # Force software rendering if GPU issues")
    print("   export GAZEBO_MODEL_PATH=$PWD/maps")
    print("2. Use smaller OSM area extracts for better performance")
    print("3. Consider using gazebo --verbose to get more error information")


def main():
    parser = argparse.ArgumentParser(
        description="Optimize Gazebo world files for better performance with large OSM meshes"
    )
    parser.add_argument("world_file", help="Path to the .world file to optimize")
    parser.add_argument("-o", "--output", help="Output path (default: input_optimized.world)")
    
    args = parser.parse_args()
    
    world_path = Path(args.world_file)
    if not world_path.exists():
        print(f"Error: World file not found: {world_path}")
        return 1
    
    output_path = Path(args.output) if args.output else None
    
    try:
        optimize_world_for_performance(world_path, output_path)
        return 0
    except Exception as e:
        print(f"Error optimizing world file: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())