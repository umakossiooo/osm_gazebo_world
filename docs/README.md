# OSM to Gazebo World Converter

**Convert real-world OpenStreetMap data into 3D Gazebo simulation environments for robotics research and autonomous vehicle testing.**

## Quick Start

```bash
# 1. Setup (one time)
git clone https://github.com/umakossiooo/osm_gazebo_world.git
cd osm_gazebo_world && docker-compose build

# 2. Convert OSM → Gazebo  
docker-compose run --rm osm2gazebo \
  python convert_osm_to_gazebo.py maps/map.osm maps/output.world --auto-optimize

# 3. Launch 3D simulation with Gazebo Garden
export GAZEBO_MODEL_PATH=$PWD/maps:$GAZEBO_MODEL_PATH
gz sim maps/output_optimized.world
```

## Getting Your Own Map Data

1. **Download from OpenStreetMap**: Go to [openstreetmap.org](https://www.openstreetmap.org) → Export → Select area → Export
2. **Use included samples**: Sample maps are included in the `maps` directory

## Advanced Usage

```bash
# Custom scaling (0.5 = half size) 
--scale 0.5

# Auto-optimize (recommended for large maps)
--auto-optimize

# Auto-launch after conversion
--auto-optimize --launch

# Fix existing worlds
./optimize_complete.py maps/my_area.world
```

## Common Issues & Troubleshooting

### Mesh Errors
If you see errors like: `One of the submeshes does not have a normal count [0] that matches its vertex count`
→ Use `--auto-optimize` flag or run `./optimize_complete.py maps/your_world.world`

### Map Appears Vertical
→ Fixed automatically with `--auto-optimize` or use `./fix_orientation.py`

### Docker Build Issues
→ Increase Docker memory to 4GB+ and run `docker-compose build --no-cache`

## Working Commands

For Gazebo Garden:
```bash
# Set environment variables
export GAZEBO_MODEL_PATH=$PWD/maps:$GAZEBO_MODEL_PATH

# Run simulation
gz sim maps/your_map_optimized.world --verbose
```

## Features

- 🏢 **Realistic buildings** with textures
- 🛣️ **Detailed roads** with markings  
- 🚦 **Traffic infrastructure** and signage
- 🌳 **Vegetation** and green spaces
- ⚡ **Physics simulation** ready for robots

---
*Project optimized for Gazebo Garden (Gazebo Sim) usage.*