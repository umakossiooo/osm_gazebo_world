# OSM to Gazebo World Converter - Troubleshooting Guide

This guide helps resolve common issues when converting OpenStreetMap data to Gazebo worlds.

## Common Issues and Solutions

### 1. Mesh Normal Errors

**Problem**: Error messages like:
```
[Err] [CustomMeshShape.cc:144] One of the submeshes does not have a normal count [0] that matches its vertex count [42]
```

**Cause**: OSM2World generates OBJ files without vertex normals, which are required by Gazebo's physics engine.

**Solution**: Use the `fix_mesh_normals.py` script to add calculated normals:

```bash
# Fix existing meshes
python3 fix_mesh_normals.py maps/meshes/map.obj -o maps/meshes/map_fixed.obj

# The convert_osm_to_gazebo.py script now automatically fixes normals
python3 convert_osm_to_gazebo.py input.osm output.world
```

### 2. Segmentation Faults / Crashes

**Problem**: Gazebo crashes with segmentation fault, especially with stack traces mentioning `swrast_dri.so`.

**Causes**:
- Software rendering (no GPU acceleration)
- Large, complex meshes overwhelming the renderer
- OpenGL context issues
- Memory exhaustion

**Solutions**:

#### A. Use Optimized World Files
```bash
# Create performance-optimized world
python3 optimize_world.py maps/map.world -o maps/map_optimized.world

# Launch with proper environment
./launch_gazebo.sh maps/map_optimized.world
```

#### B. Environment Variables
```bash
# Force software rendering (if GPU issues)
export LIBGL_ALWAYS_SOFTWARE=1

# Set OpenGL version compatibility
export MESA_GL_VERSION_OVERRIDE=3.3
export MESA_GLSL_VERSION_OVERRIDE=330

# Reduce memory fragmentation
export MALLOC_ARENA_MAX=2
```

#### C. System-Level Solutions

**Install GPU drivers** (if using dedicated GPU):
```bash
# NVIDIA
sudo apt install nvidia-driver-470

# AMD
sudo apt install mesa-vulkan-drivers

# Intel
sudo apt install intel-media-va-driver
```

**Increase virtual memory**:
```bash
# Temporarily increase swap
sudo swapon --show
sudo fallocate -l 2G /tmp/swapfile
sudo chmod 600 /tmp/swapfile
sudo mkswap /tmp/swapfile
sudo swapon /tmp/swapfile
```

### 3. Performance Issues

**Problem**: Gazebo runs very slowly or becomes unresponsive.

**Solutions**:

#### A. Use Smaller OSM Areas
- Extract smaller regions from OSM data
- Use tools like Osmosis or online extractors
- Recommended area: < 1 km² for complex urban areas

#### B. Optimize Physics Settings
The optimization script automatically:
- Reduces physics update rate
- Disables shadows
- Simplifies collision detection
- Comments out complex mesh collisions

#### C. Runtime Optimizations
```bash
# Launch with reduced graphics quality
gazebo world.world --verbose --profile

# Disable GUI for headless simulation
gzserver world.world
```

### 4. Memory Issues

**Problem**: Out of memory errors or system becoming unresponsive.

**Solutions**:

#### A. Monitor Memory Usage
```bash
# Check available memory
free -h

# Monitor Gazebo memory usage
top -p $(pgrep gazebo)
```

#### B. Reduce Memory Usage
- Use optimized world files (disabled collision on large meshes)
- Close other applications
- Use smaller OSM extracts
- Consider running on a machine with more RAM

### 5. Missing Dependencies

**Problem**: Java not found, OSM2World fails to run.

**Solution**:
```bash
# Install Java Runtime Environment
sudo apt update
sudo apt install default-jre

# Verify installation
java -version
```

### 6. File Path Issues

**Problem**: Gazebo cannot find mesh files.

**Solutions**:

#### A. Set Model Path
```bash
export GAZEBO_MODEL_PATH=$PWD/maps:$GAZEBO_MODEL_PATH
```

#### B. Use Absolute Paths
Update world files to use absolute mesh paths if needed.

## Usage Examples

### Basic Conversion
```bash
# Convert OSM to Gazebo world
python3 convert_osm_to_gazebo.py maps/map.osm maps/map.world

# The script now automatically fixes normals
```

### Fix Existing Meshes
```bash
# Fix mesh normals
python3 fix_mesh_normals.py input.obj -o output_fixed.obj
```

### Optimize for Performance
```bash
# Create optimized world
python3 optimize_world.py input.world -o output_optimized.world
```

### Safe Launch
```bash
# Launch with proper environment setup
./launch_gazebo.sh maps/map_optimized.world
```

## Hardware Recommendations

### Minimum Requirements
- 4 GB RAM
- OpenGL 3.3 support
- 2 GB free disk space

### Recommended
- 8+ GB RAM
- Dedicated GPU with 2+ GB VRAM
- SSD storage
- Multi-core CPU

### For Large Urban Areas
- 16+ GB RAM
- High-end GPU (GTX 1060/RX 580 or better)
- NVMe SSD

## Best Practices

1. **Start Small**: Begin with small OSM areas (< 0.5 km²)
2. **Test Hardware**: Use `glxinfo` to check OpenGL capabilities
3. **Monitor Resources**: Watch memory and CPU usage during conversion and simulation
4. **Use Optimized Worlds**: Always use the optimized versions for simulation
5. **Backup Original Data**: Keep original OSM and mesh files before modifications

## Getting Help

If issues persist:

1. Run with verbose output: `gazebo world.world --verbose`
2. Check system logs: `dmesg | tail -n 50`
3. Monitor resource usage: `htop` or `top`
4. Test with smaller OSM areas
5. Try different OpenGL settings

## File Structure

```
osm_world/
├── convert_osm_to_gazebo.py    # Main conversion script (auto-fixes normals)
├── fix_mesh_normals.py         # Standalone normal fixing utility  
├── optimize_world.py           # Performance optimization utility
├── launch_gazebo.sh            # Safe launcher with environment setup
├── maps/
│   ├── *.osm                   # OpenStreetMap data files
│   ├── *.world                 # Gazebo world files
│   ├── *_optimized.world       # Performance-optimized worlds
│   └── meshes/
│       ├── *.obj               # Original meshes (may lack normals)
│       └── *_fixed.obj         # Meshes with calculated normals
└── OSM2World.jar              # OSM2World converter
```