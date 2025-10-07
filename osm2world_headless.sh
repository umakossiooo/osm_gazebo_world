#!/bin/bash
# OSM2World headless wrapper - runs OSM2World via Xvfb virtual framebuffer
# This script avoids X11 display issues with Java GUI libraries

# Check if Xvfb is installed
if ! command -v Xvfb &> /dev/null; then
    echo "Xvfb not found, will attempt to run directly with headless Java option"
    java -Djava.awt.headless=true "$@"
    exit $?
fi

# Start Xvfb with a virtual display
Xvfb :99 -screen 0 1024x768x24 -ac &
XVFB_PID=$!

# Set the display to the virtual one
export DISPLAY=:99

# Trap to make sure Xvfb is killed when the script exits
trap "kill $XVFB_PID" EXIT

# Run the Java command with all arguments passed to this script
java "$@"
exit $?