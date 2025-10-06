#!/bin/bash

# Launch script for Gazebo with OSM worlds
# This script sets up the environment to prevent common crashes and rendering issues

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}OSM Gazebo World Launcher${NC}"
echo "=================================="

# Function to print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if world file is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <world_file> [additional_gazebo_args]"
    echo
    echo "Available world files:"
    find maps/ -name "*.world" -type f | sort
    echo
    echo "Example: $0 maps/map_optimized.world"
    echo "Example: $0 maps/rome_optimized.world --verbose"
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
export GAZEBO_RESOURCE_PATH="$PWD/maps:$GAZEBO_RESOURCE_PATH"

# Check for GPU/graphics issues and set software rendering if needed
if [ "$LIBGL_ALWAYS_SOFTWARE" != "1" ]; then
    print_info "Testing OpenGL capabilities..."
    
    # Test if we can get GPU info
    if ! glxinfo >/dev/null 2>&1; then
        print_warn "glxinfo not available, cannot test OpenGL"
    else
        GPU_INFO=$(glxinfo | grep "OpenGL renderer" || true)
        if echo "$GPU_INFO" | grep -q "llvmpipe\|software\|swrast"; then
            print_warn "Software rendering detected: $GPU_INFO"
            print_warn "This may cause performance issues and crashes with large meshes"
            
            # Ask if user wants to continue with software rendering
            echo -n "Continue with software rendering? (y/N): "
            read -r response
            if [[ ! "$response" =~ ^[Yy]$ ]]; then
                print_info "Exiting. Consider using a machine with GPU acceleration."
                exit 1
            fi
            export LIBGL_ALWAYS_SOFTWARE=1
        else
            print_success "Hardware acceleration available: $GPU_INFO"
        fi
    fi
fi

# Additional environment variables for stability
export MESA_GL_VERSION_OVERRIDE=3.3
export MESA_GLSL_VERSION_OVERRIDE=330

# Memory and performance settings
export MALLOC_ARENA_MAX=2  # Reduce memory fragmentation

print_info "Environment configured:"
print_info "  GAZEBO_MODEL_PATH: $GAZEBO_MODEL_PATH"
print_info "  LIBGL_ALWAYS_SOFTWARE: ${LIBGL_ALWAYS_SOFTWARE:-not set}"

# Check available memory
AVAILABLE_MEM=$(free -m | awk 'NR==2{print $7}')
if [ "$AVAILABLE_MEM" -lt 2048 ]; then
    print_warn "Available memory is low ($AVAILABLE_MEM MB). Large worlds may cause crashes."
    print_warn "Consider closing other applications or using a smaller OSM area."
fi

# Launch Gazebo with the world
print_info "Launching Gazebo..."
print_info "Command: gazebo \"$WORLD_FILE\" $*"

# Use exec to replace the shell process with gazebo
exec gazebo "$WORLD_FILE" "$@"