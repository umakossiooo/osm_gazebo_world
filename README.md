# OSM to Gazebo World Converter

This tool converts OpenStreetMap (.osm) files to Gazebo (.world) files, ready for simulation.

## Quick Start

```bash
# One-step command: convert OSM file and launch Gazebo
./osm2gazebo.sh maps/roma/map.osm

# For complex OSM files with geometry issues, use simple mode
./osm2gazebo.sh maps/roma/map.osm --simple

# OR use the separate commands:
# 1. Convert an OSM file to a Gazebo world
./convert.sh maps/roma/map.osm

# 2. Launch the world in Gazebo
./launch.sh maps/roma/map_optimized.world
```

## Requirements

- Docker and docker-compose
- Gazebo Garden (for visualization)

## Installation

All dependencies are handled by Docker, so you only need:

```bash
# Install Docker if needed
sudo apt update
sudo apt install -y docker.io docker-compose
```

## Usage

### 1. Preparing OSM Data

Download OSM data from [OpenStreetMap](https://www.openstreetmap.org/export) or [GEOFABRIK](https://download.geofabrik.de/):
1. Go to your area of interest
2. Export as .osm file
3. Save it to the maps/ directory

### 2. Converting OSM to Gazebo

```bash
./convert.sh maps/roma/map.osm [scale]
```

Parameters:
- `maps/roma/map.osm`: Path to the OSM file (must start with 'maps/')
- `scale` (optional): Scale factor for the model (default: 1.0)
- `--simple` (optional): Use simple mode with fewer details to avoid geometry errors in complex OSM files
- `scale`: Optional scale factor (default: 1.0)

### 3. Launching the World

```bash
./launch.sh maps/roma/map_optimized.world
```

### All-in-One Command

```bash
./osm2gazebo.sh maps/roma/map.osm
```

This will convert the OSM file and immediately launch Gazebo with the resulting world.

## Troubleshooting

**Gazebo crashes or has rendering issues:**
- The launch script automatically detects and handles software rendering.
- For large maps, try using a smaller scale factor: `./convert.sh maps/your-map.osm 0.5`

**"OSM2World.jar not found" error:**
- The Docker container has it preinstalled, so make sure you're using the convert.sh script.

**"Fuel world download failed" warnings:**
- These warnings are normal and can be ignored - the world will still load.