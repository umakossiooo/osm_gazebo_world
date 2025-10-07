#!/bin/bash

# OSM2Gazebo - Simple one-step conversion and launch script
# This script converts an OSM file to a Gazebo world and launches Gazebo

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Display help if needed
if [ $# -lt 1 ] || [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
  echo -e "${BLUE}OSM to Gazebo - All-in-one Tool${NC}"
  echo "========================================="
  echo -e "Usage: $0 ${GREEN}<osm_file>${NC} [scale] [--simple]"
  echo ""
  echo "Arguments:"
  echo -e "  ${GREEN}<osm_file>${NC}  Path to the OSM file to convert"
  echo -e "  ${BLUE}[scale]${NC}      Optional scale factor (default: 1.0)"
  echo -e "  ${YELLOW}[--simple]${NC}   Use simple mode with fewer details (helps with complex OSM files)"
  echo ""
  echo "Example:"
  echo -e "  $0 maps/roma/map.osm 0.5"
  echo -e "  $0 maps/roma/map.osm --simple"
  echo ""
  exit 1
fi

# Input arguments
OSM_FILE="$1"
SCALE="${2:-1.0}"

# Check for --simple flag
SIMPLE_FLAG=""
if [[ "$*" == *"--simple"* ]]; then
  SIMPLE_FLAG="--simple"
  echo -e "${YELLOW}Using simple mode with fewer details for better compatibility${NC}"
  
  # If second argument is --simple, set scale back to default
  if [ "$2" == "--simple" ]; then
    SCALE="1.0"
  fi
fi

# Check if file exists
if [ ! -f "$OSM_FILE" ]; then
  # Try to fix common path issues
  if [ -f "maps/$OSM_FILE" ]; then
    echo -e "${YELLOW}Note: Found file at maps/$OSM_FILE${NC}"
    OSM_FILE="maps/$OSM_FILE"
  elif [ -f "${OSM_FILE/map\//maps\/}" ]; then
    # Fix "map/path" to "maps/path"
    FIXED_PATH="${OSM_FILE/map\//maps\/}"
    echo -e "${YELLOW}Note: Found file at $FIXED_PATH${NC}"
    OSM_FILE="$FIXED_PATH"
  else
    echo -e "${RED}Error: OSM file not found: $OSM_FILE${NC}"
    echo -e "${YELLOW}Tip: Make sure the path is correct. OSM files should be in the 'maps/' directory.${NC}"
    echo -e "${YELLOW}Example: maps/roma/map.osm${NC}"
    exit 1
  fi
fi

# Get absolute paths
ABSOLUTE_OSM_PATH=$(realpath "$OSM_FILE")
OSM_DIR=$(dirname "$ABSOLUTE_OSM_PATH")
OSM_NAME=$(basename "$ABSOLUTE_OSM_PATH" .osm)
OUTPUT_DIR="$OSM_DIR"

# Step 1: Convert OSM to Gazebo
echo -e "${BLUE}Step 1: Converting OSM file to Gazebo world...${NC}"
./convert.sh "$ABSOLUTE_OSM_PATH" "$SCALE" $SIMPLE_FLAG

# Check if conversion was successful
if [ $? -ne 0 ]; then
  echo -e "${RED}Error: OSM to Gazebo conversion failed.${NC}"
  exit 1
fi

# Look for world files in several possible locations
echo -e "${BLUE}Looking for the generated world file...${NC}"

# Expected locations in priority order
EXPECTED_WORLD_FILE="$OSM_DIR/${OSM_NAME}_optimized.world"
MAP_DIR_WORLD="maps/map/map_optimized.world"

# Check if world file exists in expected location
if [ -f "$EXPECTED_WORLD_FILE" ]; then
  WORLD_FILE="$EXPECTED_WORLD_FILE"
  echo -e "${GREEN}Found world file at expected location: $WORLD_FILE${NC}"
elif [ -f "$MAP_DIR_WORLD" ]; then
  WORLD_FILE="$MAP_DIR_WORLD"
  echo -e "${YELLOW}Found world file in alternate location: $WORLD_FILE${NC}"
else
  # Try to find the most recently created world file
  echo -e "${YELLOW}Searching for world files...${NC}"
  WORLD_FILE=$(find maps -name "*_optimized.world" -type f | sort -t ' ' -k 1 | head -1)
  
  if [ -z "$WORLD_FILE" ]; then
    echo -e "${RED}Error: No world file found in the maps directory.${NC}"
    exit 1
  fi
  echo -e "${YELLOW}Found world file: $WORLD_FILE${NC}"
fi

# Step 2: Launch Gazebo with the world file
echo -e "${BLUE}Step 2: Launching Gazebo with the converted world...${NC}"
./launch.sh "$WORLD_FILE"

echo -e "${GREEN}All done!${NC}"