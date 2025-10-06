# 📋 Quick Reference

## ⚡ Fast Track - Get Running in 3 Commands

```bash
# 1. Setup
git clone https://github.com/umakossiooo/osm_gazebo_world.git && cd osm_gazebo_world && docker-compose build

# 2. Convert (Rome sample included)
docker-compose run --rm osm2gazebo python convert_osm_to_gazebo.py maps/map.osm maps/rome.world --auto-optimize

# 3. Launch
export GAZEBO_MODEL_PATH=$PWD/maps:$GAZEBO_MODEL_PATH && gz sim maps/rome_optimized.world
```

## 🛠️ Common Commands

| Task | Command |
|------|---------|
| **Convert OSM** | `docker-compose run --rm osm2gazebo python convert_osm_to_gazebo.py INPUT.osm OUTPUT.world --auto-optimize` |
| **Fix existing world** | `./optimize_complete.py maps/my_world.world` |
| **Launch Gazebo** | `export GAZEBO_MODEL_PATH=$PWD/maps:$GAZEBO_MODEL_PATH && gz sim maps/my_world_optimized.world` |
| **Safe launch** | `./launch_gazebo.sh maps/my_world_optimized.world` |

## 🐛 Quick Fixes

| Problem | Solution |
|---------|----------|
| 💥 **Gazebo crashes** | Use `--auto-optimize` or `./optimize_complete.py` |
| 🔄 **Map vertical** | Fixed automatically with `--auto-optimize` |
| ⚠️ **Mesh errors** | Use `_optimized.world` files |
| 🐳 **Docker fails** | Increase Docker memory to 8GB+ |

## 📖 Full Documentation

- **[README.md](README.md)** - Main overview
- **[USAGE.md](USAGE.md)** - Detailed instructions  
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Complete problem solving
- **[WORKING_COMMANDS.md](WORKING_COMMANDS.md)** - Confirmed working examples