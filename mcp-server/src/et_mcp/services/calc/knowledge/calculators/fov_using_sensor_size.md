---
id: fov_using_sensor_size

category: optics

tags:
  - fov
  - field_of_view
  - coverage
  - visible_area
  - sensor_size
  - sensor_size_mm
  - sensor_width_mm
  - sensor_height_mm
  - sensor_diagonal_mm
  - lens
  - camera
  - optical_geometry
  - imaging_geometry
  - machine_vision
  - single_axis_fov
  - horizontal_fov
  - vertical_fov
  - diagonal_fov
  - quick_fov
  - simple_fov
  - fov_from_sensor
  - how_much_can_see
  - coverage_calculation
  - inspection_width
  - view_width
  - field_width
  - visible_width
  - area_scan
  - camera_coverage
  - lens_selection

required_inputs:
  - sensor_size_mm
  - focal_length_mm
  - working_distance_mm

optional_inputs: []

description: "Calculate FOV for one sensor axis from physical sensor size (mm), focal length, and working distance"
chain_note: "Use sensor_geometry first if you have pixel count and pixel pitch but not sensor_size_mm"
---

# Purpose

Calculate field of view for one sensor axis (width, height, or diagonal) given the physical sensor dimension in millimeters, lens focal length, and working distance. Simpler and faster than fov_using_pixel_size when the sensor's physical size is already known.

This is the right calculator when someone says "my sensor is 8.8 mm wide" or "I have a 2/3-inch sensor" (with the physical width already converted to mm) rather than specifying resolution and pixel pitch.

# Explanation

Applies the standard thin-lens FOV formula:

  ratio = working_distance_mm / focal_length_mm
  fov_mm = sensor_size_mm × (ratio − 1)

This is a single-axis calculation. Call it once for the horizontal dimension and again for the vertical if both are needed — or use fov_using_pixel_size which returns all three axes in one call.

The formula assumes the thin-lens model. The (ratio − 1) term is the magnification factor: it represents how much the image space (sensor) maps to object space. At infinite working distance it approaches ratio = ∞, meaning FOV grows without bound. At working_distance = focal_length, magnification = 0 and FOV = 0 (physically invalid).

# Use Cases

- Quick FOV check when sensor datasheet gives physical dimensions directly.
- Evaluate different lenses against a fixed sensor size.
- Calculate diagonal FOV by passing sensor_diagonal_mm as sensor_size_mm.
- Estimate camera coverage when spec sheet lists sensor format in mm rather than pixel count.
- First-pass camera layout planning before committing to a specific sensor model.
- Verify a lens–sensor combination meets project FOV requirements.
- Calculate FOV for each camera axis separately when aspect ratio effects need to be understood.
- Compute FOV for a legacy camera where pixel size is not documented.
- Teaching or explaining the optical formula with physical sensor dimensions.

# Example Queries

- What field of view will I get with this lens?
- Sensor width is 8.8 mm, what is the FOV at 500 mm?
- Calculate visible width at 500 mm working distance.
- What is the FOV at this working distance?
- How much width will the camera see?
- FOV for a 1/1.8 inch sensor with a 12 mm lens at 400 mm.
- Sensor is 11.3 mm wide, 16 mm lens, 600 mm distance — what is the FOV?
- What coverage do I get with a 35 mm lens at 2 meters?
- My sensor diagonal is 15.86 mm — what is the diagonal FOV?
- How wide is the field of view at 300 mm working distance?
- I have a 2/3 inch sensor (8.8 mm wide) — what does 25 mm lens give me?
- FOV for sensor size 6.4 × 4.8 mm with a 16 mm lens.
- What is the horizontal FOV for my camera?
- Will a 250 mm part fit in the frame?
- What focal length gives me 400 mm FOV with this sensor?

# Input Meanings

sensor_size_mm:
Physical size of the sensor dimension being evaluated, in millimeters. Pass sensor_width_mm for horizontal FOV, sensor_height_mm for vertical FOV, or sensor_diagonal_mm for diagonal FOV. Common sensor widths by format: 1/4" ≈ 3.2 mm, 1/3" ≈ 4.8 mm, 1/2" ≈ 6.4 mm, 1/1.8" ≈ 7.2 mm, 2/3" ≈ 8.8 mm, 1" ≈ 12.8 mm, 4/3" ≈ 17.3 mm. Note: sensor "inch" sizes are format designators with non-obvious mm equivalences — look up the actual physical dimension on the datasheet when available.

focal_length_mm:
Lens focal length in millimeters. Use the nominal value from the lens datasheet. Common values in machine vision: 6, 8, 12, 16, 25, 35, 50 mm.

working_distance_mm:
Distance from the lens front principal plane to the target object in millimeters. Must be greater than focal_length_mm; must be meaningfully greater in practice. Cannot be negative or zero.

# Gotchas

- This calculator does one axis at a time. For horizontal and vertical FOV together, either call it twice or use fov_using_pixel_size.
- Sensor "inch" designations (1/2", 2/3", 1") are not direct physical measurements. A 2/3" sensor is not 16.9 mm wide — it is approximately 8.8 mm wide. Always look up the actual mm value.
- working_distance_mm must exceed focal_length_mm significantly (practical minimum ≈ 1.2× focal length for macro, typically 3–20× for normal machine vision). If working_distance ≤ focal_length, the result will be zero or negative — physically impossible.
- The calculator has built-in limits: sensor_size_mm must be < 200 mm and focal_length_mm must be < 2000 mm. Results outside 2–50000 mm FOV are flagged as out of range.
- This formula gives the FOV at exactly the focal plane. Objects closer or farther than working_distance will appear larger or smaller respectively.
- Does not account for lens distortion. Wide-angle lenses (< 8 mm) can deviate significantly from the thin-lens model at image edges.

# Related Calculators

- fov_using_pixel_size: Use when sensor is specified by resolution (pixels) and pixel size (µm) rather than physical mm. Returns horizontal, vertical, and diagonal FOV in one call.
- working_distance_using_sensor_size: The inverse — given desired FOV and sensor size, find required working distance.
- focal_length: Another inverse — given desired FOV, working distance, and sensor size, find the required focal length.
- sensor_geometry: Converts pixel count + pixel pitch to physical mm — use it first to get sensor_size_mm when only resolution and pixel size are known.
