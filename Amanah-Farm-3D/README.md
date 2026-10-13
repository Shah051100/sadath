# Amanah Farm — Manzno Sheep Shed 3D Model

Parametric Blender model generator for a climate-responsive, low-cost sheep shed in Manzno village, Anantnag, Kashmir.

## What is included

- `amanah_farm_model.py` — complete Blender Python generator
- `component_schedule.csv` — preliminary component/material schedule
- `design_assumptions_and_questions.txt` — dimensions, welfare caveats, and technical review questions
- `qc_report.json` — dimensional checks performed by the generator

Running the script creates an `amanah_farm_outputs/` folder containing:

- `amanah_farm_sheep_shed.blend`
- `amanah_farm_sheep_shed.obj`
- `amanah_farm_sheep_shed.glb`
- `component_schedule.csv`
- `design_assumptions_and_questions.txt`
- `qc_report.json`
- `renders/01_main_three_quarter.png`
- `renders/02_opposite_exterior.png`
- `renders/03_interior_animal_eye.png`
- `renders/04_roof_off_cutaway.png`
- `renders/05_dimensioned_floor_plan.png`
- `renders/06_structural_frame.png`
- `renders/07_foundation_junction.png`
- `renders/08_wattle_mud_closeup.png`

## Run in Blender

### Blender UI

1. Install Blender 3.6 LTS or a current Blender 4.x release.
2. Open Blender.
3. Open the **Scripting** workspace.
4. Click **Open** and select `amanah_farm_model.py`.
5. Press **Run Script**.
6. Wait for the scene and the eight study renders to finish.
7. Open the `amanah_farm_outputs` folder beside the script to inspect exports and renders.

### Command line

From this folder:

```bash
blender --background --python amanah_farm_model.py
```

To build only the editable scene while iterating, edit the settings near the top of the script:

```python
RENDER_VIEWS = False
EXPORT_GEOMETRY = False
SAVE_BLEND = True
```

## Model navigation

The scene is separated into collections for:

- site terrain
- stone foundation and damp-proof course
- timber frame and bracing
- willow wattle and mud plaster
- pitched roof, insulation, gutters and rainwater
- internal fittings and partitions
- clean water and dirty-water routes
- livestock scale placeholders
- orchard, path, fence and mountain context
- annotations
- cameras and lights

The required cameras are created as named objects: main exterior, opposite exterior, interior animal eye level, roof-off cutaway, top-down plan, structural frame, foundation junction, and wattle/mud close-up.

## Important professional limitations

This is a dimensionally coherent design-development model, not a certified construction drawing. It intentionally does **not** invent soil bearing capacity, surveyed elevations, snow load, wind load, seismic resistance, timber grading, veterinary approvals, planning permissions, or construction-safe structural connections.

Before construction, obtain local review for foundation depth and reinforcement, damp-proofing, timber joints, snow and wind actions, seismic detailing, roof fixings, drainage, condensation control, fire safety, animal welfare, biosecurity, and veterinary requirements. The 24 m² main sheep area provides 2.40 m²/head at 10 sheep and 2.00 m²/head at 12 sheep before subtracting feeders, partitions, bedding and circulation; confirm the final flock and welfare standard locally.
