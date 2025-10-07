#!/usr/bin/env bash
# Cleanup script to consolidate documentation and remove unnecessary files

set -e

echo "Cleaning up OSM to Gazebo World Converter project..."

# Create docs directory if it doesn't exist
mkdir -p docs

# Merge documentation
echo "Consolidating documentation..."
if [ -f README.md ]; then
    cp README.md docs/README.md
fi

# List of unnecessary files to remove
# Be careful not to delete important files
UNNECESSARY_FILES=(
    "QUICK_START.md"
    "TROUBLESHOOTING.md"
    "WORKING_COMMANDS.md"
    "USAGE.md"
    "*.log"
    "*.tmp"
)

for file in "${UNNECESSARY_FILES[@]}"; do
    find . -name "$file" -type f -print -delete
done

echo "Creating symlinks for convenience..."
ln -sf docs/README.md .

echo "Cleanup completed successfully!"