"""
AMANAH FARM / MANZNO, ANANTNAG
Parametric sheep shed model generator for Blender 3.6+ / 4.x.

Run from a terminal:
    blender --background --python amanah_farm_model.py

Or open the file in Blender's Scripting workspace and click Run Script.
The script creates an editable scene, cameras, materials, annotations,
quality-control files, OBJ/GLB exports, and rendered study views.

This is a design-development model, not a certified construction drawing.
All structural member sizes, connections, foundations, drainage and animal
welfare allowances require local professional review before construction.
"""

import bpy
import csv
import json
import math
import os
from math import atan2, cos, pi, radians, sin, sqrt
from pathlib import Path

from mathutils import Vector


# -----------------------------------------------------------------------------
# PROJECT SETTINGS
# -----------------------------------------------------------------------------

PROJECT_NAME = "Amanah Farm — Manzno Sheep Shed"
LOCATION = "Manzno village, Anantnag, Kashmir, India"

ROOT = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()
OUTPUT_DIR = ROOT / "amanah_farm_outputs"
RENDER_DIR = OUTPUT_DIR / "renders"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
RENDER_DIR.mkdir(parents=True, exist_ok=True)

# True will make the script render every defined study camera. Set to False for
# a quick scene-only build while iterating.
RENDER_VIEWS = True
EXPORT_GEOMETRY = True
SAVE_BLEND = True

# Dimensional brief, metres. Eaves and ridge are measured from adjacent grade.
SHED_L = 8.0
SHED_W = 5.0
PLINTH_H = 0.45
EAVES_Z = 2.60
RIDGE_Z = 4.00
ROOF_OVERHANG = 0.45
YARD_L = 8.0
YARD_W = 5.0

# Coordinate convention: shed spans X = 0..8 and Y = 0..5.
# The open exercise yard sits to the south, Y = -5..0.
YARD_Y0 = -YARD_W
YARD_Y1 = 0.0

# Preliminary member sizes. All are intentionally exposed in one place for
# easy engineering review and modification.
TIMBER_POST = 0.18
TIMBER_BEAM = 0.16
TIMBER_RAFTER = 0.14
TIMBER_PURLIN = 0.12
ROOF_THICKNESS = 0.08
PARTITION_H = 1.15
WALL_TOP = EAVES_Z - 0.10
FLOOR_Z = PLINTH_H + 0.08

# The internal zoning uses a small L-shaped isolation pen so all requested
# areas add to the exact 40 m² covered footprint.
ZONES = {
    "Main_Sheep_Resting_Feeding": 24.0,
    "Ram_Pen": 4.0,
    "Lambing_Pen": 4.0,
    "Isolation_Pen": 3.0,
    "Dry_Feed_Equipment_Store": 5.0,
}

COLLECTION_NAMES = [
    "00_SITE_TERRAIN",
    "01_FOUNDATION_STONE",
    "02_TIMBER_FRAME",
    "03_WATTLE_AND_MUD",
    "04_ROOF_AND_RAINWATER",
    "05_INTERNAL_FITTINGS",
    "06_WATER_AND_WASTE",
    "07_LIVESTOCK_SCALE",
    "08_LANDSCAPE",
    "09_ANNOTATIONS",
    "10_CAMERAS_AND_LIGHTS",
]

# -----------------------------------------------------------------------------
# COLLECTIONS, MATERIALS, AND BASIC UTILITIES
# -----------------------------------------------------------------------------

COLLECTIONS = {}
MATERIALS = {}


def collection(name):
    """Create or return a top-level collection."""
    if name in COLLECTIONS:
        return COLLECTIONS[name]
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(coll)
    COLLECTIONS[name] = coll
    return coll


def move_to_collection(obj, coll):
    """Keep a newly-created object in one logical collection."""
    for old_coll in list(obj.users_collection):
        old_coll.objects.unlink(obj)
    coll.objects.link(obj)
    return obj


def clear_scene():
    """Remove the default scene while preserving Blender's master collection."""
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablock in (bpy.data.meshes, bpy.data.curves, bpy.data.materials,
                      bpy.data.cameras, bpy.data.lights):
        # Unused datablocks are harmless, but clearing them makes repeated runs
        # in the same Blender file much less confusing.
        for item in list(datablock):
            if item.users == 0:
                datablock.remove(item)
    for child in list(bpy.context.scene.collection.children):
        bpy.context.scene.collection.children.unlink(child)
        if child.users == 0:
            bpy.data.collections.remove(child)
    COLLECTIONS.clear()
    MATERIALS.clear()


def make_material(name, color, roughness=0.75, metallic=0.0,
                  transmission=0.0, alpha=1.0):
    """Create a simple Principled BSDF material with useful custom metadata."""
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.diffuse_color = (*color, alpha)
    if hasattr(mat, "surface_render_method"):
        mat.surface_render_method = "DITHERED" if alpha < 1 else "DITHERED"
    elif hasattr(mat, "blend_method"):
        mat.blend_method = "BLEND" if alpha < 1 else "OPAQUE"
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
        if "Transmission Weight" in bsdf.inputs:
            bsdf.inputs["Transmission Weight"].default_value = transmission
        elif "Transmission" in bsdf.inputs:
            bsdf.inputs["Transmission"].default_value = transmission
        if "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = alpha
    mat["schedule_material"] = name
    MATERIALS[name] = mat
    return mat


def make_materials():
    """Palette based on local stone, walnut/timber, willow and clay."""
    make_material("Stone_Base", (0.25, 0.27, 0.25), 0.92)
    make_material("Stone_Light", (0.38, 0.39, 0.34), 0.88)
    make_material("Stone_Dark", (0.17, 0.19, 0.18), 0.94)
    make_material("Mortar", (0.49, 0.48, 0.42), 0.98)
    make_material("Damp_Proof_Course", (0.08, 0.10, 0.09), 0.65)
    make_material("Timber_Walnut", (0.28, 0.13, 0.055), 0.72)
    make_material("Timber_Light", (0.49, 0.28, 0.11), 0.78)
    make_material("Timber_End", (0.62, 0.38, 0.16), 0.8)
    make_material("Willow", (0.46, 0.35, 0.17), 0.88)
    make_material("Willow_Fresh", (0.56, 0.44, 0.22), 0.88)
    make_material("Mud_Plaster", (0.57, 0.43, 0.27), 0.96)
    make_material("Clay_Light", (0.67, 0.53, 0.34), 0.93)
    make_material("Straw", (0.74, 0.57, 0.24), 0.92)
    make_material("Roof_Corrugated", (0.22, 0.28, 0.27), 0.42, metallic=0.45)
    make_material("Roof_Ridge", (0.12, 0.16, 0.15), 0.34, metallic=0.58)
    make_material("Roof_Insulation", (0.72, 0.65, 0.47), 0.9)
    make_material("Galvanized_Metal", (0.42, 0.48, 0.46), 0.32, metallic=0.75)
    make_material("Water_Blue", (0.08, 0.35, 0.48), 0.2, metallic=0.1)
    make_material("Clean_Water_Line", (0.06, 0.48, 0.76), 0.34, metallic=0.1)
    make_material("Dirty_Water_Line", (0.34, 0.16, 0.08), 0.72)
    make_material("Bedding", (0.67, 0.48, 0.21), 1.0)
    make_material("Feed", (0.43, 0.28, 0.10), 1.0)
    make_material("Fence_Wood", (0.30, 0.16, 0.07), 0.9)
    make_material("Terrain", (0.18, 0.28, 0.16), 1.0)
    make_material("Terrain_Light", (0.34, 0.42, 0.23), 1.0)
    make_material("Orchard_Trunk", (0.20, 0.10, 0.045), 1.0)
    make_material("Orchard_Leaf", (0.17, 0.35, 0.12), 0.95)
    make_material("Mountain_Far", (0.23, 0.31, 0.34), 1.0)
    make_material("Mountain_Mid", (0.31, 0.38, 0.36), 1.0)
    make_material("Plan_Zone", (0.78, 0.67, 0.38), 0.88, alpha=0.78)
    make_material("Annotation", (0.07, 0.12, 0.10), 0.9)
    make_material("Annotation_Gold", (0.64, 0.39, 0.10), 0.82)
    make_material("Safety_Red", (0.55, 0.12, 0.08), 0.75)
    make_material("White", (0.88, 0.88, 0.82), 0.9)


def apply_bevel(obj, width=0.02, segments=2):
    if width <= 0:
        return obj
    modifier = obj.modifiers.new(name="Small_Rounded_Edges", type="BEVEL")
    modifier.width = width
    modifier.segments = segments
    modifier.limit_method = "ANGLE"
    return obj


