# Comandos Funcionando ✅

## Comando Principal (CONFIRMADO)

Para ejecutar la simulación del mundo de Roma:

```bash
# Configurar el path de modelos
export GAZEBO_MODEL_PATH=$PWD/maps:$GAZEBO_MODEL_PATH

# Ejecutar Gazebo Sim con el mundo optimizado
gz sim maps/rome_optimized.world --verbose
```

## Archivos Disponibles

```bash
ls maps/
# map.world                 - Mundo original
# map_optimized.world       - Mundo optimizado (RECOMENDADO)
# rome.world                - Mundo de Roma original  
# rome_optimized.world      - Mundo de Roma optimizado (RECOMENDADO)

ls maps/meshes/
# map.obj                   - Mesh original (SIN normales)
# map_fixed.obj            - Mesh con normales (FUNCIONA)
# rome.obj                 - Mesh Roma original (SIN normales)
# rome_fixed.obj           - Mesh Roma con normales (FUNCIONA)
```

## Problemas Solucionados ✅

1. **Error de normales**: `normal count [0] that matches vertex count`
   - ✅ **Solucionado**: Usando archivos `_fixed.obj` que tienen normales calculadas

2. **Segmentation fault**: Crashes del simulador
   - ✅ **Solucionado**: Usando archivos `_optimized.world` con configuración mejorada

3. **Advertencias XML**: Elementos SDF no definidos
   - ✅ **Normal**: Gazebo maneja estas advertencias automáticamente

## Warnings Normales (No son errores)

Estos warnings son esperados y NO afectan el funcionamiento:

```
Warning [Utils.cc:132] XML Element[gravity], child of element[physics], not defined in SDF
Warning [Utils.cc:132] XML Element[max_contacts], child of element[ode], not defined in SDF  
[GUI] [Wrn] Material file [/home/studente/osm_world/maps/meshes/rome.obj.mtl] not found
[GUI] [Wrn] Missing material for shape[SurfaceArea] in OBJ file
```

## Scripts Disponibles

```bash
# Arreglar normales de meshes
./fix_mesh_normals.py maps/meshes/mi_mesh.obj -o maps/meshes/mi_mesh_fixed.obj

# Optimizar archivos world
./optimize_world.py maps/mi_mundo.world -o maps/mi_mundo_optimized.world

# Lanzamiento seguro con configuración de ambiente
./launch_gazebo.sh maps/mi_mundo_optimized.world
```

## Estado Actual

- ✅ **Gazebo Sim funcionando** con `gz sim maps/rome_optimized.world`
- ✅ **Meshes con normales** generadas correctamente  
- ✅ **Mundos optimizados** para mejor rendimiento
- ✅ **Scripts de ayuda** disponibles para troubleshooting