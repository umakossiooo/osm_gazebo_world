#!/usr/bin/env python3
"""
OSM to Gazebo World Converter - Convert OpenStreetMap data to 3D Gazebo worlds
Works with both Gazebo Garden (gz sim) and classic Gazebo
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Import utility functions
try:
    from utils import (
        print_info, print_success, print_warn, print_error,
        ensure_osm2world_path, run_script, run_process
    )
except ImportError:
    # Fallback if utils.py is not available
    try:
        from colorama import Fore, Style, init as colorama_init
        colorama_init(autoreset=True)
    except ImportError:  # pragma: no cover - color is optional
        class _Dummy:
            def __getattr__(self, name):
                return ""
    
        def colorama_init(*_args, **_kwargs):
            return None
    
        Fore = Style = _Dummy()  # type: ignore
    
    
    def print_info(message: str) -> None:
        print(f"{Fore.BLUE}[INFO]{Style.RESET_ALL} {message}")
    
    
    def print_success(message: str) -> None:
        print(f"{Fore.GREEN}[OK]{Style.RESET_ALL} {message}")
    
    
    def print_warn(message: str) -> None:
        print(f"{Fore.YELLOW}[WARN]{Style.RESET_ALL} {message}")
    
    
    def print_error(message: str) -> None:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {message}", file=sys.stderr)


def ensure_osm2world_path() -> Path:
    # Default install path inside the container
    default_path = Path("/opt/osm2world/OSM2World.jar")
    env_path = Path(os.environ.get("OSM2WORLD_JAR", default_path.as_posix()))
    if env_path.exists():
        return env_path
    # Debian/Ubuntu package path
    deb_path = Path("/usr/share/osm2world/OSM2World.jar")
    if deb_path.exists():
        return deb_path
    # Fallback: try local project dir
    local_path = Path("OSM2World.jar")
    if local_path.exists():
        return local_path
    raise FileNotFoundError(
        "OSM2World.jar not found. Ensure it exists at /opt/osm2world/OSM2World.jar or set OSM2WORLD_JAR."
    )


def run_osm2world(osm_path: Path, out_mesh_path: Path) -> None:
    osm2world_jar = ensure_osm2world_path()
    lib_dir = osm2world_jar.parent / "lib"
    
    # Build classpath with all JAR files
    classpath_parts = [osm2world_jar.as_posix()]
    if lib_dir.exists():
        classpath_parts.extend([jar.as_posix() for jar in lib_dir.glob("*.jar")])
    classpath = ":".join(classpath_parts)
    
    java_cmd = [
        "java",
        "-cp",
        classpath,
        "org.osm2world.console.OSM2World",
        "-i",
        osm_path.as_posix(),
        "-o",
        out_mesh_path.as_posix(),
    ]
    print_info("Running OSM2World to generate mesh (this may take a while)...")
    try:
        subprocess.run(java_cmd, check=True)
    except FileNotFoundError as exc:
        raise RuntimeError(
            "Java runtime not found. Ensure Java is installed inside the container."
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"OSM2World failed with exit code {exc.returncode}. Check your .osm file."
        ) from exc


def fix_mesh_normals(mesh_path: Path) -> None:
    """Fix OBJ mesh by calculating and adding missing vertex normals."""
    print_info("Fixing mesh normals for Gazebo compatibility...")
    
    # Use the fix_mesh_normals.py script
    script_path = Path(__file__).parent / "fix_mesh_normals.py"
    if not script_path.exists():
        print_warn("fix_mesh_normals.py not found, skipping normal generation")
        return
        
    temp_fixed_path = mesh_path.with_suffix(".fixed.obj")
    
    try:
        subprocess.run([
            sys.executable, 
            script_path.as_posix(),
            mesh_path.as_posix(),
            "-o",
            temp_fixed_path.as_posix()
        ], check=True, capture_output=True, text=True)
        
        # Replace original with fixed version
        shutil.move(temp_fixed_path.as_posix(), mesh_path.as_posix())
        print_success("Mesh normals fixed successfully")
        
    except subprocess.CalledProcessError as exc:
        print_warn(f"Failed to fix mesh normals: {exc}")
        if temp_fixed_path.exists():
            temp_fixed_path.unlink()
    except Exception as exc:
        print_warn(f"Error fixing mesh normals: {exc}")
        if temp_fixed_path.exists():
            temp_fixed_path.unlink()


def write_world_file(
    world_path: Path,
    relative_mesh_uri: str,
    scale: float,
) -> None:
    # SDF world with built-in ground plane, sun, and a static model referencing the OBJ mesh
    content = f"""