def add_box(name, location, dimensions, material, coll_name,
            rotation=(0.0, 0.0, 0.0), bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = rotation
    obj.scale = (dimensions[0] / 2.0, dimensions[1] / 2.0, dimensions[2] / 2.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    move_to_collection(obj, collection(coll_name))
    if material:
        obj.data.materials.append(MATERIALS[material] if isinstance(material, str) else material)
    if bevel:
        apply_bevel(obj, bevel)
    return obj


def add_cylinder(name, location, radius, depth, material, coll_name,
                 vertices=12, rotation=(0.0, 0.0, 0.0), bevel=0.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius,
                                        depth=depth, location=location,
                                        rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    move_to_collection(obj, collection(coll_name))
    if material:
        obj.data.materials.append(MATERIALS[material] if isinstance(material, str) else material)
    if bevel:
        apply_bevel(obj, bevel)
    return obj


def add_uv_sphere(name, location, scale, material, coll_name,
                  segments=16, rings=8):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings,
                                         location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    move_to_collection(obj, collection(coll_name))
    if material:
        obj.data.materials.append(MATERIALS[material] if isinstance(material, str) else material)
    return obj


def add_beam_between(name, start, end, width, depth, material, coll_name,
                     bevel=0.0):
    start = Vector(start)
    end = Vector(end)
    vec = end - start
    length = vec.length
    if length < 0.001:
        return None
    mid = (start + end) / 2.0
    bpy.ops.mesh.primitive_cube_add(location=mid)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = (width, depth, length)
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(vec.normalized())
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    move_to_collection(obj, collection(coll_name))
    if material:
        obj.data.materials.append(MATERIALS[material] if isinstance(material, str) else material)
    if bevel:
        apply_bevel(obj, bevel)
    return obj


def add_cylinder_between(name, start, end, radius, material, coll_name,
                         vertices=12):
    start = Vector(start)
    end = Vector(end)
    vec = end - start
    length = vec.length
    if length < 0.001:
        return None
    mid = (start + end) / 2.0
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius,
                                        depth=length, location=mid)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(vec.normalized())
    move_to_collection(obj, collection(coll_name))
    if material:
        obj.data.materials.append(MATERIALS[material] if isinstance(material, str) else material)
    return obj


def add_text(name, body, location, size=0.22, material="Annotation",
             coll_name="09_ANNOTATIONS", rotation=(0.0, 0.0, 0.0),
             align_x="CENTER", extrude=0.003, bevel=0.0):
    curve = bpy.data.curves.new(name=name, type="FONT")
    curve.body = body
    curve.align_x = align_x
    curve.align_y = "CENTER"
    curve.size = size
    curve.extrude = extrude
    curve.bevel_depth = bevel
    curve.resolution_u = 6
    obj = bpy.data.objects.new(name, curve)
    collection(coll_name).objects.link(obj)
    obj.location = location
    obj.rotation_euler = rotation
    if material:
        curve.materials.append(MATERIALS[material] if isinstance(material, str) else material)
    obj["annotation_text"] = body
    return obj


def add_polyline(name, points, material, coll_name, bevel_depth=0.015,
                 cyclic=False):
    curve = bpy.data.curves.new(name=name, type="CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 1
    curve.bevel_depth = bevel_depth
    curve.bevel_resolution = 1
    spline = curve.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for point, co in zip(spline.points, points):
        point.co = (*co, 1.0)
    spline.use_cyclic_u = cyclic
    obj = bpy.data.objects.new(name, curve)
    collection(coll_name).objects.link(obj)
    curve.materials.append(MATERIALS[material] if isinstance(material, str) else material)
    return obj


# -----------------------------------------------------------------------------
# SITE AND FOUNDATION
# -----------------------------------------------------------------------------


def create_terrain():
    """Neutral sloping platform; no site-specific elevations are claimed."""
    coll = collection("00_SITE_TERRAIN")
    width, depth = 32.0, 26.0
    nx, ny = 8, 7
    verts = []
    faces = []
    for iy in range(ny + 1):
        y = -9.0 + depth * iy / ny
        for ix in range(nx + 1):
            x = -10.0 + width * ix / nx
            # A modest conceptual slope and a soft fall away from the shed.
            z = 0.025 * x + 0.035 * y - 0.02 * sin(x * 0.55) * cos(y * 0.35)
            verts.append((x, y, z))
    for iy in range(ny):
        for ix in range(nx):
            a = iy * (nx + 1) + ix
            b = a + 1
            d = (iy + 1) * (nx + 1) + ix
            c = d + 1
            faces.append((a, b, c, d))
    mesh = bpy.data.meshes.new("Concept_Terrain_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new("Site_Terrain_Concept_Slope", mesh)
    coll.objects.link(obj)
    obj.data.materials.append(MATERIALS["Terrain"])
    obj["note"] = "Conceptual slope only; confirm survey, soil and drainage locally."

    # A lighter strip makes the service path legible without pretending to be a
    # finished site plan.
    add_box("Service_Path_Base", (4.0, -4.4, 0.10), (9.5, 1.0, 0.08),
            "Stone_Light", "08_LANDSCAPE", bevel=0.04)
    for i in range(12):
        x = -0.8 + i * 0.78
        add_box(f"Path_Stone_{i+1:02d}", (x, -4.4, 0.16), (0.56, 0.72, 0.07),
                "Stone_Dark" if i % 3 else "Stone_Light", "08_LANDSCAPE", bevel=0.03)


def create_stone_plinth():
    """Raised stone base plus individually readable perimeter stone blocks."""
    add_box("Foundation_Stone_Core", (SHED_L / 2, SHED_W / 2, PLINTH_H / 2),
            (SHED_L, SHED_W, PLINTH_H), "Stone_Base", "01_FOUNDATION_STONE",
            bevel=0.045)
    add_box("Foundation_Damp_Proof_Course", (SHED_L / 2, SHED_W / 2, PLINTH_H + 0.015),
            (SHED_L + 0.06, SHED_W + 0.06, 0.03), "Damp_Proof_Course",
            "01_FOUNDATION_STONE", bevel=0.01)

    stone_mats = ["Stone_Light", "Stone_Base", "Stone_Dark"]
    # North and south faces.
    x = 0.0
    idx = 1
    while x < SHED_L - 0.01:
        length = min(0.72 + 0.13 * ((idx * 7) % 3), SHED_L - x)
        for y, side in [(0.0, "South"), (SHED_W, "North")]:
            add_box(f"Foundation_Stone_{side}_{idx:02d}",
                    (x + length / 2, y, PLINTH_H * 0.50),
                    (length - 0.025, 0.22, PLINTH_H - 0.035),
                    stone_mats[(idx + (0 if side == "South" else 1)) % len(stone_mats)],
                    "01_FOUNDATION_STONE", bevel=0.025)
        x += length
        idx += 1
    # East and west faces, with corner overlap kept visually believable.
    y = 0.22
    idx = 1
    while y < SHED_W - 0.01:
        length = min(0.65 + 0.11 * ((idx * 5) % 3), SHED_W - y - 0.22)
        for x, side in [(0.0, "West"), (SHED_L, "East")]:
            add_box(f"Foundation_Stone_{side}_{idx:02d}",
                    (x, y + length / 2, PLINTH_H * 0.50),
                    (0.22, length - 0.025, PLINTH_H - 0.035),
                    stone_mats[(idx + 1) % len(stone_mats)],
                    "01_FOUNDATION_STONE", bevel=0.025)
        y += length
        idx += 1

    # Preliminary post shoe / anchor positions. The actual anchorage requires
    # engineering and is intentionally named as a review item.
    post_points = frame_post_points()
    for i, (x, y) in enumerate(post_points, 1):
        add_box(f"Timber_Anchor_Plate_{i:02d}", (x, y, PLINTH_H + 0.035),
                (0.27, 0.27, 0.035), "Galvanized_Metal", "01_FOUNDATION_STONE",
                bevel=0.01)
        add_cylinder(f"Timber_Anchor_Bolt_{i:02d}", (x, y, PLINTH_H + 0.07),
                     0.025, 0.07, "Galvanized_Metal", "01_FOUNDATION_STONE",
                     vertices=10)


def frame_post_points():
    xs = [0.18, 2.0, 4.0, 6.0, 7.82]
    points = []
    for x in xs:
        points.append((x, 0.18))
        points.append((x, 4.82))
    points.extend([(0.18, 2.5), (7.82, 2.5)])
    # Keep order deterministic and remove near duplicates.
    out = []
    for p in points:
        if p not in out:
            out.append(p)
    return out


# -----------------------------------------------------------------------------
# TIMBER FRAME AND ROOF
# -----------------------------------------------------------------------------


def create_timber_frame():
    posts = frame_post_points()
    for i, (x, y) in enumerate(posts, 1):
        add_box(f"Post_{'West' if x < 0.3 else 'East' if x > 7.7 else 'Bay'}_{i:02d}",
                (x, y, (PLINTH_H + EAVES_Z) / 2),
                (TIMBER_POST, TIMBER_POST, EAVES_Z - PLINTH_H),
                "Timber_Walnut", "02_TIMBER_FRAME", bevel=0.025)

    # Eaves beams on both long elevations and end wall plates.
    add_box("Beam_South_Eaves", (SHED_L / 2, 0.18, EAVES_Z),
            (SHED_L - 0.18, TIMBER_BEAM, TIMBER_BEAM), "Timber_Light",
            "02_TIMBER_FRAME", bevel=0.025)
    add_box("Beam_North_Eaves", (SHED_L / 2, 4.82, EAVES_Z),
            (SHED_L - 0.18, TIMBER_BEAM, TIMBER_BEAM), "Timber_Light",
            "02_TIMBER_FRAME", bevel=0.025)
    add_box("Beam_West_Eaves", (0.18, SHED_W / 2, EAVES_Z),
            (TIMBER_BEAM, SHED_W - 0.18, TIMBER_BEAM), "Timber_Light",
            "02_TIMBER_FRAME", bevel=0.025)
    add_box("Beam_East_Eaves", (7.82, SHED_W / 2, EAVES_Z),
            (TIMBER_BEAM, SHED_W - 0.18, TIMBER_BEAM), "Timber_Light",
            "02_TIMBER_FRAME", bevel=0.025)

    # Ridge beam and central purlin line.
    add_box("Beam_Ridge", (SHED_L / 2, SHED_W / 2, RIDGE_Z),
            (SHED_L + 0.40, TIMBER_BEAM, TIMBER_BEAM), "Timber_End",
            "02_TIMBER_FRAME", bevel=0.025)
    add_box("Beam_Central_Tie", (SHED_L / 2, SHED_W / 2, 2.36),
            (SHED_L - 0.25, TIMBER_BEAM, TIMBER_BEAM), "Timber_Light",
            "02_TIMBER_FRAME", bevel=0.02)

    # End-wall diagonal bracing, visible on both gables.
    for side, y in [("West", 0.18), ("East", 4.82)]:
        add_beam_between(f"Brace_{side}_A", (0.30, y, PLINTH_H + 0.25),
                         (2.0, y, EAVES_Z - 0.15), 0.11, 0.11, "Timber_Light",
                         "02_TIMBER_FRAME", bevel=0.018)
        add_beam_between(f"Brace_{side}_B", (7.70, y, PLINTH_H + 0.25),
                         (6.0, y, EAVES_Z - 0.15), 0.11, 0.11, "Timber_Light",
                         "02_TIMBER_FRAME", bevel=0.018)

    # Long elevation bracing is split around the main south gate.
    for side, y in [("South", 0.18), ("North", 4.82)]:
        for bay, x0, x1 in [("A", 0.25, 2.0), ("B", 2.0, 4.0),
                            ("C", 4.0, 6.0), ("D", 6.0, 7.75)]:
            add_beam_between(f"Brace_{side}_{bay}_Rising",
                             (x0, y, PLINTH_H + 0.22),
                             (x1, y, EAVES_Z - 0.20),
                             0.075, 0.10, "Timber_Light", "02_TIMBER_FRAME",
                             bevel=0.012)

    # Roof trusses / rafters. Ridge runs longitudinally along X.
    roof_left_eave = (0.0, -ROOF_OVERHANG, EAVES_Z)
    roof_right_eave = (0.0, SHED_W + ROOF_OVERHANG, EAVES_Z)
    ridge = (0.0, SHED_W / 2, RIDGE_Z)
    for i, x in enumerate([0.35, 1.5, 2.75, 4.0, 5.25, 6.5, 7.65], 1):
        add_beam_between(f"Roof_Rafter_Left_{i:02d}",
                         (x, roof_left_eave[1], roof_left_eave[2]),
                         (x, ridge[1], ridge[2]),
                         TIMBER_RAFTER, TIMBER_RAFTER, "Timber_Light",
                         "02_TIMBER_FRAME", bevel=0.018)
        add_beam_between(f"Roof_Rafter_Right_{i:02d}",
                         (x, ridge[1], ridge[2]),
                         (x, roof_right_eave[1], roof_right_eave[2]),
                         TIMBER_RAFTER, TIMBER_RAFTER, "Timber_Light",
                         "02_TIMBER_FRAME", bevel=0.018)
        add_beam_between(f"Roof_Tie_{i:02d}",
                         (x, 0.24, EAVES_Z - 0.05),
                         (x, 4.76, EAVES_Z - 0.05),
                         0.10, 0.10, "Timber_Light", "02_TIMBER_FRAME",
                         bevel=0.012)

    # Purlins run with the roof slope; X-longitudinal lines are separate beams.
    left_yz = [(0.20, 2.72), (1.05, 3.10), (1.85, 3.51)]
    right_yz = [(4.80, 2.72), (3.95, 3.10), (3.15, 3.51)]
    for i, (y, z) in enumerate(left_yz, 1):
        add_box(f"Purlin_Left_{i:02d}", (SHED_L / 2, y, z),
                (SHED_L + 0.30, TIMBER_PURLIN, TIMBER_PURLIN),
                "Timber_Walnut", "02_TIMBER_FRAME", bevel=0.018)
    for i, (y, z) in enumerate(right_yz, 1):
        add_box(f"Purlin_Right_{i:02d}", (SHED_L / 2, y, z),
                (SHED_L + 0.30, TIMBER_PURLIN, TIMBER_PURLIN),
                "Timber_Walnut", "02_TIMBER_FRAME", bevel=0.018)


def create_roof_and_rainwater():
    """Two editable roof planes, corrugation ribs, ridge cap, gutters and tank."""
    slope_dy = (SHED_W / 2) + ROOF_OVERHANG
    slope_dz = RIDGE_Z - EAVES_Z
    slope_len = sqrt(slope_dy ** 2 + slope_dz ** 2)
    slope_angle = atan2(slope_dz, slope_dy)
    center_z = (RIDGE_Z + EAVES_Z) / 2
    center_left_y = (SHED_W / 2 - ROOF_OVERHANG) / 2
    center_right_y = SHED_W - center_left_y
    roof_length = SHED_L + 2 * ROOF_OVERHANG

    add_box("Roof_Plane_Left_Corrugated", (SHED_L / 2, center_left_y, center_z),
            (roof_length, slope_len, ROOF_THICKNESS), "Roof_Corrugated",
            "04_ROOF_AND_RAINWATER", rotation=(slope_angle, 0.0, 0.0), bevel=0.01)
    add_box("Roof_Plane_Right_Corrugated", (SHED_L / 2, center_right_y, center_z),
            (roof_length, slope_len, ROOF_THICKNESS), "Roof_Corrugated",
            "04_ROOF_AND_RAINWATER", rotation=(-slope_angle, 0.0, 0.0), bevel=0.01)

    # A warm inner ceiling/insulation layer makes the optional build-up inspectable.
    add_box("Roof_Insulation_Left_Concept", (SHED_L / 2, center_left_y + 0.02, center_z - 0.09),
            (roof_length - 0.08, slope_len - 0.08, 0.045), "Roof_Insulation",
            "04_ROOF_AND_RAINWATER", rotation=(slope_angle, 0.0, 0.0))
    add_box("Roof_Insulation_Right_Concept", (SHED_L / 2, center_right_y - 0.02, center_z - 0.09),
            (roof_length - 0.08, slope_len - 0.08, 0.045), "Roof_Insulation",
            "04_ROOF_AND_RAINWATER", rotation=(-slope_angle, 0.0, 0.0))

    # Corrugation ribs, kept sparse enough for editing.
    for i, x in enumerate([0.25 + j * 0.52 for j in range(16)], 1):
        add_beam_between(f"Roof_Corrugation_Left_{i:02d}",
                         (x, -ROOF_OVERHANG - 0.01, EAVES_Z + 0.045),
                         (x, SHED_W / 2, RIDGE_Z + 0.045),
                         0.025, 0.025, "Galvanized_Metal",
                         "04_ROOF_AND_RAINWATER")
        add_beam_between(f"Roof_Corrugation_Right_{i:02d}",
                         (x, SHED_W / 2, RIDGE_Z + 0.045),
                         (x, SHED_W + ROOF_OVERHANG + 0.01, EAVES_Z + 0.045),
                         0.025, 0.025, "Galvanized_Metal",
                         "04_ROOF_AND_RAINWATER")

    add_box("Roof_Ridge_Cap", (SHED_L / 2, SHED_W / 2, RIDGE_Z + 0.07),
            (roof_length + 0.12, 0.18, 0.12), "Roof_Ridge",
            "04_ROOF_AND_RAINWATER", bevel=0.025)

    # Gutters and downpipes. The tank is deliberately outside the dirty-water route.
    for side, y in [("South", -ROOF_OVERHANG - 0.04), ("North", SHED_W + ROOF_OVERHANG + 0.04)]:
        add_cylinder_between(f"Gutter_{side}", (0.0, y, EAVES_Z - 0.02),
                            (SHED_L, y, EAVES_Z - 0.02), 0.055,
                            "Galvanized_Metal", "04_ROOF_AND_RAINWATER")
    for side, y, x in [("South", -ROOF_OVERHANG - 0.04, 7.45),
                       ("North", SHED_W + ROOF_OVERHANG + 0.04, 7.45)]:
        add_cylinder_between(f"Downpipe_{side}", (x, y, EAVES_Z - 0.03),
                            (x, y, 0.55), 0.045, "Galvanized_Metal",
                            "04_ROOF_AND_RAINWATER")
        add_cylinder_between(f"Downpipe_Foot_{side}", (x, y, 0.55),
                            (8.8, 3.8 if side == "North" else -1.0, 0.35),
                            0.045, "Galvanized_Metal", "04_ROOF_AND_RAINWATER")

    add_cylinder("Rainwater_Tank", (9.25, 3.75, 1.15), 0.72, 1.55,
                 "Water_Blue", "04_ROOF_AND_RAINWATER", vertices=24, bevel=0.025)
    add_box("Rainwater_Tank_Lid", (9.25, 3.75, 1.95), (1.14, 1.14, 0.09),
            "Galvanized_Metal", "04_ROOF_AND_RAINWATER", bevel=0.025)
    add_text("Rainwater_Tank_Label", "RAINWATER\nSTORAGE", (9.25, 3.05, 2.05),
             size=0.15, material="White", coll_name="09_ANNOTATIONS",
             rotation=(radians(90), 0.0, 0.0))

    # High-level ventilated ridge opening and protective mesh.
    add_box("High_Level_Ventilation_Opening", (4.0, 2.49, 3.70),
            (6.4, 0.08, 0.34), "Dark_Water" if "Dark_Water" in MATERIALS else "Roof_Ridge",
            "04_ROOF_AND_RAINWATER")
    for i in range(18):
        x = 0.9 + i * 0.36
        add_beam_between(f"Vent_Mesh_Bar_{i+1:02d}", (x, 2.43, 3.58),
                         (x, 2.43, 3.91), 0.018, 0.018,
                         "Galvanized_Metal", "04_ROOF_AND_RAINWATER")
    add_text("Vent_Label", "PROTECTED HIGH-LEVEL VENT", (4.0, 2.27, 3.95),
             size=0.14, material="Annotation_Gold", coll_name="09_ANNOTATIONS")


# -----------------------------------------------------------------------------
# WALL INFILL, OPENINGS, AND INTERNAL FUNCTIONAL ZONING
# -----------------------------------------------------------------------------


def create_wattle_panel(name_prefix, axis, fixed, start, end, z0, z1,
                        exposed=True, plaster_band=None):
    """Create separate willow stakes, woven branches and optional plaster band.

    axis='x' means a wall running along X with constant Y; axis='y' means
    a wall running along Y with constant X. Wattle is an infill proposal and
    is intentionally separate from the structural frame collection.
    """
    if end <= start:
        return
    if axis == "x":
        positions = []
        p = start + 0.08
        while p < end - 0.04:
            positions.append(p)
            p += 0.31
        for i, p in enumerate(positions, 1):
            add_cylinder(f"{name_prefix}_Willow_Stake_{i:02d}",
                         (p, fixed, (z0 + z1) / 2), 0.025, z1 - z0,
                         "Willow", "03_WATTLE_AND_MUD", vertices=8)
        for j, z in enumerate([z0 + 0.18 + k * 0.22 for k in range(8)], 1):
            if z < z1 - 0.04:
                add_cylinder_between(f"{name_prefix}_Woven_Branch_{j:02d}",
                                     (start, fixed - 0.025 * (j % 2), z),
                                     (end, fixed - 0.025 * (j % 2), z + 0.04 * (j % 2)),
                                     0.018, "Willow_Fresh", "03_WATTLE_AND_MUD",
                                     vertices=8)
        if plaster_band:
            low, high = plaster_band
            add_box(f"{name_prefix}_Mud_Plaster_Band", ((start + end) / 2, fixed,
                                                          (low + high) / 2),
                    (end - start - 0.08, 0.045, high - low),
                    "Mud_Plaster", "03_WATTLE_AND_MUD", bevel=0.012)
    else:
        positions = []
        p = start + 0.08
        while p < end - 0.04:
            positions.append(p)
            p += 0.31
        for i, p in enumerate(positions, 1):
            add_cylinder(f"{name_prefix}_Willow_Stake_{i:02d}",
                         (fixed, p, (z0 + z1) / 2), 0.025, z1 - z0,
                         "Willow", "03_WATTLE_AND_MUD", vertices=8)
        for j, z in enumerate([z0 + 0.18 + k * 0.22 for k in range(8)], 1):
            if z < z1 - 0.04:
                add_cylinder_between(f"{name_prefix}_Woven_Branch_{j:02d}",
                                     (fixed - 0.025 * (j % 2), start, z),
                                     (fixed - 0.025 * (j % 2), end, z + 0.04 * (j % 2)),
                                     0.018, "Willow_Fresh", "03_WATTLE_AND_MUD",
                                     vertices=8)
        if plaster_band:
            low, high = plaster_band
            add_box(f"{name_prefix}_Mud_Plaster_Band", (fixed, (start + end) / 2,
                                                          (low + high) / 2),
                    (0.045, end - start - 0.08, high - low),
                    "Mud_Plaster", "03_WATTLE_AND_MUD", bevel=0.012)


def create_walls_and_openings():
    z0 = PLINTH_H + 0.06
    z1 = EAVES_Z - 0.12

    # South wall: leave a practical 1.4 m service/animal gate opening.
    create_wattle_panel("Wattle_South_West", "x", 0.18, 0.25, 1.05, z0, z1,
                        exposed=True, plaster_band=(z0 + 0.05, 1.25))
    create_wattle_panel("Wattle_South_Mid", "x", 0.18, 2.55, 5.8, z0, z1,
                        exposed=True, plaster_band=(z0 + 0.05, 1.30))
    create_wattle_panel("Wattle_South_East", "x", 0.18, 7.0, 7.70, z0, z1,
                        exposed=True, plaster_band=(z0 + 0.05, 1.25))

    # North elevation is mostly wattle with a high ventilation band.
    create_wattle_panel("Wattle_North_A", "x", 4.82, 0.25, 3.55, z0, z1,
                        exposed=True, plaster_band=(z0 + 0.05, 1.12))
    create_wattle_panel("Wattle_North_B", "x", 4.82, 4.45, 7.70, z0, z1,
                        exposed=True, plaster_band=(z0 + 0.05, 1.12))
    add_box("North_High_Ventilation_Band", (4.0, 4.84, 2.22),
            (6.4, 0.045, 0.36), "Willow", "03_WATTLE_AND_MUD")

    # Gables: simpler woven infill, with plaster on the weather-facing lower half.
    create_wattle_panel("Wattle_West_Gable", "y", 0.18, 0.25, 4.75, z0, 2.30,
                        exposed=True, plaster_band=(z0 + 0.05, 1.24))
    create_wattle_panel("Wattle_East_Gable", "y", 7.82, 0.25, 4.75, z0, 2.30,
                        exposed=True, plaster_band=(z0 + 0.05, 1.24))

    # Main gate on the south side: framed timber leaf with a diagonal brace.
    add_box("Main_Animal_Access_Door", (1.80, 0.10, 1.42), (1.48, 0.12, 1.78),
            "Timber_Light", "03_WATTLE_AND_MUD", bevel=0.025)
    add_box("Main_Door_Frame_Left", (1.04, 0.12, 1.40), (0.14, 0.18, 2.02),
            "Timber_Walnut", "02_TIMBER_FRAME", bevel=0.02)
    add_box("Main_Door_Frame_Right", (2.56, 0.12, 1.40), (0.14, 0.18, 2.02),
            "Timber_Walnut", "02_TIMBER_FRAME", bevel=0.02)
    add_beam_between("Main_Door_Diagonal_Brace", (1.18, 0.02, 0.65),
                     (2.42, 0.02, 2.17), 0.08, 0.08, "Timber_Walnut",
                     "03_WATTLE_AND_MUD", bevel=0.012)
    add_text("Main_Door_Label", "MAIN ACCESS", (1.80, -0.12, 2.34), size=0.14,
             material="Annotation_Gold", coll_name="09_ANNOTATIONS",
             rotation=(radians(78), 0.0, 0.0))

    # Smaller cleaning/service door on the east wall.
    add_box("Service_Cleaning_Door", (7.87, 1.20, 1.22), (0.12, 1.25, 1.48),
            "Timber_Light", "03_WATTLE_AND_MUD", bevel=0.02)
    add_box("Service_Door_Frame_Top", (7.87, 1.20, 2.02), (0.18, 1.48, 0.14),
            "Timber_Walnut", "02_TIMBER_FRAME", bevel=0.02)


def add_partition_segment(name, start, end, height=PARTITION_H, gate=False):
    """Timber-railed movable partition; start/end are 3D points."""
    start = Vector(start)
    end = Vector(end)
    zbase = FLOOR_Z + 0.04
    add_beam_between(f"{name}_Bottom_Rail", (start.x, start.y, zbase),
                    (end.x, end.y, zbase), 0.10, 0.10, "Timber_Light",
                    "05_INTERNAL_FITTINGS", bevel=0.015)
    add_beam_between(f"{name}_Top_Rail", (start.x, start.y, zbase + height),
                    (end.x, end.y, zbase + height), 0.10, 0.10, "Timber_Light",
                    "05_INTERNAL_FITTINGS", bevel=0.015)
    length = (end - start).length
    pieces = max(2, int(length / 0.62))
    for i in range(pieces + 1):
        t = i / pieces
        p = start.lerp(end, t)
        add_box(f"{name}_Post_{i+1:02d}", (p.x, p.y, zbase + height / 2),
                (0.09, 0.09, height + 0.08), "Timber_Walnut",
                "05_INTERNAL_FITTINGS", bevel=0.012)
    if gate:
        mid = start.lerp(end, 0.5)
        add_box(f"{name}_Swing_Gate", (mid.x, mid.y, zbase + height * 0.50),
                (max(0.45, length * 0.42), 0.06, height * 0.82),
                "Timber_Light", "05_INTERNAL_FITTINGS", bevel=0.015)


def add_zone_label(name, text, x, y, width=1.4):
    label = add_text(name, text, (x, y, FLOOR_Z + 0.012), size=0.17,
                     material="Annotation_Gold", coll_name="09_ANNOTATIONS",
                     rotation=(0.0, 0.0, 0.0))
    label.data.space_character = 1.0
    return label


def create_internal_zoning():
    # Floor and bedding slabs.
    add_box("Covered_Floor_Slab", (SHED_L / 2, SHED_W / 2, FLOOR_Z - 0.045),
            (SHED_L - 0.08, SHED_W - 0.08, 0.09), "Clay_Light",
            "05_INTERNAL_FITTINGS", bevel=0.02)
    add_box("Dry_Bedding_Main_Area", (3.0, 2.0, FLOOR_Z + 0.012),
            (5.88, 3.88, 0.035), "Bedding", "05_INTERNAL_FITTINGS", bevel=0.02)

    # Exact provisional plan:
    # Main = x0..6 / y0..4 = 24 m²
    # Storage = x6..8 / y0..2.5 = 5 m²
    # Ram = x6..8 / y2.5..4.5 = 4 m²
    # Lambing = x0..4 / y4..5 = 4 m²
    # Isolation = x4..6 / y4..5 + x6..8 / y4.5..5 = 3 m² (L-shaped).
    add_partition_segment("Partition_Main_SouthEdge", (0.25, 4.0, 0), (6.0, 4.0, 0), gate=True)
    add_partition_segment("Partition_Store_Ram", (6.0, 2.5, 0), (8.0, 2.5, 0), gate=True)
    add_partition_segment("Partition_Ram_Isolation", (6.0, 4.5, 0), (8.0, 4.5, 0), gate=True)
    add_partition_segment("Partition_Lambing_Isolation", (4.0, 4.0, 0), (4.0, 5.0, 0), gate=True)
    add_partition_segment("Partition_Main_Side", (6.0, 0.25, 0), (6.0, 4.0, 0), gate=True)

    add_zone_label("Zone_Label_Main", "MAIN REST / FEED\n24 m²", 3.0, 2.0)
    add_zone_label("Zone_Label_Ram", "RAM\n4 m²", 7.0, 3.45)
    add_zone_label("Zone_Label_Lambing", "LAMBING\n4 m²", 2.0, 4.48)
    add_zone_label("Zone_Label_Isolation", "ISOLATION\n3 m²", 5.0, 4.48)
    add_zone_label("Zone_Label_Store", "DRY STORE\n5 m²", 7.0, 1.2)

    # Feed and equipment fittings.
    add_box("Feed_Trough_Main", (3.15, 0.48, FLOOR_Z + 0.30),
            (4.55, 0.42, 0.42), "Timber_Light", "05_INTERNAL_FITTINGS", bevel=0.05)
    add_box("Feed_Trough_Liner", (3.15, 0.48, FLOOR_Z + 0.53),
            (4.15, 0.24, 0.07), "Galvanized_Metal", "05_INTERNAL_FITTINGS", bevel=0.02)
    for i in range(8):
        add_box(f"Hay_Rack_Slat_{i+1:02d}", (1.15 + i * 0.50, 4.36, 1.22),
                (0.08, 0.08, 1.15), "Timber_Light", "05_INTERNAL_FITTINGS",
                bevel=0.015)
    add_box("Hay_Rack_Top", (2.90, 4.36, 1.82), (3.65, 0.10, 0.10),
            "Timber_Walnut", "05_INTERNAL_FITTINGS", bevel=0.015)

    # Dry-feed store: lockable raised shelves and a feed-bag placeholder.
    add_box("Feed_Store_Shelf_A", (6.45, 0.55, 1.05), (0.95, 1.45, 0.10),
            "Timber_Light", "05_INTERNAL_FITTINGS", bevel=0.015)
    add_box("Feed_Store_Shelf_B", (7.55, 0.55, 1.05), (0.35, 1.45, 0.10),
            "Timber_Light", "05_INTERNAL_FITTINGS", bevel=0.015)
    for i in range(3):
        add_box(f"Feed_Bag_{i+1:02d}", (6.55 + i * 0.38, 1.55, 0.76),
                (0.28, 0.40, 0.52), "Feed", "05_INTERNAL_FITTINGS", bevel=0.035)

    # Water trough inside the main zone; line is kept separate from dirty water.
    add_box("Clean_Water_Trough", (5.0, 3.42, FLOOR_Z + 0.24),
            (1.25, 0.35, 0.32), "Galvanized_Metal", "06_WATER_AND_WASTE", bevel=0.05)
    add_box("Clean_Water_Surface", (5.0, 3.42, FLOOR_Z + 0.41),
            (1.02, 0.18, 0.03), "Water_Blue", "06_WATER_AND_WASTE", bevel=0.01)


# -----------------------------------------------------------------------------
# OPEN YARD, WATER / WASTE, AND LANDSCAPE CONTEXT
# -----------------------------------------------------------------------------


def create_fence_line(prefix, start, end, height=1.25, spacing=1.65):
    start = Vector(start)
    end = Vector(end)
    length = (end - start).length
    count = max(1, int(length / spacing))
    for i in range(count + 1):
        p = start.lerp(end, i / count)
        add_box(f"{prefix}_Post_{i+1:02d}", (p.x, p.y, p.z + height / 2),
                (0.12, 0.12, height), "Fence_Wood", "08_LANDSCAPE", bevel=0.02)
    add_beam_between(f"{prefix}_Top_Rail", (start.x, start.y, start.z + height * 0.82),
                     (end.x, end.y, end.z + height * 0.82), 0.08, 0.08,
                     "Fence_Wood", "08_LANDSCAPE", bevel=0.015)
    add_beam_between(f"{prefix}_Mid_Rail", (start.x, start.y, start.z + height * 0.42),
                     (end.x, end.y, end.z + height * 0.42), 0.06, 0.06,
                     "Fence_Wood", "08_LANDSCAPE", bevel=0.015)


def create_open_yard():
    add_box("Open_Exercise_Yard_Surface", (SHED_L / 2, -2.5, 0.12),
            (YARD_L, YARD_W, 0.08), "Terrain_Light", "08_LANDSCAPE", bevel=0.05)
    # Loose bedding / compacted area near the shed; exterior drainage remains
    # beyond the south edge and falls away from the covered resting area.
    add_box("Yard_Compacted_Access_Band", (4.0, -0.45, 0.17), (7.5, 0.50, 0.10),
            "Stone_Light", "08_LANDSCAPE", bevel=0.03)
    create_fence_line("Yard_Fence_South", (0.0, -5.0, 0.20), (8.0, -5.0, 0.20))
    create_fence_line("Yard_Fence_West", (0.0, -5.0, 0.20), (0.0, -0.18, 0.20))
    create_fence_line("Yard_Fence_East", (8.0, -5.0, 0.20), (8.0, -0.18, 0.20))
    # Yard gate / latch.
    add_box("Yard_Access_Gate", (4.0, -4.98, 0.86), (1.35, 0.10, 1.15),
            "Timber_Light", "08_LANDSCAPE", bevel=0.02)
    add_beam_between("Yard_Gate_Brace", (3.40, -4.92, 0.34),
                     (4.60, -4.92, 1.38), 0.065, 0.065, "Timber_Walnut",
                     "08_LANDSCAPE", bevel=0.012)
    add_text("Yard_Label", "OPEN EXERCISE YARD\n8 × 5 m", (4.0, -2.55, 0.23),
             size=0.18, material="Annotation_Gold", coll_name="09_ANNOTATIONS")


def create_water_and_waste():
    # Drainage channel is a visible, shallow, separate route along the south edge.
    add_box("Clean_Gravel_Drain_Channel", (4.0, -0.58, 0.13), (7.4, 0.16, 0.12),
            "Stone_Dark", "06_WATER_AND_WASTE", bevel=0.025)
    add_text("Drain_Label", "DRAINAGE FALL →", (5.65, -0.86, 0.18), size=0.15,
             material="Safety_Red", coll_name="09_ANNOTATIONS")
    add_polyline("Dirty_Wash_Water_Route",
                  [(6.9, -0.62, 0.22), (9.0, -0.62, 0.22), (10.8, -2.2, 0.22)],
                  "Dirty_Water_Line", "06_WATER_AND_WASTE", bevel_depth=0.035)
    add_text("Dirty_Water_Label", "DIRTY / WASH WATER\nTO MANURE + COMPOST ZONE",
             (9.15, -1.15, 0.25), size=0.13, material="Safety_Red",
             coll_name="09_ANNOTATIONS")

    # Compost / manure pad is down-gradient and physically away from the tank.
    add_box("Manure_Compost_Pad", (11.0, -3.1, 0.14), (3.3, 2.4, 0.12),
            "Stone_Light", "06_WATER_AND_WASTE", bevel=0.035)
    for i, x in enumerate([10.15, 11.0, 11.85]):
        add_box(f"Compost_Bin_{i+1:02d}", (x, -3.1, 0.72), (0.72, 1.45, 1.10),
                "Timber_Light", "06_WATER_AND_WASTE", bevel=0.035)
        add_box(f"Compost_Bin_Top_{i+1:02d}", (x, -3.1, 1.30), (0.68, 1.35, 0.035),
                "Willow", "06_WATER_AND_WASTE", bevel=0.012)
    add_text("Compost_Label", "COVERED MANURE / COMPOST\nNO CLEAN-WATER CONNECTION",
             (11.0, -4.50, 0.23), size=0.15, material="Annotation_Gold",
             coll_name="09_ANNOTATIONS")

    # A blue clean-water route from tank to trough; deliberately ends at the shed.
    add_polyline("Clean_Water_Route",
                  [(9.25, 3.75, 1.85), (8.65, 3.75, 1.25), (7.75, 3.45, 0.82),
                   (5.0, 3.42, FLOOR_Z + 0.42)],
                  "Clean_Water_Line", "06_WATER_AND_WASTE", bevel_depth=0.04)
    add_text("Clean_Water_Label", "CLEAN WATER\nTANK → TROUGH", (7.45, 3.75, 1.65),
             size=0.14, material="Clean_Water_Line", coll_name="09_ANNOTATIONS")
    add_box("Trout_Water_Separation_Sign", (10.0, 0.7, 1.25), (1.5, 0.08, 1.4),
            "Timber_Light", "06_WATER_AND_WASTE", bevel=0.02)
    add_text("Trout_Separation_Sign_Text", "FISH WATER\nSEPARATE SYSTEM\nNO MANURE ENTRY", (10.0, 0.60, 1.30),
             size=0.13, material="Safety_Red", coll_name="09_ANNOTATIONS",
             rotation=(radians(90), 0.0, 0.0))


def create_tree(name, x, y, scale=1.0):
    z = 0.45 + 0.02 * y
    add_cylinder(f"{name}_Trunk", (x, y, z + 1.1 * scale), 0.12 * scale,
                 2.2 * scale, "Orchard_Trunk", "08_LANDSCAPE", vertices=10)
    add_beam_between(f"{name}_Branch_A", (x, y, z + 1.5 * scale),
                     (x + 0.65 * scale, y + 0.08, z + 2.1 * scale),
                     0.07 * scale, 0.07 * scale, "Orchard_Trunk", "08_LANDSCAPE")
    add_uv_sphere(f"{name}_Canopy_A", (x - 0.10 * scale, y, z + 2.35 * scale),
                  (0.95 * scale, 0.75 * scale, 0.78 * scale),
                  "Orchard_Leaf", "08_LANDSCAPE", segments=14, rings=8)
    add_uv_sphere(f"{name}_Canopy_B", (x + 0.62 * scale, y + 0.05, z + 2.12 * scale),
                  (0.62 * scale, 0.55 * scale, 0.55 * scale),
                  "Orchard_Leaf", "08_LANDSCAPE", segments=12, rings=6)


def create_mountains():
    # Abstract distant mountain silhouettes: contextual only, not a survey.
    for i, (x, y, radius, depth, mat) in enumerate([
        (-7.0, 14.0, 4.8, 6.0, "Mountain_Far"),
        (0.5, 16.0, 6.4, 7.5, "Mountain_Mid"),
        (9.0, 15.0, 5.2, 6.5, "Mountain_Far"),
    ], 1):
        bpy.ops.mesh.primitive_cone_add(vertices=7, radius1=radius, radius2=0.0,
                                        depth=depth, location=(x, y, depth / 2 - 0.2))
        obj = bpy.context.object
        obj.name = f"Distant_Mountain_{i:02d}"
        move_to_collection(obj, collection("08_LANDSCAPE"))
        obj.data.materials.append(MATERIALS[mat])


def create_landscape():
    create_tree("Orchard_Tree_01", -3.0, 8.0, 1.05)
    create_tree("Orchard_Tree_02", 0.0, 9.0, 0.85)
    create_tree("Orchard_Tree_03", 4.0, 9.3, 1.10)
    create_tree("Orchard_Tree_04", 8.2, 8.3, 0.90)
    create_tree("Orchard_Tree_05", 12.2, 7.8, 1.05)
    create_mountains()
    add_text("Context_Label", "CONCEPTUAL ORCHARD EDGE / MOUNTAIN CONTEXT",
             (1.6, 10.6, 0.38), size=0.17, material="Annotation_Gold",
             coll_name="09_ANNOTATIONS")


# -----------------------------------------------------------------------------
# LIVESTOCK SCALE PLACEHOLDERS
# -----------------------------------------------------------------------------


def create_sheep(name, location, scale=1.0, rotation_z=0.0):
    """Low-poly, editable scale placeholder — not a veterinary representation."""
    x, y, z = location
    body = add_uv_sphere(f"{name}_Body", (x, y, z + 0.52 * scale),
                         (0.62 * scale, 0.34 * scale, 0.40 * scale),
                         "White", "07_LIVESTOCK_SCALE", segments=12, rings=6)
    body.rotation_euler[2] = rotation_z
    head = add_uv_sphere(f"{name}_Head", (x + 0.52 * scale * cos(rotation_z),
                                            y + 0.52 * scale * sin(rotation_z),
                                            z + 0.68 * scale),
                         (0.25 * scale, 0.20 * scale, 0.23 * scale),
                         "White", "07_LIVESTOCK_SCALE", segments=10, rings=5)
    head.rotation_euler[2] = rotation_z
    for side in (-1, 1):
        leg_x = x - 0.32 * scale + side * 0.25 * scale
        for dy in (-0.18, 0.18):
            add_cylinder(f"{name}_Leg_{side}_{dy}", (leg_x, y + dy * scale, z + 0.22 * scale),
                         0.045 * scale, 0.45 * scale, "Orchard_Trunk",
                         "07_LIVESTOCK_SCALE", vertices=8)
    add_uv_sphere(f"{name}_Ear_A", (x + 0.66 * scale * cos(rotation_z) - 0.13,
                                      y + 0.66 * scale * sin(rotation_z) + 0.10,
                                      z + 0.78 * scale),
                  (0.12 * scale, 0.04 * scale, 0.06 * scale),
                  "White", "07_LIVESTOCK_SCALE", segments=8, rings=4)
    add_uv_sphere(f"{name}_Ear_B", (x + 0.66 * scale * cos(rotation_z) - 0.13,
                                      y + 0.66 * scale * sin(rotation_z) - 0.10,
                                      z + 0.78 * scale),
                  (0.12 * scale, 0.04 * scale, 0.06 * scale),
                  "White", "07_LIVESTOCK_SCALE", segments=8, rings=4)


def create_livestock():
    # Four placeholders inside and three in the yard give readable scale
    # without implying a final flock count or breed.
    for i, location in enumerate([(2.0, 1.55, FLOOR_Z), (3.4, 2.55, FLOOR_Z),
                                  (4.8, 1.75, FLOOR_Z), (2.6, 3.25, FLOOR_Z)], 1):
        create_sheep(f"Sheep_Inside_{i:02d}", location, scale=0.82,
                     rotation_z=0.2 * i)
    for i, location in enumerate([(2.0, -2.0, 0.18), (4.5, -3.25, 0.18),
                                  (6.1, -1.4, 0.18)], 1):
        create_sheep(f"Sheep_Yard_{i:02d}", location, scale=0.90,
                     rotation_z=-0.3 * i)
    add_text("Livestock_Note", "SCALE PLACEHOLDERS ONLY", (2.8, 2.45, 2.28),
             size=0.14, material="Annotation_Gold", coll_name="09_ANNOTATIONS")


# -----------------------------------------------------------------------------
# DIMENSIONS, NOTES, CAMERAS, AND LIGHTING
# -----------------------------------------------------------------------------


def add_dimension(name, start, end, offset, label, axis="x"):
    """Readable dimension line for the top-down study view."""
    start = Vector(start)
    end = Vector(end)
    if axis == "x":
        p1 = Vector((start.x, start.y + offset, start.z))
        p2 = Vector((end.x, end.y + offset, end.z))
        add_beam_between(f"{name}_Line", p1, p2, 0.014, 0.014,
                         "Annotation_Gold", "09_ANNOTATIONS")
        add_beam_between(f"{name}_Tick_A", (p1.x, p1.y - 0.10, p1.z),
                         (p1.x, p1.y + 0.10, p1.z), 0.014, 0.014,
                         "Annotation_Gold", "09_ANNOTATIONS")
        add_beam_between(f"{name}_Tick_B", (p2.x, p2.y - 0.10, p2.z),
                         (p2.x, p2.y + 0.10, p2.z), 0.014, 0.014,
                         "Annotation_Gold", "09_ANNOTATIONS")
        add_text(f"{name}_Text", label, ((p1.x + p2.x) / 2, p1.y + 0.15, p1.z + 0.02),
                 size=0.18, material="Annotation_Gold", coll_name="09_ANNOTATIONS")
    else:
        p1 = Vector((start.x + offset, start.y, start.z))
        p2 = Vector((end.x + offset, end.y, end.z))
        add_beam_between(f"{name}_Line", p1, p2, 0.014, 0.014,
                         "Annotation_Gold", "09_ANNOTATIONS")
        add_beam_between(f"{name}_Tick_A", (p1.x - 0.10, p1.y, p1.z),
                         (p1.x + 0.10, p1.y, p1.z), 0.014, 0.014,
                         "Annotation_Gold", "09_ANNOTATIONS")
        add_beam_between(f"{name}_Tick_B", (p2.x - 0.10, p2.y, p2.z),
                         (p2.x + 0.10, p2.y, p2.z), 0.014, 0.014,
                         "Annotation_Gold", "09_ANNOTATIONS")
        add_text(f"{name}_Text", label, (p1.x - 0.22, (p1.y + p2.y) / 2, p1.z + 0.02),
                 size=0.18, material="Annotation_Gold", coll_name="09_ANNOTATIONS",
                 rotation=(0.0, 0.0, radians(90)))


def create_plan_annotations():
    add_dimension("Dimension_Shed_Length", (0.0, 0.0, 0.06), (SHED_L, 0.0, 0.06),
                  -1.10, "8.00 m", axis="x")
    add_dimension("Dimension_Shed_Width", (0.0, 0.0, 0.06), (0.0, SHED_W, 0.06),
                  -1.10, "5.00 m", axis="y")
    add_dimension("Dimension_Yard_Length", (0.0, YARD_Y0, 0.06), (SHED_L, YARD_Y0, 0.06),
                  -0.65, "8.00 m", axis="x")
    add_dimension("Dimension_Yard_Width", (SHED_L, YARD_Y0, 0.06), (SHED_L, YARD_Y1, 0.06),
                  1.05, "5.00 m", axis="y")
    add_text("Plan_Title", "AMANAH FARM / PROVISIONAL SHEEP SHED PLAN", (4.0, 7.2, 0.10),
             size=0.24, material="Annotation", coll_name="09_ANNOTATIONS")
    add_text("Plan_Subtitle", "MANZNO, ANANTNAG · 8 × 5 m COVERED + 8 × 5 m OPEN YARD",
             (4.0, 6.75, 0.10), size=0.14, material="Annotation_Gold",
             coll_name="09_ANNOTATIONS")
    add_text("Plan_North", "N ↑", (-1.1, 6.0, 0.10), size=0.25,
             material="Annotation_Gold", coll_name="09_ANNOTATIONS")


def look_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def add_camera(name, location, target, lens=48):
    cam_data = bpy.data.cameras.new(name)
    cam = bpy.data.objects.new(name, cam_data)
    collection("10_CAMERAS_AND_LIGHTS").objects.link(cam)
    cam.location = location
    cam.data.lens = lens
    cam.data.sensor_width = 36
    look_at(cam, target)
    cam["view_target"] = tuple(target)
    return cam


def create_cameras():
    cameras = {}
    cameras["CAM_Main_Exterior"] = add_camera("CAM_Main_Exterior", (13.5, -13.5, 9.0),
                                               (3.9, 1.9, 1.65), lens=52)
    cameras["CAM_Opposite_Exterior"] = add_camera("CAM_Opposite_Exterior", (-7.5, 13.0, 7.4),
                                                   (4.0, 2.0, 1.6), lens=52)
    cameras["CAM_Interior_Animal_Eye"] = add_camera("CAM_Interior_Animal_Eye", (3.2, 1.1, 1.35),
                                                     (5.8, 3.65, 1.30), lens=38)
    cameras["CAM_Roof_Off_Cutaway"] = add_camera("CAM_Roof_Off_Cutaway", (13.8, -12.0, 12.0),
                                                  (4.0, 2.2, 0.75), lens=55)
    cameras["CAM_Top_Down_Floor_Plan"] = add_camera("CAM_Top_Down_Floor_Plan", (4.0, 2.2, 18.0),
                                                    (4.0, 1.2, 0.0), lens=52)
    cameras["CAM_Structural_Frame"] = add_camera("CAM_Structural_Frame", (12.8, -11.3, 8.2),
                                                  (4.0, 2.3, 1.85), lens=55)
    cameras["CAM_Foundation_Junction"] = add_camera("CAM_Foundation_Junction", (2.2, -2.0, 3.0),
                                                     (0.35, 0.18, 0.65), lens=62)
    cameras["CAM_Wattle_Mud_Closeup"] = add_camera("CAM_Wattle_Mud_Closeup", (2.3, 6.1, 2.15),
                                                   (2.1, 4.80, 1.55), lens=68)
    for cam in cameras.values():
        cam.hide_render = True
    return cameras


def create_lights():
    world = bpy.context.scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.16, 0.22, 0.19, 1.0)
        bg.inputs["Strength"].default_value = 0.35

    def add_area(name, location, energy, size, color, target):
        data = bpy.data.lights.new(name, type="AREA")
        data.energy = energy
        data.shape = "DISK"
        data.size = size
        data.color = color
        light = bpy.data.objects.new(name, data)
        collection("10_CAMERAS_AND_LIGHTS").objects.link(light)
        light.location = location
        look_at(light, target)
        return light

    def add_sun(name, rotation, energy, color):
        data = bpy.data.lights.new(name, type="SUN")
        data.energy = energy
        data.angle = radians(12)
        data.color = color
        light = bpy.data.objects.new(name, data)
        collection("10_CAMERAS_AND_LIGHTS").objects.link(light)
        light.rotation_euler = rotation
        return light

    add_sun("Sun_Himalayan_Daylight", (radians(28), radians(-22), radians(-32)),
            2.0, (1.0, 0.85, 0.68))
    add_area("Area_Key", (4.0, -8.0, 10.0), 1150, 8.0, (1.0, 0.78, 0.57), (4, 2, 1))
    add_area("Area_Fill", (-7.0, 7.0, 6.0), 700, 10.0, (0.55, 0.72, 1.0), (4, 2, 1.4))
    add_area("Area_Interior", (4.0, 2.5, 3.4), 420, 5.0, (1.0, 0.82, 0.60), (4, 2, 0.8))


# -----------------------------------------------------------------------------
# QUALITY CONTROL, EXPORTS, AND RENDERING
# -----------------------------------------------------------------------------


def calculate_qc():
    covered = SHED_L * SHED_W
    yard = YARD_L * YARD_W
    zones_total = sum(ZONES.values())
    pitch = math.degrees(math.atan2(RIDGE_Z - EAVES_Z, SHED_W / 2))
    sheep_area_per_head_10 = ZONES["Main_Sheep_Resting_Feeding"] / 10.0
    sheep_area_per_head_12 = ZONES["Main_Sheep_Resting_Feeding"] / 12.0
    checks = {
        "covered_footprint_m2": covered,
        "open_yard_m2": yard,
        "covered_plus_yard_m2": covered + yard,
        "internal_zones_total_m2": zones_total,
        "internal_zones_fit_exactly": abs(zones_total - covered) < 1e-6,
        "eaves_height_m": EAVES_Z,
        "ridge_height_m": RIDGE_Z,
        "roof_pitch_degrees": round(pitch, 2),
        "roof_pitch_approx_30_degrees": abs(pitch - 30.0) <= 5.0,
        "main_resting_area_m2": ZONES["Main_Sheep_Resting_Feeding"],
        "main_area_per_sheep_at_10_head_m2": sheep_area_per_head_10,
        "main_area_per_sheep_at_12_head_m2": sheep_area_per_head_12,
        "welfare_note": "At 12 head, 2.0 m²/head is before subtracting feeders, partitions and circulation; confirm local sheep welfare guidance and flock size.",
        "technical_status": "DESIGN-DEVELOPMENT MODEL — NOT CONSTRUCTION-READY",
    }
    return checks


def write_project_documents():
    qc = calculate_qc()
    with open(OUTPUT_DIR / "qc_report.json", "w", encoding="utf-8") as handle:
        json.dump(qc, handle, indent=2)

    schedule = [
        ("Foundation_Stone", "Local stone masonry plinth", "Stone + mortar", "Preliminary; foundation and bearing design by engineer"),
        ("Timber_Frame", "Posts, beams, wall plates, braces, rafters", "Locally graded timber", "Member sizes/connections to be checked for snow, wind and seismic loads"),
        ("Wattle_Infill", "Willow stakes and woven branches", "Willow", "Non-load-bearing infill proposal"),
        ("Mud_Plaster_Band", "Partial clay-and-straw weathering layer", "Clay + straw", "Confirm moisture detailing, drying and maintenance"),
        ("Roof_Corrugated", "Pitched metal roof with overhang", "Corrugated coated metal", "Confirm snow load, corrosion protection and fixings"),
        ("Roof_Insulation", "Optional internal insulation layer", "Natural-fibre or approved board", "Confirm vapour/condensation strategy"),
        ("Rainwater_System", "Gutters, downpipes, storage tank", "Galvanized metal + tank", "Confirm potable/non-potable use and overflow"),
        ("Internal_Partitions", "Movable sheep, ram, lambing and isolation pens", "Timber rails", "Confirm animal handling and cleaning clearances"),
        ("Feeding_Fittings", "Troughs, hay rack and dry store", "Timber + galvanized metal", "Confirm safe edges and feed hygiene"),
        ("Waste_System", "Drain, manure pad and compost bins", "Stone + timber", "Keep dirty route separate from clean water and any fish system"),
        ("Yard_Fence", "Open exercise yard perimeter and gate", "Timber", "Confirm gate latch and predator protection"),
    ]
    with open(OUTPUT_DIR / "component_schedule.csv", "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["Component", "Role", "Proposed material", "Review note"])
        writer.writerows(schedule)

    assumptions = f"""AMANAH FARM — DESIGN ASSUMPTIONS AND OUTSTANDING TECHNICAL QUESTIONS
Location: {LOCATION}
Model status: architectural design-development study; not a certified construction drawing.

DIMENSIONS USED
- Covered shed: {SHED_L:.2f} m × {SHED_W:.2f} m = {qc['covered_footprint_m2']:.2f} m².
- Open exercise yard: {YARD_L:.2f} m × {YARD_W:.2f} m = {qc['open_yard_m2']:.2f} m².
- Raised stone plinth: {PLINTH_H:.2f} m above conceptual adjacent grade.
- Eaves: {EAVES_Z:.2f} m; ridge: {RIDGE_Z:.2f} m; calculated roof pitch: {qc['roof_pitch_degrees']:.2f}°.
- Internal provisional zones total exactly {qc['internal_zones_total_m2']:.2f} m².

FUNCTIONAL / WELFARE CAVEATS
- The main resting/feeding zone is 24 m²: 2.40 m²/head at 10 sheep and 2.00 m²/head at 12 sheep before subtracting feeders, partitions and circulation.
- Confirm whether the intended flock includes pregnant ewes, lambs, a ram, or isolation capacity; welfare density and pen sizes may need adjustment.
- Confirm door widths, turning clearances, handling route, bedding depth, cleaning access and emergency exit with a livestock specialist or veterinarian.

CLIMATE / STRUCTURAL QUESTIONS
- Commission a local topographic survey and soil bearing / drainage assessment.
- Engineer stone foundation depth, footing width, damp-proof separation and timber anchors.
- Verify snow, wind and seismic actions for the actual Anantnag site; the 30° roof is only a starting point.
- Confirm timber grade, moisture content, preservative treatment, fire performance and all post/beam/rafter connections.
- Confirm corrugated roof gauge, fixings, corrosion protection, snow guards, overhangs and gutter sizing.
- Validate condensation control, insulation, vapour movement and high-level ventilation in cold wet seasons.

WATER / WASTE / BIOSECURITY QUESTIONS
- Confirm clean water source, tank sizing, freeze protection and livestock trough hygiene.
- Keep manure, dirty wash water and compost leachate physically separated from any clean-water system.
- No manure or dirty water is connected to any proposed trout raceway supply.
- Design a covered manure/compost pad with an approved leachate and stormwater strategy.
- Review biosecurity, isolation pen protocol, rodent/predator control and cleaning chemicals.

MATERIAL / MAINTENANCE QUESTIONS
- Test local stone, willow, clay and straw samples for durability, moisture and repair cycles.
- Confirm whether exposed wattle can dry adequately on each elevation; use more plaster or a ventilated rainscreen where needed.
- Detail insect, rodent and livestock-impact protection at the base of wattle infill.
- Confirm local craftspeople, procurement lead times and repair/replacement strategy.

MODELLING LIMITATION
The sheep, terrain, orchard and mountains are scale/context placeholders. No precise site elevations, soil conditions, structural capacities, veterinary approvals or planning permissions are invented by this model.
"""
    (OUTPUT_DIR / "design_assumptions_and_questions.txt").write_text(assumptions, encoding="utf-8")


def configure_scene():
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.length_unit = "METERS"
    scene.unit_settings.scale_length = 1.0
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.filepath = str(RENDER_DIR / "CAM_Main_Exterior.png")
    try:
        engine_ids = {item.identifier for item in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items}
        scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in engine_ids else "BLENDER_EEVEE"
    except Exception:
        scene.render.engine = "BLENDER_EEVEE"
    scene.render.image_settings.color_depth = "8"
    scene.render.resolution_percentage = 100
    try:
        available_looks = [item.name for item in bpy.types.ColorManagedViewSettings.bl_rna.properties["look"].enum_items]
        if "AgX - Medium High Contrast" in available_looks:
            scene.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        pass
    scene["project_name"] = PROJECT_NAME
    scene["location"] = LOCATION
    scene["model_status"] = "Design-development model; not construction-ready."
    scene["covered_area_m2"] = SHED_L * SHED_W
    scene["yard_area_m2"] = YARD_L * YARD_W
    scene["zone_total_m2"] = sum(ZONES.values())


def set_collection_render_visibility(collection_name, visible):
    coll = bpy.data.collections.get(collection_name)
    if coll:
        coll.hide_render = not visible


def render_one(camera, filename, hidden_collections=None):
    hidden_collections = hidden_collections or []
    original = {}
    for name in hidden_collections:
        coll = bpy.data.collections.get(name)
        if coll:
            original[name] = coll.hide_render
            coll.hide_render = True
    for item in bpy.data.objects:
        if item.type == "CAMERA":
            item.hide_render = item != camera
    camera.hide_render = False
    bpy.context.scene.camera = camera
    bpy.context.scene.render.filepath = str(RENDER_DIR / filename)
    bpy.ops.render.render(write_still=True)
    for name, value in original.items():
        bpy.data.collections[name].hide_render = value
    for item in bpy.data.objects:
        if item.type == "CAMERA":
            item.hide_render = True


def render_views(cameras):
    view_jobs = [
        ("CAM_Main_Exterior", "01_main_three_quarter.png", []),
        ("CAM_Opposite_Exterior", "02_opposite_exterior.png", []),
        ("CAM_Interior_Animal_Eye", "03_interior_animal_eye.png", ["04_ROOF_AND_RAINWATER"]),
        ("CAM_Roof_Off_Cutaway", "04_roof_off_cutaway.png", ["04_ROOF_AND_RAINWATER", "08_LANDSCAPE"]),
        ("CAM_Top_Down_Floor_Plan", "05_dimensioned_floor_plan.png", ["04_ROOF_AND_RAINWATER", "07_LIVESTOCK_SCALE"]),
        ("CAM_Structural_Frame", "06_structural_frame.png", ["03_WATTLE_AND_MUD", "04_ROOF_AND_RAINWATER", "05_INTERNAL_FITTINGS", "06_WATER_AND_WASTE", "07_LIVESTOCK_SCALE", "08_LANDSCAPE"]),
        ("CAM_Foundation_Junction", "07_foundation_junction.png", ["03_WATTLE_AND_MUD", "04_ROOF_AND_RAINWATER", "05_INTERNAL_FITTINGS", "06_WATER_AND_WASTE", "07_LIVESTOCK_SCALE", "08_LANDSCAPE"]),
        ("CAM_Wattle_Mud_Closeup", "08_wattle_mud_closeup.png", ["04_ROOF_AND_RAINWATER", "05_INTERNAL_FITTINGS", "06_WATER_AND_WASTE", "07_LIVESTOCK_SCALE", "08_LANDSCAPE"]),
    ]
    for cam_name, filename, hidden in view_jobs:
        render_one(cameras[cam_name], filename, hidden)


def export_geometry():
    blend_path = OUTPUT_DIR / "amanah_farm_sheep_shed.blend"
    if SAVE_BLEND:
        bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    # Blender 4.x uses wm.obj_export; Blender 3.x uses export_scene.obj.
    obj_path = OUTPUT_DIR / "amanah_farm_sheep_shed.obj"
    try:
        bpy.ops.wm.obj_export(filepath=str(obj_path), export_materials=True,
                              export_normals=True, export_uv=True)
    except Exception:
        try:
            bpy.ops.export_scene.obj(filepath=str(obj_path), use_materials=True,
                                     use_normals=True, use_uvs=True)
        except Exception as exc:
            (OUTPUT_DIR / "obj_export_error.txt").write_text(str(exc), encoding="utf-8")

    glb_path = OUTPUT_DIR / "amanah_farm_sheep_shed.glb"
    try:
        bpy.ops.export_scene.gltf(filepath=str(glb_path), export_format="GLB",
                                  export_materials="EXPORT",
                                  export_cameras=False, export_lights=False)
    except Exception as exc:
        (OUTPUT_DIR / "glb_export_error.txt").write_text(str(exc), encoding="utf-8")


def build_model():
    clear_scene()
    make_materials()
    configure_scene()
    for name in COLLECTION_NAMES:
        collection(name)

    create_terrain()
    create_stone_plinth()
    create_timber_frame()
    create_roof_and_rainwater()
    create_walls_and_openings()
    create_internal_zoning()
    create_open_yard()
    create_water_and_waste()
    create_landscape()
    create_livestock()
    create_plan_annotations()
    cameras = create_cameras()
    create_lights()
    write_project_documents()

    if EXPORT_GEOMETRY:
        export_geometry()
    if RENDER_VIEWS:
        render_views(cameras)
    bpy.context.scene.camera = cameras["CAM_Main_Exterior"]
    if SAVE_BLEND:
        # Save once more after render settings and all visibility states have
        # returned to their editable default state.
        bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_DIR / "amanah_farm_sheep_shed.blend"))

    print("\nAMANAH FARM MODEL COMPLETE")
    print(f"Output folder: {OUTPUT_DIR}")
    print(json.dumps(calculate_qc(), indent=2))


if __name__ == "__main__":
    build_model()
