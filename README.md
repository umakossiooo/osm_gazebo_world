# OSM to Gazebo World Converter 🏙️

**Convert real-world OpenStreetMap data into 3D Gazebo simulation environments in minutes.**

Perfect for robotics research, autonomous vehicle testing, and urban simulation with realistic buildings, roads, and physics.

## 🚀 Quick Start

```bash
# 1. Setup (one time)
git clone https://github.com/umakossiooo/osm_gazebo_world.git
cd osm_gazebo_world && docker-compose build

# 2. Convert OSM → Gazebo  
docker-compose run --rm osm2gazebo \
  python convert_osm_to_gazebo.py maps/map.osm maps/rome.world --auto-optimize

# 3. Launch 3D simulation
export GAZEBO_MODEL_PATH=$PWD/maps:$GAZEBO_MODEL_PATH
gz sim maps/rome_optimized.world
```

**Done!** 🎉 Real-world 3D environment from map data.

📚 **[→ Detailed Setup Guide](QUICK_START.md)**

## � Getting Your Own Map Data

1. **Download from OpenStreetMap**: Go to [openstreetmap.org](https://www.openstreetmap.org) → Export → Select area → Export
2. **Use included samples**: Rome area included in `maps/map.osm` for testing

## ⚙️ Advanced Usage

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

## ❓ Common Issues

**Problem: Gazebo crashes or mesh errors?**  
→ Use `--auto-optimize` flag or run `./optimize_complete.py maps/your_world.world`

**Problem: Map appears vertical?**  
→ Fixed automatically with `--auto-optimize` or use `./fix_orientation.py`

**Problem: Docker build fails?**  
→ Increase Docker memory to 4GB+ and run `docker-compose build --no-cache`

📖 **[Full troubleshooting guide](TROUBLESHOOTING.md)**

## 📋 What You Get

- 🏢 **Realistic buildings** with textures and materials
- 🛣️ **Detailed roads** with proper markings  
- 🚦 **Traffic infrastructure** and signage
- 🌳 **Vegetation** and green spaces
- ⚡ **Physics simulation** ready for robots and vehicles

## 🔗 Links

- 📖 **[Detailed Documentation](USAGE.md)**
- 🐛 **[Troubleshooting Guide](TROUBLESHOOTING.md)**
- 🌍 **[Get OSM Data](https://www.openstreetmap.org)**
- 🤖 **[Gazebo Documentation](https://gazebosim.org)**

---
*Converts real-world map data into 3D simulation environments. Perfect for autonomous vehicle testing and robotics research.*


