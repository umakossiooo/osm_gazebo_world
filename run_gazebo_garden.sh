#!/usr/bin/env bash
# Run a simulation with Gazebo Garden

set -e

# Color output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Check if world file is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <world_file> [additional_gazebo_args]"
    echo
    echo "Available world files:"
    find maps/ -name "*.world" -type f | sort
    echo
    echo "Example: $0 maps/map_optimized.world"
    exit 1
fi

WORLD_FILE="$1"
shift  # Remove first argument so $@ contains remaining args

# Check if world file exists
if [ ! -f "$WORLD_FILE" ]; then
    print_error "World file not found: $WORLD_FILE"
    exit 1
fi

print_info "World file: $WORLD_FILE"

# Set environment variables for better compatibility
export GAZEBO_MODEL_PATH="$PWD/maps:$GAZEBO_MODEL_PATH"
export GZ_SIM_RESOURCE_PATH="$PWD/maps:$GZ_SIM_RESOURCE_PATH"

print_info "Environment configured:"
print_info "  GAZEBO_MODEL_PATH: $GAZEBO_MODEL_PATH"
print_info "  GZ_SIM_RESOURCE_PATH: $GZ_SIM_RESOURCE_PATH"

# Check if Gazebo Garden is available
if ! command -v gz >/dev/null 2>&1; then
    print_error "Gazebo Garden not found. Please install it first."
    exit 1
fi

print_info "Launching Gazebo Garden with $WORLD_FILE $*"
exec gz sim "$WORLD_FILE" "$@"