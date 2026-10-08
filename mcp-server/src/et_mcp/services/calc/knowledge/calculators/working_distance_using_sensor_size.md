---
id: working_distance_using_sensor_size

category: optics

tags:
  - working_distance
  - mounting_distance
  - object_distance
  - stand_off_distance
  - standoff
  - wd
  - camera_distance
  - sensor_size
  - sensor_size_mm
  - lens
  - fov
  - field_of_view
  - object_size
  - coverage
  - imaging_geometry
  - optical_geometry
  - machine_vision
  - camera_mounting
  - camera_placement
  - camera_height
  - mounting_height
  - how_far_camera
  - where_to_mount
  - inverse_fov
  - back_calculate
  - simple_working_distance
  - quick_wd

required_inputs:
  - object_size_mm
  - sensor_size_mm
  - focal_length_mm

optional_inputs: []

description: "Find camera mounting distance to image a given object size, using physical sensor size (mm) and focal length"
chain_note: "Use sensor_geometry first if you have pixel count and pixel pitch but not sensor_size_mm"
---

# Purpose

Calculate the required working distance (camera-to-object distance) to image a given object size, using known physical sensor dimension and lens focal length.

This is the simpler working distance calculator — use it when the sensor's physical size in mm is already known (from the datasheet or computed by sensor_geometry) and you don't want to supply resolution and pixel pitch. It does a single-axis calculation: pass object width and sensor width for horizontal, or object height and sensor height for vertical.

# Explanation

Rearranges the thin-lens magnification formula:

  magnification_term = object_size_mm / sensor_size_mm
  working_distance_mm = focal_length_mm × (magnification_term + 1)

Equivalently: working_distance = focal_length × (object_size / sensor_size + 1)

The ratio object_size / sensor_size is the demagnification factor — how many times larger the object is than the sensor. A 300 mm object on an 8.8 mm sensor has a demagnification of ~34×. The working distance is the focal length scaled by that demagnification factor plus one.

# Use Cases

- Determine mounting distance to capture a full product width on a known sensor.
- Quick working distance estimate from a lens and sensor datasheet, no pixel-level data needed.
- Plan camera placement when sensor physical dimensions are already known.
- Evaluate whether a camera fits inside a machine enclosure (check if working distance is achievable).
- Calculate where to mount a camera to image a PCB, tray, pallet, or flat object.
- Compare working distance requirements across different focal lengths for the same sensor and object size.
- Compute working distance for each axis (pass sensor width + object width, then sensor height + object height).
- First-pass layout before detailed optical design.
- Determine if a standard lens focal length achieves a practical working distance for a given inspection area.

# Example Queries

- How far should the camera be from the object?
- What working distance is required for a 300 mm wide object?
- Where should I mount the camera?
- Required distance for 300 mm object width with an 8.8 mm sensor and 16 mm lens.
- Determine mounting distance from lens geometry.
- My object is 500 mm wide, sensor is 11.3 mm, lens is 25 mm — what is the working distance?
- Calculate camera position for imaging a 200 mm part.
- How far back do I need to put the camera to see the whole part?
- Sensor is 2/3 inch (8.8 mm wide), object is 400 mm wide, 12 mm lens — how far?
- What is the WD for a 1-inch sensor imaging a 600 mm belt?
- Camera stand-off distance for 250 mm object with 35 mm lens.
- How much clearance do I need between camera and product?
- I need to image a 450 mm pallet — what is the mounting height with a 50 mm lens?
- Working distance for a 16 mm lens on a sensor with 7.2 mm width viewing a 300 mm object.

# Input Meanings

object_size_mm:
Physical size of the object (or desired FOV) to be captured in the evaluated axis, in millimeters. For horizontal: use object width. For vertical: use object height. This is what you want to see — not the sensor size.

sensor_size_mm:
Physical sensor dimension in the same axis, in millimeters. For horizontal FOV: use sensor width. For vertical: use sensor height. Common sensor widths: 2/3" ≈ 8.8 mm, 1" ≈ 12.8 mm, 4/3" ≈ 17.3 mm. If only pixel count and pixel size are known, use sensor_geometry first to derive this value.

focal_length_mm:
Lens focal length in millimeters. Use the nominal value from the lens datasheet.

# Gotchas

- This calculator has built-in limits from the original calculator it ports: sensor_size_mm must be < 200 mm and focal_length_mm must be ≤ 2000 mm. Results are also limited to the range 50–500000 mm working distance.
- object_size_mm and sensor_size_mm must be in the same axis (both horizontal, or both vertical). Mixing axes gives a geometrically meaningless result.
- The result is the working distance at the focal plane. If the object is not flat or is at varying distances, effective coverage changes.
- A shorter focal length lens reduces the required working distance. A longer focal length increases it. If the working distance is too short for the machine envelope, switch to a shorter focal length.
- If pixel count and pixel size are known but sensor physical size is not, run sensor_geometry first to get sensor_size_mm.
- This is a single-axis calculator. For full 2D coverage verification, run it twice — once for width and once for height. Or use working_distance_using_pixel_size which computes both axes in one call.
- Rounding: working distance is returned rounded to 1 decimal place (to match original JS calculator behavior).

# Related Calculators

- working_distance_using_pixel_size: Use when sensor is specified by pixel count and pixel size instead of physical mm. Also returns both axes and sensor geometry in one call.
- fov_using_sensor_size: The inverse — given working distance, compute FOV.
- fov_using_pixel_size: The most complete forward calculator — FOV from pixel count, pixel size, focal length, and WD.
- focal_length: Given desired FOV, working distance, and sensor size — find the required focal length.
- sensor_geometry: Converts pixel count + pixel pitch to physical mm dimensions needed as input here.
