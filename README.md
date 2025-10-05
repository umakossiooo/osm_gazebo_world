## OSM to Gazebo (.world) Converter

Convert OpenStreetMap `.osm` files into Gazebo-compatible `.world` files using OSM2World, packaged in Docker for reproducible runs. Supports Gazebo Harmonic and Classic.

### Features
- Converts `.osm` to a mesh via OSM2World, then generates a minimal `.world` referencing that mesh
- Runs fully inside Docker (Python 3.10 + Java + OSM2World)
- Simple CLI: `python convert_osm_to_gazebo.py input.osm output.world`
- Optional `--scale` parameter and colored logs

### Build
```bash
docker-compose build
```

### Prepare input map
Place your `.osm` file under `./maps/`, for example:
```bash
mkdir -p maps
cp /path/to/my_map.osm maps/
```

### Convert to `.world`
```bash
docker-compose run --rm osm2gazebo \
  python convert_osm_to_gazebo.py maps/my_map.osm maps/my_map.world
```

Optional scaling (e.g., half size):
```bash
docker-compose run --rm osm2gazebo \
  python convert_osm_to_gazebo.py maps/my_map.osm maps/my_map.world --scale 0.5
```

Outputs:
- World file: `maps/my_map.world`
- Meshes: `maps/meshes/` (referenced by the world file)

### Open in Gazebo
For Gazebo Harmonic:
```bash
gz sim maps/my_map.world
```

For Gazebo Classic:
```bash
gazebo maps/my_map.world
```

### How it works
1. `OSM2World` converts the `.osm` into a Wavefront `.obj` mesh.
2. The script writes a minimal SDF world that includes a static model referencing that mesh, plus ground and sun.

### Troubleshooting
- Java errors: Ensure the image built successfully; it installs `openjdk-17-jre-headless`.
- `OSM2World.jar not found`: The container downloads it to `/opt/osm2world/` and sets `OSM2WORLD_JAR`. If overriding, export `OSM2WORLD_JAR` to the correct path.
- Conversion failures: Check that your `.osm` is valid. Try a smaller area.
- Large maps: OSM2World can be memory intensive. Increase Docker memory or use smaller extracts.

### Development
Run the script with help to see options:
```bash
docker-compose run --rm osm2gazebo python convert_osm_to_gazebo.py --help
```


