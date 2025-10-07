#!/usr/bin/env python3
"""
Enhanced Nature Features Module
Adds support for benches, trees, and woods/forests in OSM to Gazebo conversion

This module extends the OSM to Gazebo conversion process to better detect and render:
- Benches (amenity=bench)
- Individual trees (natural=tree)
- Woods/Forests (natural=wood or landuse=forest)
"""

import os
import sys
from pathlib import Path
import xml.etree.ElementTree as ET
import subprocess
import tempfile

try:
    from utils import print_info, print_success, print_warn, print_error
except ImportError:
    from colorama import Fore, Style, init as colorama_init
    colorama_init(autoreset=True)
    
    def print_info(message: str) -> None:
        print(f"{Fore.BLUE}[INFO]{Style.RESET_ALL} {message}")
        
    def print_success(message: str) -> None:
        print(f"{Fore.GREEN}[OK]{Style.RESET_ALL} {message}")
        
    def print_warn(message: str) -> None:
        print(f"{Fore.YELLOW}[WARN]{Style.RESET_ALL} {message}")
        
    def print_error(message: str) -> None:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {message}", file=sys.stderr)

class NatureFeaturesEnhancer:
    """Class to enhance OSM to Gazebo conversion with better nature feature support"""
    
    # Model paths and settings using available models
    BENCH_MODEL = "model://FoodCourtBenchLong"
    TREE_MODEL_DECIDUOUS = "model://Tree"
    TREE_MODEL_CONIFEROUS = "model://PineTree"
    
    def __init__(self, osm_file, world_file, scale=1.0):
        """Initialize with input OSM file and output world file paths"""
        self.osm_file = Path(osm_file)
        self.world_file = Path(world_file)
        self.scale = float(scale)
        self.bench_count = 0
        self.tree_count = 0
        self.wood_area = 0
        
        # Create directory for models if needed
        models_dir = Path(os.path.dirname(self.world_file)) / "models"
        models_dir.mkdir(exist_ok=True)
        
        self.models_dir = models_dir
        
    def extract_features(self):
        """Extract nature features from OSM file"""
        try:
            tree = ET.parse(self.osm_file)
            root = tree.getroot()
            
            benches = []
            individual_trees = []
            woods = []
            
            print_info("Scanning OSM file for nature features...")
            
            # Extract nodes with amenity=bench
            for node in root.findall(".//node"):
                has_bench = False
                has_tree = False
                lat = float(node.get('lat', 0))
                lon = float(node.get('lon', 0))
                
                for tag in node.findall('./tag'):
                    k = tag.get('k')
                    v = tag.get('v')
                    
                    if k == 'amenity' and v == 'bench':
                        has_bench = True
                    elif k == 'natural' and v == 'tree':
                        has_tree = True
                    
                if has_bench:
                    benches.append({'lat': lat, 'lon': lon})
                    
                if has_tree:
                    tree_type = 'deciduous'  # Default
                    height = 5.0  # Default height
                    
                    # Check for specific tree attributes
                    for tag in node.findall('./tag'):
                        if tag.get('k') == 'leaf_type' and tag.get('v') == 'needleleaved':
                            tree_type = 'coniferous'
                        elif tag.get('k') == 'height':
                            try:
                                height = float(tag.get('v', 5.0))
                            except ValueError:
                                height = 5.0
                                
                    individual_trees.append({
                        'lat': lat, 
                        'lon': lon, 
                        'type': tree_type,
                        'height': height
                    })
            
            # Extract woods/forest areas (simplified - just getting ways)
            for way in root.findall(".//way"):
                is_wood = False
                wood_type = 'mixed'  # Default
                
                for tag in way.findall('./tag'):
                    k = tag.get('k')
                    v = tag.get('v')
                    
                    if (k == 'natural' and v == 'wood') or (k == 'landuse' and v == 'forest'):
                        is_wood = True
                    
                    if k == 'wood' or k == 'leaf_type':
                        if v in ['deciduous', 'broadleaved']:
                            wood_type = 'deciduous'
                        elif v in ['coniferous', 'needleleaved']:
                            wood_type = 'coniferous'
                        elif v == 'mixed':
                            wood_type = 'mixed'
                
                if is_wood:
                    # Get nodes that form the wood polygon
                    nodes = []
                    for nd in way.findall('./nd'):
                        ref = nd.get('ref')
                        node = root.find(f".//node[@id='{ref}']")
                        if node is not None:
                            lat = float(node.get('lat', 0))
                            lon = float(node.get('lon', 0))
                            nodes.append((lat, lon))
                    
                    # Calculate approximate area (simplified)
                    # This is just a rough estimate for display purposes
                    if len(nodes) > 2:
                        area = self._calculate_polygon_area(nodes)
                        woods.append({
                            'nodes': nodes,
                            'type': wood_type,
                            'area': area
                        })
            
            self.bench_count = len(benches)
            self.tree_count = len(individual_trees)
            self.wood_area = sum(w['area'] for w in woods)
            
            print_success(f"Found {self.bench_count} benches, {self.tree_count} individual trees, " 
                        f"and {len(woods)} wooded areas ({self.wood_area:.1f} m²)")
            
            return {
                'benches': benches,
                'trees': individual_trees,
                'woods': woods
            }
            
        except Exception as e:
            print_error(f"Failed to extract features: {str(e)}")
            return {'benches': [], 'trees': [], 'woods': []}
    
    def _calculate_polygon_area(self, coords):
        """Calculate area of polygon using simplified formula"""
        n = len(coords)
        if n < 3:
            return 0
            
        # Convert lat/lon to approximate meters using simple scaling
        # This is just a rough approximation for display purposes
        # For more accurate calculations, proper geo libraries should be used
        earth_radius = 6371000  # meters
        coords_meters = []
        
        # Convert to flat X,Y approximation
        # This is simplified and would only be reasonable for small areas
        for lat, lon in coords:
            x = lon * earth_radius * 0.0174533 * self.scale  # pi/180
            y = lat * earth_radius * 0.0174533 * self.scale
            coords_meters.append((x, y))
            
        # Calculate area using Shoelace formula
        area = 0
        for i in range(n):
            j = (i + 1) % n
            area += coords_meters[i][0] * coords_meters[j][1]
            area -= coords_meters[j][0] * coords_meters[i][1]
        
        area = abs(area) / 2.0
        return area
    
    def enhance_world_file(self):
        """Enhance the Gazebo world file with nature features"""
        if not os.path.exists(self.world_file):
            print_error(f"World file not found: {self.world_file}")
            return False
            
        # Extract features from OSM file
        features = self.extract_features()
        
        if sum(len(features[k]) for k in features) == 0:
            print_warn("No nature features found to add")
            return False
            
        try:
            # Read the world file
            with open(self.world_file, 'r') as f:
                world_content = f.read()
                
            # Parse to find where to insert new elements
            import re
            
            # Find position to insert (before the closing world tag)
            insert_position = world_content.rfind("</world>")
            if insert_position == -1:
                print_error("Could not find </world> tag in world file")
                return False
                
            # Create the new content to insert
            new_content = self._generate_gazebo_models(features)
            
            # Insert the new content
            updated_content = (
                world_content[:insert_position] + 
                "\n<!-- Enhanced nature features -->\n" + 
                new_content +
                world_content[insert_position:]
            )
            
            # Create backup
            backup_file = str(self.world_file) + ".bak"
            with open(backup_file, 'w') as f:
                f.write(world_content)
                
            # Write updated world file
            with open(self.world_file, 'w') as f:
                f.write(updated_content)
                
            print_success(f"Enhanced world file with nature features (backup saved as {backup_file})")
            return True
            
        except Exception as e:
            print_error(f"Failed to enhance world file: {str(e)}")
            return False
    
    def _generate_gazebo_models(self, features):
        """Generate Gazebo model entries for detected features"""
        content = []
        
        # Add benches
        for i, bench in enumerate(features['benches']):
            # Convert lat/lon to x,y
            x, y = self._latlon_to_xy(bench['lat'], bench['lon'])
            model_name = f"bench_{i+1}"
            
            content.append(f"""
  <model name="{model_name}">
    <include>
      <uri>{self.BENCH_MODEL}</uri>
      <pose>{x} {y} 0 0 0 0</pose>
    </include>
    <static>true</static>
  </model>""")
        
        # Add individual trees
        for i, tree in enumerate(features['trees']):
            x, y = self._latlon_to_xy(tree['lat'], tree['lon'])
            model_name = f"tree_{i+1}"
            model_uri = self.TREE_MODEL_DECIDUOUS if tree['type'] == 'deciduous' else self.TREE_MODEL_CONIFEROUS
            scale = tree['height'] / 5.0  # Scale based on height, assuming default is 5m
            
            content.append(f"""
  <model name="{model_name}">
    <include>
      <uri>{model_uri}</uri>
      <pose>{x} {y} 0 0 0 0</pose>
      <scale>{scale} {scale} {scale}</scale>
    </include>
    <static>true</static>
  </model>""")
        
        # For woods, we add a marker for visualization
        for i, wood in enumerate(features['woods']):
            # Use centroid of wood area
            centroid_lat = sum(n[0] for n in wood['nodes']) / len(wood['nodes'])
            centroid_lon = sum(n[1] for n in wood['nodes']) / len(wood['nodes'])
            x, y = self._latlon_to_xy(centroid_lat, centroid_lon)
            model_name = f"wood_{i+1}"
            
            # For large woods, add multiple trees instead of one marker
            if wood['area'] > 5000:  # For large areas
                # Add a "forest" indicator - a group of trees
                tree_content = []
                max_trees = min(20, int(wood['area'] / 500))  # Limit max trees
                
                for j in range(max_trees):
                    # Place trees in a grid around the centroid
                    grid_size = int(max_trees ** 0.5)
                    row = j // grid_size
                    col = j % grid_size
                    
                    offset_x = (row - grid_size/2) * 10
                    offset_y = (col - grid_size/2) * 10
                    
                    # Randomize position a bit
                    import random
                    rand_x = random.uniform(-5, 5)
                    rand_y = random.uniform(-5, 5)
                    
                    tree_x = x + offset_x + rand_x
                    tree_y = y + offset_y + rand_y
                    
                    # Decide tree type
                    if wood['type'] == 'mixed':
                        tree_type = 'deciduous' if j % 2 == 0 else 'coniferous'
                    else:
                        tree_type = wood['type']
                        
                    model_uri = self.TREE_MODEL_DECIDUOUS if tree_type == 'deciduous' else self.TREE_MODEL_CONIFEROUS
                    
                    # Randomize size
                    scale = random.uniform(0.8, 1.3)
                    
                    tree_content.append(f"""
    <model name="tree_{model_name}_{j+1}">
      <include>
        <uri>{model_uri}</uri>
        <pose>{tree_x} {tree_y} 0 0 0 0</pose>
        <scale>{scale} {scale} {scale}</scale>
      </include>
      <static>true</static>
    </model>""")
                
                # Add all trees as a single content block
                content.append("\n".join(tree_content))
            else:
                # For small woods, just add a single representative tree
                model_uri = self.TREE_MODEL_DECIDUOUS if wood['type'] in ['deciduous', 'mixed'] else self.TREE_MODEL_CONIFEROUS
                scale = min(2.0, max(1.0, wood['area'] / 1000))
                
                content.append(f"""
  <model name="{model_name}">
    <include>
      <uri>{model_uri}</uri>
      <pose>{x} {y} 0 0 0 0</pose>
      <scale>{scale} {scale} {scale}</scale>
    </include>
    <static>true</static>
  </model>""")
        
        return "\n".join(content)
    
    def _latlon_to_xy(self, lat, lon):
        """Convert latitude/longitude to x,y coordinates (simple approximation)"""
        # This is a very simplified conversion that works for small areas
        # For a real implementation, proper geo libraries should be used
        # and the conversion should account for the origin of the map
        
        # Get reference point (first node in OSM file)
        try:
            tree = ET.parse(self.osm_file)
            root = tree.getroot()
            first_node = root.find(".//node")
            
            if first_node is not None:
                ref_lat = float(first_node.get('lat', 0))
                ref_lon = float(first_node.get('lon', 0))
            else:
                ref_lat = lat
                ref_lon = lon
                
            # Convert to meters using simple approximation
            earth_radius = 6371000  # meters
            lat_rad = lat * 0.0174533  # deg to rad
            ref_lat_rad = ref_lat * 0.0174533
            
            x = earth_radius * (lon - ref_lon) * 0.0174533 * self.scale * math.cos(lat_rad)
            y = earth_radius * (lat - ref_lat) * 0.0174533 * self.scale
            
            return x, y
            
        except Exception as e:
            print_error(f"Error converting lat/lon to xy: {str(e)}")
            return 0, 0


def enhance_world_with_nature_features(osm_file, world_file, scale=1.0):
    """Add nature features (benches, trees, woods) to a Gazebo world file based on OSM data"""
    enhancer = NatureFeaturesEnhancer(osm_file, world_file, scale)
    return enhancer.enhance_world_file()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhance Gazebo world with nature features from OSM")
    parser.add_argument("osm_file", help="Path to input OSM file")
    parser.add_argument("world_file", help="Path to Gazebo world file to enhance")
    parser.add_argument("--scale", type=float, default=1.0, help="Scale factor for the map")
    
    args = parser.parse_args()
    
    # Import math here to avoid global import (needed for coordinate conversion)
    import math
    
    enhance_world_with_nature_features(args.osm_file, args.world_file, args.scale)