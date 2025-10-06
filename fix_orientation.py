#!/usr/bin/env python3
"""
Fix mesh orientation in Gazebo world files.
OSM meshes are often generated in vertical orientation and need to be rotated.
"""

import argparse
import sys
from pathlib import Path


def fix_mesh_orientation(world_path: Path, output_path: Path = None, rotation: str = "1.5708 0 0") -> None:
    """
    Fix mesh orientation by adding or updating the pose rotation in a Gazebo world file.
    
    Args:
        world_path: Path to the input world file
        output_path: Path for output (default: overwrite input)
        rotation: Rotation angles in radians as "roll pitch yaw" (default: 90° roll)
    """
    if output_path is None:
        output_path = world_path
    
    print(f"Fixing orientation in: {world_path}")
    
    content = world_path.read_text()
    
    # Check if pose already exists in the osm_environment model
    if '<model name="osm_environment">' in content and '<pose>' in content:
        print("Pose already exists, updating rotation...")
        
        # Find the osm_environment model section
        model_start = content.find('<model name="osm_environment">')
        if model_start != -1:
            # Look for existing pose within this model
            model_section_start = model_start
            model_section_end = content.find('</model>', model_start)
            
            if model_section_end != -1:
                model_section = content[model_section_start:model_section_end + 8]  # +8 for </model>
                
                if '<pose>' in model_section:
                    # Update existing pose
                    pose_start = model_section.find('<pose>') + len('<pose>')
                    pose_end = model_section.find('</pose>')
                    
                    if pose_end != -1:
                        # Replace the pose content
                        new_pose_content = f"0 0 0 {rotation}"
                        updated_section = (model_section[:pose_start] + 
                                         new_pose_content + 
                                         model_section[pose_end:])
                        content = (content[:model_section_start] + 
                                 updated_section + 
                                 content[model_section_end + 8:])
                        print(f"Updated existing pose to: {new_pose_content}")
    else:
        # Add new pose element
        print("Adding new pose rotation...")
        
        # Look for the osm_environment model
        target = '<model name="osm_environment">\n      <static>true</static>'
        replacement = f'''<model name="osm_environment">
      <static>true</static>
      <!-- Rotate mesh to horizontal orientation (OSM meshes are often vertical) -->
      <pose>0 0 0 {rotation}</pose>'''
        
        if target in content:
            content = content.replace(target, replacement)
            print(f"Added pose rotation: 0 0 0 {rotation}")
        else:
            print("Warning: Could not find osm_environment model to modify")
    
    output_path.write_text(content)
    print(f"Fixed world file written to: {output_path}")
    
    # Provide helpful information about the rotation
    angles = rotation.split()
    if len(angles) >= 3:
        roll_deg = float(angles[0]) * 180 / 3.14159
        pitch_deg = float(angles[1]) * 180 / 3.14159
        yaw_deg = float(angles[2]) * 180 / 3.14159
        print(f"Applied rotation: Roll={roll_deg:.1f}°, Pitch={pitch_deg:.1f}°, Yaw={yaw_deg:.1f}°")


def main():
    parser = argparse.ArgumentParser(
        description="Fix mesh orientation in Gazebo world files by adding rotation"
    )
    parser.add_argument("world_file", help="Path to the .world file to fix")
    parser.add_argument("-o", "--output", help="Output path (default: overwrite input)")
    parser.add_argument("-r", "--rotation", default="1.5708 0 0", 
                       help="Rotation as 'roll pitch yaw' in radians (default: '1.5708 0 0' = 90° roll)")
    
    args = parser.parse_args()
    
    world_path = Path(args.world_file)
    if not world_path.exists():
        print(f"Error: World file not found: {world_path}")
        return 1
    
    output_path = Path(args.output) if args.output else None
    
    try:
        fix_mesh_orientation(world_path, output_path, args.rotation)
        print("\nCommon rotation values:")
        print("  1.5708 0 0    - 90° roll (vertical to horizontal)")
        print("  -1.5708 0 0   - -90° roll (reverse)")
        print("  0 1.5708 0    - 90° pitch")
        print("  0 0 1.5708    - 90° yaw")
        print("  3.14159 0 0   - 180° roll (upside down)")
        return 0
    except Exception as e:
        print(f"Error fixing orientation: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())