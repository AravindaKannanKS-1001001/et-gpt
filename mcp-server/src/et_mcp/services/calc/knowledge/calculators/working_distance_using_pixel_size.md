---
id: working_distance_using_pixel_size

category: optics

tags:
  - working_distance
  - mounting_distance
  - camera_distance
  - object_distance
  - stand_off_distance
  - standoff
  - wd
  - pixel_size
  - pixel_pitch
  - pixel_size_um
  - resolution
  - width_pixels
  - height_pixels
  - fov
  - field_of_view
  - desired_fov
  - target_fov
  - fov_x
  - sensor
  - imaging_geometry
  - optical_geometry
  - machine_vision
  - camera_mounting
  - camera_placement
  - camera_position
  - how_far_camera
  - camera_height
  - mounting_height
  - bracket_distance
  - where_to_mount
  - inverse_fov
  - back_calculate

required_inputs:
  - width_pixels
  - height_pixels
  - pixel_size_um
  - focal_length_mm
  - fov_x_mm

optional_inputs: []

description: "Find camera mounting distance to achieve a target horizontal FOV, given sensor resolution, pixel pitch, and focal length"
---

# Purpose

Calculate the working distance required to achieve a specific horizontal field of view, given sensor resolution (pixels), pixel pitch, and lens focal length. Also returns derived sensor geometry and all three FOV axes at the computed working distance.

This is the inverse of fov_using_pixel_size. Use it when the desired coverage width is the starting requirement — "I need to see 400 mm wide" — and you want to find the camera mounting distance for a camera specified by resolution and pixel pitch.

# Explanation

Stage 1 — Sensor geometry: same as fov_using_pixel_size.
  sensor_width_mm = width_pixels × pixel_size_um / 1000

Stage 2 — Inverse optical formula: rearranges the thin-lens formula to solve for working distance.
  working_distance_mm = focal_length_mm × (fov_x_mm / sensor_width_mm + 1)

The formula drives from the horizontal FOV requirement. Vertical and diagonal FOV are then derived from the sensor aspect ratio:
  fov_y_mm = fov_x_mm / (width_pixels / height_pixels)
  fov_diagonal_mm = sqrt(fov_x_mm² + fov_y_mm²)

# Use Cases

- Determine camera mounting height for a conveyor inspection system where FOV width is specified by the conveyor belt width.
- Find the stand-off distance for a fixed-mount camera above a production line.
- Plan camera bracket position when the required coverage area is defined first.
- Verify that a specific camera and lens combination can achieve the required coverage at a physically feasible mounting distance.
- Compare mounting distance requirements for different lens focal lengths against a required FOV.
- Design robot-mounted vision systems where end-effector distance to object is constrained.
- Determine camera height for overhead inspection of pallets, trays, or flat objects.
- Back-calculate mounting distance from a specified FOV during system quotation.
- Check whether a desired FOV is achievable given mechanical constraints on where the camera can be mounted.

# Example Queries

- How far away should the camera be for 400 mm horizontal FOV?
- What working distance gives me 300 mm coverage width?
- Camera is 2448×2048, 3.45 µm pixels, 16 mm lens — how far back do I mount it for 350 mm FOV?
- Find mounting distance from desired coverage width of 500 mm.
- Required working distance for this sensor with 200 mm desired FOV.
- I need to see 600 mm wide — where do I put the camera?
- My conveyor is 400 mm wide — how high should the camera be?
- What is the mounting height for a 5 MP camera with 25 mm lens to see 300 mm?
- I need 250 mm FOV with a Basler camera 2448×2048 at 3.45 µm — calculate working distance.
- How far should I mount the camera if I need to inspect a 500 mm part?
- Determine standoff distance to cover a 450 mm inspection area.
- If I need 200 mm wide FOV with a 12 mm lens and 2448×2048 sensor — what WD?

# Input Meanings

width_pixels:
Sensor width in pixels. From camera datasheet as horizontal resolution. Example: 2448.

height_pixels:
Sensor height in pixels. From camera datasheet as vertical resolution. Needed to derive vertical and diagonal FOV. Example: 2048.

pixel_size_um:
Physical size of one sensor pixel in micrometers (µm). Also called pixel pitch. Found on camera or sensor datasheet. Common values: 2.74 µm, 3.45 µm, 4.8 µm, 5.5 µm, 5.86 µm.

focal_length_mm:
Lens focal length in millimeters. The nominal value from the lens datasheet.

fov_x_mm:
Desired horizontal field of view in millimeters. This is the target coverage width that drives the calculation. Must match the horizontal (width) axis of the sensor.

# Gotchas

- fov_x_mm must be the horizontal (width) FOV — it must be ≥ fov_y_mm (the vertical FOV derived from aspect ratio). If you accidentally pass the vertical or a smaller dimension as fov_x_mm, the result is flagged invalid with a warning: "FOV X must be greater than or equal to FOV Y."
- The computed working distance grows with fov_x_mm and focal_length_mm. A very large desired FOV with a long focal length can produce an unrealistically large working distance.
- Results are physically valid only when working distance > focal_length_mm. If fov_x_mm is very small relative to the sensor size, the formula may produce a working distance close to focal length — check validity.
- If sensor_size_mm is already known, use working_distance_using_sensor_size — it requires fewer inputs and is equivalent for horizontal FOV.
- Do not confuse fov_x_mm (the desired horizontal coverage) with sensor_width_mm — they are different quantities.
- Working distance is measured to the object surface, not to a mounting bracket. Account for any offset between the camera body/mount and the front principal plane of the lens.

# Related Calculators

- fov_using_pixel_size: The forward direction — given working distance, compute FOV.
- working_distance_using_sensor_size: Equivalent calculation when sensor_size_mm is already known (simpler inputs).
- sensor_geometry: If you need sensor physical dimensions as a standalone output.
- focal_length: If you want to find what lens focal length achieves a given FOV at a fixed working distance.
