#!/bin/bash
# Simple conversion script using Docker - no menus, just direct conversion

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Display help if needed
if [ $# -lt 1 ] || [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
  echo "Usage: $0 <osm_file> [scale] [--simple]"
  echo "Example: $0 maps/roma/map.osm 0.5"
  echo "  <osm_file>: Path to the OSM file to convert"
  echo "  [scale]: Optional scale factor (default: 1.0)"
  echo "  [--simple]: Use simple mode with fewer details (for complex OSM files with geometry issues)"
  exit 1
fi

# Input arguments
OSM_FILE="$1"
SCALE="${2:-1.0}"

# Check for --simple flag
SIMPLE_FLAG=""
if [[ "$*" == *"--simple"* ]]; then
  SIMPLE_FLAG="--simple"
  echo -e "${YELLOW}Using simple mode with fewer details${NC}"
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
    echo -e "${YELLOW}Tip: OSM files should be in the 'maps/' directory.${NC}"
    echo -e "${YELLOW}Example: maps/roma/map.osm${NC}"
    exit 1
  fi
fi

echo -e "${BLUE}Converting $OSM_FILE (scale: $SCALE)${NC}"

# Convert absolute paths to paths relative to the repository root
# This helps with Docker volume mounts
REL_OSM_FILE=$(realpath --relative-to=$(pwd) "$OSM_FILE")

# Run Docker for conversion
docker-compose run --rm \
  -e JAVA_TOOL_OPTIONS="-Djava.awt.headless=true -Xmx2g -Dorg.osm2world.skipNonCriticalExceptions=true -Dorg.osm2world.faultTolerance=true" \
  osm2gazebo ./osm_to_gazebo.py "$REL_OSM_FILE" --scale "$SCALE" $SIMPLE_FLAG

# Check if conversion was successful
if [ $? -eq 0 ]; then
  echo -e "${GREEN}Conversion complete!${NC}"
  
  # Get the output paths
  BASE_DIR=$(dirname "$OSM_FILE")
  FILENAME=$(basename "$OSM_FILE" .osm)
  
  # Check both possible locations for the world file
  WORLD_FILE="$BASE_DIR/${FILENAME}_optimized.world"
  MAP_DIR_WORLD="maps/map/map_optimized.world"
  
  if [ -f "$WORLD_FILE" ]; then
    echo -e "${BLUE}World file created at: $WORLD_FILE${NC}"
  elif [ -f "$MAP_DIR_WORLD" ]; then
    echo -e "${YELLOW}Note: World file created at $MAP_DIR_WORLD instead of expected $WORLD_FILE${NC}"
    # Create symlink to make it consistent
    ln -sf "$(realpath "$MAP_DIR_WORLD")" "$WORLD_FILE"
    echo -e "${GREEN}Created symlink from $MAP_DIR_WORLD to $WORLD_FILE${NC}"
  else
    echo -e "${RED}Warning: World file not found at expected locations${NC}"
    # Try to find it anywhere
    FOUND_WORLD=$(find maps -name "*_optimized.world" -type f -newer "$OSM_FILE" | head -1)
    if [ -n "$FOUND_WORLD" ]; then
      echo -e "${YELLOW}Found world file at: $FOUND_WORLD${NC}"
      # Create symlink to make it consistent
      ln -sf "$(realpath "$FOUND_WORLD")" "$WORLD_FILE"
      echo -e "${GREEN}Created symlink from $FOUND_WORLD to $WORLD_FILE${NC}"
    fi
  fi
  
  echo -e "${BLUE}To launch the world:${NC}"
  echo "  ./launch.sh $WORLD_FILE"
else
  echo -e "${RED}Conversion failed!${NC}"
  exit 1
fi