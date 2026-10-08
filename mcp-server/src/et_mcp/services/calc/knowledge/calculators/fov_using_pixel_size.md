---
id: fov_using_pixel_size

category: optics

tags:
  - fov
  - field_of_view
  - coverage
  - visible_area
  - inspection_area
  - horizontal_fov
  - vertical_fov
  - diagonal_fov
  - fov_x
  - fov_y
  - camera
  - sensor
  - lens
  - pixel_size
  - pixel_pitch
  - pixel_size_um
  - resolution
  - width_pixels
  - height_pixels
  - megapixel
  - sensor_width
  - sensor_height
  - sensor_diagonal
  - aspect_ratio
  - imaging_geometry
  - optical_geometry
  - machine_vision
  - industrial_camera
  - area_scan
  - coverage_area
  - how_much_can_camera_see
  - what_can_camera_see
  - camera_coverage
  - view_area
  - viewing_area
  - field_coverage
  - inspection_width
  - inspection_height

required_inputs:
  - width_pixels
  - height_pixels
  - pixel_size_um
  - focal_length_mm
  - working_distance_mm

optional_inputs: []

description: "Calculate FOV (width, height, diagonal in mm) from pixel count, pixel pitch, focal length, and working distance"
---

# Purpose

Calculate complete sensor geometry (physical width, height, diagonal in mm, aspect ratio) and horizontal, vertical, and diagonal field of view — all derived from sensor resolution, pixel pitch, lens focal length, and working distance.

This is the most complete FOV calculator. Use it when you know the camera sensor as "N megapixels at X µm pixel size" — which is the standard way machine vision cameras are specified — and you want to know exactly how much of the world that camera can see at a given distance through a given lens.

# Explanation

The formula works in two stages:

Stage 1 — Sensor geometry: multiplies pixel count by pixel size to convert the sensor from pixel space into physical millimeters.
  sensor_width_mm = width_pixels × pixel_size_um / 1000
  sensor_height_mm = height_pixels × pixel_size_um / 1000

Stage 2 — Optical FOV: applies the thin-lens magnification formula.
  magnification_term = (working_distance_mm / focal_length_mm) − 1
  fov_x_mm = sensor_width_mm × magnification_term
  fov_y_mm = sensor_height_mm × magnification_term

The magnification_term captures how much larger the object appears relative to the sensor — it grows with working distance and shrinks with focal length. When working_distance equals focal_length, magnification_term is zero and FOV collapses to zero (invalid).

# Use Cases

- Determine total camera coverage for a new inspection system layout.
- Calculate horizontal and vertical FOV simultaneously from one set of inputs.
- Verify a lens is appropriate for a sensor before purchasing hardware.
- Determine if a conveyor belt fits within the camera's field of view.
- Plan camera mounting positions for a multi-camera array.
- Confirm that a part or PCB fits within the frame at a given working distance.
- Calculate the spatial resolution (mm/pixel) achievable at a specific working distance.
- Evaluate different lens options for the same sensor at the same working distance.
- Determine coverage area in mm² for quoting inspection throughput.
- Check if a wide-angle or telephoto lens better suits an application.
- Estimate how the FOV changes when the working distance is adjusted.
- Size the camera for a robot-mounted vision system where working distance is constrained.
- Verify that two overlapping cameras have sufficient overlap for stitching.

# Example Queries

- How much area can my camera see?
- What field of view do I get with a 16 mm lens at 500 mm distance?
- Calculate camera coverage for a 2448×2048 sensor with 3.45 µm pixels.
- Determine visible width at 600 mm distance.
- FOV for sensor with 3.45 µm pixel pitch using a 25 mm lens.
- What is the horizontal and vertical FOV for my camera?
- How much inspection area is visible at this working distance?
- I have a 5 MP camera with 3.45 µm pixels, 12 mm lens, 400 mm distance — what do I see?
- Camera is Sony IMX174, 1936×1216 pixels, 5.86 µm pitch, 16 mm lens, 300 mm WD — FOV?
- What coverage does a Basler acA2040 give at 800 mm with a 35 mm lens?
- Will a 200 mm wide part fit in the frame at 500 mm distance?
- My working distance is 350 mm, lens is 8 mm, sensor is 2048×2048 at 5.5 µm — what is the FOV?
- How many mm per pixel at 400 mm distance?
- What is the diagonal FOV?
- Calculate inspection area in mm squared.
- Can I see the whole conveyor belt width at this distance?
- What focal length gives me 300 mm horizontal FOV at 600 mm working distance?
- I need to see a 400×300 mm area — does this camera and lens work?

# Input Meanings

width_pixels:
Number of active pixels across the sensor width. Found on camera datasheet as "horizontal resolution" or "image width". Example: 2448 for a 5 MP camera.

height_pixels:
Number of active pixels down the sensor height. Found as "vertical resolution" or "image height". Example: 2048 for a 5 MP camera.

pixel_size_um:
Physical size of one square pixel on the sensor die, measured in micrometers (µm). Also called pixel pitch. Found on camera or sensor datasheet. Common values: 1.67 µm (Sony Starvis), 2.74 µm (IMX250), 3.45 µm (IMX174/178), 4.8 µm (IMX304), 5.5 µm (IMX264), 5.86 µm (IMX174). Do not confuse with sensor size in inches (1/1.8", 1/2.9") — those are format designators, not direct measurements.

focal_length_mm:
Nominal lens focal length in millimeters. Common values: 6, 8, 12, 16, 25, 35, 50 mm. Note: the actual effective focal length can vary slightly from the nominal value depending on focus distance and lens design. Use the nominal value from the lens datasheet.

working_distance_mm:
Distance from the front principal plane of the lens to the object surface being imaged, in millimeters. Must be greater than focal_length_mm — otherwise the image is formed behind the sensor (physically invalid). Must be significantly greater than focal_length_mm in practice (at least 2–3×) to form a real image at a reasonable magnification.

# Gotchas

- working_distance_mm must be greater than focal_length_mm. If they are equal or close, the result will be zero or near-zero FOV — this is a physically impossible imaging configuration.
- pixel_size_um is not the same as sensor size in inches. "1/1.8 inch sensor" is a legacy format designation with no direct millimeter equivalence without a lookup table.
- This calculator assumes the thin-lens model. Real lenses have distortion (barrel, pincushion) that slightly changes the effective FOV at the edges. For wide-angle lenses (< 8 mm focal length), actual FOV may differ by a few percent.
- The result gives the FOV at the focal plane. If the object is tilted or at a different distance, the effective FOV changes.
- FOV scales linearly with working distance for a fixed lens. Doubling the distance doubles the FOV.
- If sensor_size_mm is already known (from a datasheet), use fov_using_sensor_size instead — it's simpler and avoids the intermediate pixel size conversion.
- Do not use working_distance in meters — the input must be in millimeters.

# Related Calculators

- fov_using_sensor_size: Use when sensor physical size (mm) is already known. Simpler — fewer inputs. Does one axis at a time.
- working_distance_using_pixel_size: The inverse — given desired FOV, solve for working distance.
- sensor_geometry: Returns only the sensor physical dimensions without computing FOV. Use as a first step if you need sensor size for other calculations.
- focal_length: The inverse of this — given desired FOV and working distance, find the required focal length.
