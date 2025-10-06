# OSM to Gazebo World Converter 🏙️

Convert OpenStreetMap (OSM) data into realistic 3D Gazebo simulation worlds with buildings, roads, and textures. Perfect for robotics research, autonomous vehicle testing, and urban simulation.

## ✨ Features

- 🌍 **Real-world environments**: Convert any OSM area into a Gazebo world
- 🏗️ **Realistic rendering**: Includes textures for buildings, roads, and surfaces  
- 🚦 **Traffic signs**: German and Polish traffic sign support
- 🐳 **Docker-based**: Fully containerized, no complex setup required
- 🔧 **Customizable**: Adjustable scale, multiple output formats
- 🎯 **Production-ready**: Built-in physics, lighting, and collision detection

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Gazebo (for viewing the generated worlds)

### 1. Clone and Build

```bash
git clone https://github.com/umakossiooo/osm_gazebo_world.git
cd osm_gazebo_world
docker-compose build
```

### 2. Get OSM Data

**Option A: Download from OpenStreetMap**
1. Go to [openstreetmap.org](https://www.openstreetmap.org)
2. Navigate to your area of interest
3. Click "Export" → "Manually select a different area"
4. Select your area and click "Export"
5. Save as `maps/my_area.osm`

**Option B: Use the included Rome sample**
```bash
# A sample Rome area is included for testing
ls maps/map.osm
```

### 3. Convert to Gazebo World
```bash
# Basic conversion
docker-compose run --rm osm2gazebo \
  python convert_osm_to_gazebo.py maps/my_area.osm maps/my_area.world

# With custom scaling (0.5 = half size)
docker-compose run --rm osm2gazebo \
  python convert_osm_to_gazebo.py maps/my_area.osm maps/my_area.world --scale 0.5
```

**Generated files:**
- `maps/my_area.world` - Gazebo world file
- `maps/meshes/my_area.obj` - 3D mesh with textures

### 4. Launch in Gazebo

**Option A: Using the safe launch script (recommended):**
```bash
# Use the optimized world files to prevent crashes
./launch_gazebo.sh maps/my_area_optimized.world
```

**Option B: Direct Gazebo commands:**
```bash
# Gazebo Harmonic (gz sim) - CONFIRMED WORKING
export GAZEBO_MODEL_PATH=$PWD/maps:$GAZEBO_MODEL_PATH
gz sim maps/my_area_optimized.world --verbose

# Gazebo Classic 
gazebo maps/my_area_optimized.world
```

**Notes:** 
- Use the `_optimized.world` files to prevent mesh normal errors and crashes
- Some XML warnings are normal and don't affect functionality
- Missing .mtl material files are handled automatically by Gazebo

## 📋 Example Workflow

```bash
# 1. Clone the repository
git clone https://github.com/umakossiooo/osm_gazebo_world.git
cd osm_gazebo_world

# 2. Build the Docker image
docker-compose build

# 3. Test with included Rome sample
docker-compose run --rm osm2gazebo \
  python convert_osm_to_gazebo.py maps/map.osm maps/rome.world

# 4. Launch in Gazebo (CONFIRMED WORKING)
export GAZEBO_MODEL_PATH=$PWD/maps:$GAZEBO_MODEL_PATH
gz sim maps/rome_optimized.world
```

## 🛠️ How it Works

1. **OSM2World** converts OpenStreetMap data into a detailed 3D mesh (.obj format)
2. **Texture mapping** applies realistic materials (brick, asphalt, concrete, etc.)
3. **World generation** creates a complete Gazebo SDF world with:
   - Physics simulation
   - Realistic lighting
   - Ground plane
   - Collision detection
   - Static 3D environment

## 🎨 What You Get

Your generated Gazebo world includes:

- **🏢 Realistic buildings** with proper textures and materials
- **🛣️ Detailed roads** with markings and realistic asphalt
- **🚦 Traffic infrastructure** with localized signage (DE/PL)
- **🌳 Vegetation** including trees and green spaces
- **⚡ Physics simulation** ready for robots and vehicles
- **💡 Proper lighting** and environmental setup

## 📊 Configuration Options

```bash
# View all available options
docker-compose run --rm osm2gazebo python convert_osm_to_gazebo.py --help

# Common usage patterns
docker-compose run --rm osm2gazebo python convert_osm_to_gazebo.py \
  maps/input.osm maps/output.world --scale 1.0
```

## ⚠️ Important Notes

- **Area size**: Start with small areas (< 1km²) for testing
- **Memory usage**: Large OSM files require more RAM during conversion
- **Processing time**: Complex areas may take several minutes to process
- **File sizes**: Generated mesh files can be large (50-200MB for city areas)

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| **"normal count [0] that matches vertex count" errors** | Use `_optimized.world` files or run `./fix_mesh_normals.py` on OBJ files |
| **Gazebo segmentation fault crashes** | Use `./launch_gazebo.sh` script and `_optimized.world` files |
| **Java errors during build** | Ensure Docker has sufficient memory (4GB+) |
| **"OSM2World.jar not found"** | Rebuild the Docker image: `docker-compose build --no-cache` |
| **Conversion fails** | Try a smaller OSM area or validate your .osm file |
| **Large memory usage** | Increase Docker memory limit or use smaller extracts |
| **Missing textures in Gazebo** | Ensure you're using the latest Docker image with textures |
| **Software rendering warnings** | Set `export LIBGL_ALWAYS_SOFTWARE=1` before launching |

### 🔧 Additional Tools

This repository includes helper scripts to fix common issues:

```bash
# Fix mesh normal issues (prevents DART physics errors)
./fix_mesh_normals.py maps/meshes/my_area.obj -o maps/meshes/my_area_fixed.obj

# Optimize world files for better performance
./optimize_world.py maps/my_area.world -o maps/my_area_optimized.world

# Safe launch with proper environment setup
./launch_gazebo.sh maps/my_area_optimized.world
```

## 🤝 Contributing

Pull requests welcome! Please ensure:
- Docker builds successfully
- Include sample .osm files for testing
- Update documentation for new features

## 📄 License

This project packages OSM2World and other open-source tools. Check individual component licenses.

## 🔗 Useful Links

- [OpenStreetMap](https://www.openstreetmap.org) - Download OSM data
- [OSM2World](http://osm2world.org) - The 3D conversion engine  
- [Gazebo](https://gazebosim.org) - Robotics simulation platform


