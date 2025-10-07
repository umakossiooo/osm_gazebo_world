#!/usr/bin/env python3
"""
Clean OpenStreetMap data using GDAL/OGR to fix geometry issues.
This script helps resolve common OSM geometry problems before conversion to 3D.
"""

import argparse
import os
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
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


def check_gdal_installed() -> bool:
    """Check if GDAL/OGR is installed and available."""
    try:
        subprocess.run(["ogr2ogr", "--version"], 
                       stdout=subprocess.PIPE, 
                       stderr=subprocess.PIPE, 
                       check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def clean_osm_with_ogr(input_osm: Path, output_osm: Path) -> bool:
    """Use OGR to clean OSM geometries by converting to GeoJSON and back."""
    print_info(f"Cleaning OSM data using GDAL/OGR: {input_osm}")
    
    # Create a temporary directory for processing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Convert OSM to GeoJSON for easier processing
        geojson_path = Path(temp_dir) / "data.geojson"
        
        try:
            print_info("Converting OSM to GeoJSON...")
            subprocess.run([
                "ogr2ogr", 
                "-f", "GeoJSON",
                "-skipfailures",
                geojson_path,
                input_osm
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Convert back to OSM with fixes
            print_info("Converting GeoJSON back to OSM with fixes...")
            subprocess.run([
                "ogr2ogr",
                "-f", "OSM",
                "-skipfailures",
                output_osm,
                geojson_path
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            print_success(f"Basic geometry cleaning completed")
            return True
            
        except subprocess.CalledProcessError as e:
            print_error(f"GDAL/OGR processing failed: {e}")
            if e.stderr:
                print_error(f"Error output: {e.stderr.decode('utf-8', errors='ignore')}")
            return False
        except Exception as e:
            print_error(f"Unexpected error during GDAL processing: {e}")
            return False


def fix_common_osm_issues(osm_file: Path) -> bool:
    """Fix common OSM issues in the XML structure that cause problems for OSM2World."""
    print_info(f"Fixing common OSM issues in: {osm_file}")
    
    try:
        tree = ET.parse(osm_file)
        root = tree.getroot()
        
        fixed_issues = {
            "unclosed_ways": 0,
            "missing_building_levels": 0
        }
        
        # Fix unclosed ways (polygon must be closed with first node)
        for way in root.findall(".//way"):
            # Check if way has a building tag
            is_building = False
            has_levels = False
            
            for tag in way.findall("tag"):
                if tag.get("k") == "building":
                    is_building = True
                if tag.get("k") == "building:levels":
                    has_levels = True
            
            # For buildings, make sure ways are closed
            if is_building:
                nodes = way.findall("nd")
                if len(nodes) >= 3:
                    first_ref = nodes[0].get("ref")
                    last_ref = nodes[-1].get("ref")
                    
                    # If way isn't closed, close it by adding the first node again
                    if first_ref != last_ref:
                        new_node = ET.Element("nd", ref=first_ref)
                        way.append(new_node)
                        fixed_issues["unclosed_ways"] += 1
                
                # Add default building:levels=1 if missing
                if is_building and not has_levels:
                    new_tag = ET.Element("tag", k="building:levels", v="1")
                    way.append(new_tag)
                    fixed_issues["missing_building_levels"] += 1
        
        # Write the fixed OSM file
        tree.write(osm_file)
        
        print_success(f"Fixed {fixed_issues['unclosed_ways']} unclosed ways")
        print_success(f"Added {fixed_issues['missing_building_levels']} missing building:levels tags")
        
        return True
        
    except Exception as e:
        print_error(f"Error fixing OSM structure: {e}")
        return False


def clean_osm_data(input_osm: Path, output_osm: Path) -> bool:
    """
    Complete OSM data cleaning pipeline using GDAL/OGR and XML fixes.
    
    Steps:
    1. Use GDAL/OGR to fix geometry issues
    2. Apply common OSM fixes for OSM2World compatibility
    """
    if not input_osm.exists():
        print_error(f"Input OSM file not found: {input_osm}")
        return False
    
    # Ensure output directory exists
    output_osm.parent.mkdir(parents=True, exist_ok=True)
    
    # Check GDAL/OGR installation
    if not check_gdal_installed():
        print_error("GDAL/OGR not found. Please install gdal-bin and python3-gdal packages.")
        print_error("On Ubuntu/Debian: sudo apt-get install gdal-bin python3-gdal")
        return False
    
    # Step 1: Clean with GDAL/OGR
    if not clean_osm_with_ogr(input_osm, output_osm):
        print_error("GDAL/OGR cleaning failed. Using original OSM file.")
        # Fallback to copying the original file
        import shutil
        shutil.copy2(input_osm, output_osm)
    
    # Step 2: Fix common OSM issues
    if not fix_common_osm_issues(output_osm):
        print_warn("Failed to fix some common OSM issues. Continuing with basic cleaning.")
    
    if output_osm.exists() and output_osm.stat().st_size > 0:
        print_success(f"OSM cleaning completed: {output_osm}")
        return True
    else:
        print_error(f"Cleaning failed: Output file is missing or empty")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Clean OpenStreetMap data using GDAL/OGR to fix geometry issues"
    )
    parser.add_argument("input", help="Input OSM file path")
    parser.add_argument("output", help="Output cleaned OSM file path")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if clean_osm_data(input_path, output_path):
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())