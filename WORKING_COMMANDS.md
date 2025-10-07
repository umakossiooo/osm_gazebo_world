# Working Commands ✅

## New Integrated Workflow (RECOMMENDED)

The simplest way to create clean Gazebo worlds from OSM data:

```bash
# Create a clean Gazebo world with a single command
./osm_to_gazebo.py maps/map.osm

# Run Gazebo simulation with the optimized world
export GAZEBO_MODEL_PATH=$PWD/maps:$GAZEBO_MODEL_PATH
gz sim maps/map/map_optimized.world --verbose
```

## Available Files (After Running osm_to_gazebo.py)

```bash
ls maps/your_map/
# your_map_cleaned.osm      - Cleaned OSM data with GDAL/OGR
# your_map.world            - Original Gazebo world
# your_map_optimized.world  - Optimized Gazebo world (RECOMMENDED)

ls maps/your_map/meshes/
# your_map.obj              - Original mesh (without normals)
# your_map_fixed.obj        - Fixed mesh with normals (WORKS)
```

## Fixed Problems ✅

1. **OSM Geometry Issues**: Self-intersecting polygons, unclosed ways
   - ✅ **Fixed**: Using GDAL/OGR data cleaning in new integrated workflow

2. **Vertical Mesh Orientation**: Map appears rotated vertically
   - ✅ **Fixed**: Added rotation `<pose>0 0 0 1.5708 0 0</pose>` (90° roll)

3. **Normal Count Error**: `normal count [0] that matches vertex count`
   - ✅ **Fixed**: Using `_fixed.obj` files with calculated normals

4. **Segmentation Fault**: Simulator crashes
   - ✅ **Fixed**: Using `_optimized.world` with improved configuration

5. **XML Warnings**: Undefined SDF elements
   - ✅ **Normal**: Gazebo handles these warnings automatically

## Expected Warnings (Not Errors)

These warnings are expected and DO NOT affect functionality:

```
Warning [Utils.cc:132] XML Element[gravity], child of element[physics], not defined in SDF
Warning [Utils.cc:132] XML Element[max_contacts], child of element[ode], not defined in SDF  
[GUI] [Wrn] Material file [maps/meshes/your_map.obj.mtl] not found
[GUI] [Wrn] Missing material for shape[SurfaceArea] in OBJ file
```

## Available Scripts

```bash
# Integrated workflow (one command does it all - RECOMMENDED)
./osm_to_gazebo.py maps/input.osm [--output maps/custom_dir] [--scale 0.5] [--launch]

# Clean OSM data with GDAL/OGR
./clean_osm_data.py maps/input.osm maps/output_cleaned.osm

# Convert OSM to Gazebo world
./convert_osm_to_gazebo.py maps/input.osm maps/output.world --auto-optimize

# Fix mesh normals
./fix_mesh_normals.py maps/meshes/input.obj -o maps/meshes/output_fixed.obj

# Optimize world files
./optimize_world.py maps/input.world -o maps/input_optimized.world

# Fix mesh orientation
./fix_orientation.py maps/input.world

# Launch Gazebo with environment setup
./launch_gazebo.sh maps/input_optimized.world
```

## Current Status

- ✅ **Integrated Workflow** creates clean worlds with a single command
- ✅ **GDAL/OGR Integration** fixes geometry issues before processing
- ✅ **Gazebo Sim Working** with `gz sim maps/your_map/your_map_optimized.world`
- ✅ **Meshes With Normals** generated correctly
- ✅ **Optimized Worlds** for better performance
- ✅ **Helper Scripts** available for troubleshooting