<sdf version="1.7">
  <world name="osm_world">
    <!-- Physics -->
    <physics name="default_physics" default="0" type="ode">
      <gravity>0 0 -9.8066</gravity>
      <ode>
        <solver>
          <type>quick</type>
          <iters>10</iters>
          <sor>1.3</sor>
        </solver>
        <constraints>
          <cfm>0</cfm>
          <erp>0.2</erp>
          <contact_max_correcting_vel>100</contact_max_correcting_vel>
          <contact_surface_layer>0.001</contact_surface_layer>
        </constraints>
      </ode>
      <max_step_size>0.004</max_step_size>
      <real_time_factor>1</real_time_factor>
      <real_time_update_rate>250</real_time_update_rate>
    </physics>

    <!-- Scene -->
    <scene>
      <ambient>0.4 0.4 0.4 1</ambient>
      <background>0.7 0.7 0.7 1</background>
      <shadows>1</shadows>
    </scene>

    <!-- Lighting -->
    <light type="directional" name="sun">
      <cast_shadows>1</cast_shadows>
      <pose>0 0 10 0 0 0</pose>
      <diffuse>0.8 0.8 0.8 1</diffuse>
      <specular>0.2 0.2 0.2 1</specular>
      <attenuation>
        <range>1000</range>
        <constant>0.9</constant>
        <linear>0.01</linear>
        <quadratic>0.001</quadratic>
      </attenuation>
      <direction>-0.5 0.1 -0.9</direction>
    </light>

    <!-- Ground Plane -->
    <model name="ground_plane">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>100 100</size>
            </plane>
          </geometry>
          <surface>
            <contact>
              <collide_bitmask>65535</collide_bitmask>
              <ode/>
            </contact>
            <friction>
              <ode>
                <mu>100</mu>
                <mu2>50</mu2>
              </ode>
            </friction>
          </surface>
        </collision>
        <visual name="visual">
          <cast_shadows>false</cast_shadows>
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>100 100</size>
            </plane>
          </geometry>
          <material>
            <script>
              <uri>file://media/materials/scripts/gazebo.material</uri>
              <name>Gazebo/Grey</name>
            </script>
          </material>
        </visual>
      </link>
    </model>

    <!-- OSM Environment Model -->
    <model name="osm_environment">
      <static>true</static>
      <!-- Rotate mesh to horizontal orientation (OSM meshes are often vertical) -->
      <pose>0 0 0 1.5708 0 0</pose>
      <link name="osm_mesh_link">
        <visual name="osm_visual">
          <geometry>
            <mesh>
              <uri>{relative_mesh_uri}</uri>
              <scale>{scale} {scale} {scale}</scale>
            </mesh>
          </geometry>
          <material>
            <script>
              <uri>file://media/materials/scripts/gazebo.material</uri>
              <name>Gazebo/White</name>
            </script>
          </material>
        </visual>
        <collision name="osm_collision">
          <geometry>
            <mesh>
              <uri>{relative_mesh_uri}</uri>
              <scale>{scale} {scale} {scale}</scale>
            </mesh>
          </geometry>
        </collision>
      </link>
    </model>
  </world>
</sdf>
""".strip()
    world_path.write_text(content)


def convert(osm_file: Path, output_world: Path, scale: float) -> None:
    if not osm_file.exists():
        raise FileNotFoundError(f"Input file not found: {osm_file}")

    output_world = output_world.with_suffix(".world")
    output_dir = output_world.parent
    meshes_dir = output_dir / "meshes"
    meshes_dir.mkdir(parents=True, exist_ok=True)

    base = output_world.stem
    mesh_path = meshes_dir / f"{base}.obj"

    with tempfile.TemporaryDirectory(prefix="osm2gazebo_") as tmpdir:
        tmp_mesh = Path(tmpdir) / f"{base}.obj"
        run_osm2world(osm_file, tmp_mesh)
        
        # Fix mesh normals to prevent Gazebo errors
        fix_mesh_normals(tmp_mesh)

        # Move generated mesh next to the world under meshes/
        shutil.move(tmp_mesh.as_posix(), mesh_path.as_posix())

    # Use path relative to world file for portability
    relative_mesh_uri = os.path.relpath(mesh_path.as_posix(), start=output_dir.as_posix())
    write_world_file(output_world, relative_mesh_uri, scale)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert an OpenStreetMap (.osm) file into a Gazebo .world with a mesh generated by OSM2World.",
    )
    parser.add_argument("input_osm", help="Path to input .osm file")
    parser.add_argument("output_world", help="Path to output .world file")
    parser.add_argument(
        "--scale",
        type=float,
        default=1.0,
        help="Uniform scaling factor applied to the mesh in the world (default: 1.0)",
    )
    parser.add_argument(
        "--auto-optimize",
        action="store_true",
        help="Automatically create optimized version with fixed normals and performance settings",
    )
    parser.add_argument(
        "--launch",
        action="store_true", 
        help="Automatically launch Gazebo after conversion (requires --auto-optimize)",
    )
    return parser.parse_args()


def main() -> int:
    # We'll skip colorama initialization here since it should be handled
    # in the imports or utils.py if available

    args = parse_args()
    input_osm = Path(args.input_osm).resolve()
    output_world = Path(args.output_world).resolve()

    print_info(f"Input: {input_osm}")
    print_info(f"Output world: {output_world}")
    print_info("Converting map…")

    try:
        convert(input_osm, output_world, args.scale)
    except FileNotFoundError as e:
        print_error(str(e))
        return 2
    except RuntimeError as e:
        print_error(str(e))
        return 3
    except Exception as e:  # unexpected
        print_error(f"Unexpected error: {e}")
        return 4

    print_success("Export completed.")
    print_success(f"World written to: {output_world}")
    print_success(f"Mesh stored under: {output_world.parent / 'meshes'}")
    
    # Auto-optimization if requested
    if args.auto_optimize:
        print_info("Running auto-optimization...")
        try:
            script_dir = Path(__file__).parent
            optimize_script = script_dir / "optimize_complete.py"
            
            if optimize_script.exists():
                optimize_args = [output_world.as_posix()]
                if args.launch:
                    optimize_args.append("--launch")
                    
                subprocess.run([
                    sys.executable,
                    optimize_script.as_posix()
                ] + optimize_args, check=True)
                
                print_success("Auto-optimization completed!")
            else:
                print_warn("optimize_complete.py not found, skipping auto-optimization")
                
        except subprocess.CalledProcessError as e:
            print_error(f"Auto-optimization failed: {e}")
        except Exception as e:
            print_error(f"Unexpected error during auto-optimization: {e}")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


