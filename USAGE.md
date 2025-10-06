# Detailed Usage Guide

## Prerequisites

- **Docker and Docker Compose** - For running the conversion tools
- **Gazebo** - For viewing and simulating the generated worlds
  - Gazebo Harmonic/Garden (recommended): `gz sim`
  - Gazebo Classic: `gazebo`

## Complete Workflow

### 1. Setup

```bash
git clone https://github.com/umakossiooo/osm_gazebo_world.git
cd osm_gazebo_world
docker-compose build
```

### 2. Get OSM Data

#### Option A: Download from OpenStreetMap
1. Go to [openstreetmap.org](https://www.openstreetmap.org)
2. Navigate to your area of interest
3. Click "Export" → "Manually select a different area"
4. Select your area (keep it small for testing, < 1km²)
5. Click "Export" and save as `maps/my_area.osm`

#### Option B: Use Included Sample
```bash
# Rome area sample is included
ls maps/map.osm
```

### 3. Conversion Options

#### Basic Conversion
```bash
docker-compose run --rm osm2gazebo \
  python convert_osm_to_gazebo.py maps/my_area.osm maps/my_area.world
```

#### Recommended: Auto-Optimized Conversion
```bash
# This fixes all common issues automatically
docker-compose run --rm osm2gazebo \
  python convert_osm_to_gazebo.py maps/my_area.osm maps/my_area.world --auto-optimize
```

#### Advanced Options
```bash
# Custom scaling (useful for large areas)
docker-compose run --rm osm2gazebo \
  python convert_osm_to_gazebo.py maps/my_area.osm maps/my_area.world --scale 0.5 --auto-optimize

# Auto-launch after conversion (Linux/WSL only)
docker-compose run --rm osm2gazebo \
  python convert_osm_to_gazebo.py maps/my_area.osm maps/my_area.world --auto-optimize --launch
```

### 4. Generated Files

After conversion, you'll have:
```
maps/
├── my_area.world              # Basic world file
├── my_area_optimized.world    # Performance-optimized version (use this!)
└── meshes/
    ├── my_area.obj            # Original mesh
    └── my_area_fixed.obj      # Mesh with proper normals (used by optimized world)
```

### 5. Launch Options

#### Option A: Direct Launch (Recommended)
```bash
# Set up environment
export GAZEBO_MODEL_PATH=$PWD/maps:$GAZEBO_MODEL_PATH

# Launch Gazebo Harmonic/Garden
gz sim maps/my_area_optimized.world --verbose

# OR launch Gazebo Classic
gazebo maps/my_area_optimized.world
```

#### Option B: Safe Launch Script
```bash
# Uses automatic environment setup and error checking
./launch_gazebo.sh maps/my_area_optimized.world
```

## Optimization Tools

### Complete Auto-Optimization
```bash
# Fixes everything automatically: normals, performance, orientation
./optimize_complete.py maps/my_area.world

# Auto-optimize and launch
./optimize_complete.py maps/my_area.world --launch
```

### Individual Tools
```bash
# Fix mesh normals (prevents physics errors)
./fix_mesh_normals.py maps/meshes/my_area.obj -o maps/meshes/my_area_fixed.obj

# Optimize world performance settings
./optimize_world.py maps/my_area.world -o maps/my_area_optimized.world

# Fix mesh orientation (if appears vertical)
./fix_orientation.py maps/my_area.world

# Safe environment setup and launch
./launch_gazebo.sh maps/my_area_optimized.world
```

## Configuration Options

### Scaling
```bash
--scale 0.5    # Half size (useful for large areas)
--scale 2.0    # Double size (useful for detailed small areas)
```

### Auto-Optimization
```bash
--auto-optimize    # Automatically fix all common issues
--launch          # Auto-launch Gazebo after conversion (requires --auto-optimize)
```

### View All Options
```bash
docker-compose run --rm osm2gazebo python convert_osm_to_gazebo.py --help
```

## Performance Considerations

### Area Size Recommendations
- **Testing**: < 0.5km² (small neighborhood)
- **Development**: 0.5-1km² (several blocks)
- **Production**: 1-2km² (small district)
- **Large areas**: > 2km² (requires powerful hardware, consider splitting)

### Memory Requirements
- **Small areas** (< 0.5km²): 4GB RAM
- **Medium areas** (0.5-1km²): 8GB RAM  
- **Large areas** (1-2km²): 16GB+ RAM
- **Docker**: Increase Docker memory limit if needed

### Processing Time
- **Simple areas**: 1-5 minutes
- **Complex urban areas**: 5-15 minutes
- **Large detailed areas**: 15+ minutes

### File Sizes
- **Original mesh**: 50-200MB for city areas
- **Fixed mesh**: 1.5x larger (includes normals)
- **World files**: 1-10KB

## How It Works

1. **OSM2World** converts OpenStreetMap vector data into detailed 3D meshes
2. **Texture mapping** applies realistic materials (brick, asphalt, concrete, vegetation)
3. **Normal calculation** adds vertex normals for proper lighting and physics
4. **Performance optimization** adjusts physics settings for large meshes
5. **Orientation fixing** ensures meshes appear horizontal in Gazebo
6. **World generation** creates complete SDF world with physics, lighting, and environment

## Generated World Features

Your Gazebo world includes:

### Environmental Elements
- **Realistic buildings** with proper textures and materials
- **Detailed road networks** with markings and surfaces
- **Traffic infrastructure** (signs, lights) with German/Polish localization
- **Green spaces** with vegetation and trees
- **Water features** (rivers, fountains) where present in OSM data

### Technical Features
- **Physics simulation** with collision detection
- **Proper lighting** (sun, ambient, shadows)
- **Ground plane** for robot navigation
- **Static environment** (optimized for performance)
- **Material definitions** for realistic appearance

### Coordinate System
- **Origin**: Center of the OSM bounding box
- **Units**: Meters (real-world scale)
- **Orientation**: North = +Y axis, East = +X axis, Up = +Z axis