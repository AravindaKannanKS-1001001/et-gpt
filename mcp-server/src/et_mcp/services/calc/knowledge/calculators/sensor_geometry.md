---
id: sensor_geometry

category: sensor

tags:
  - sensor_geometry
  - sensor_size
  - sensor_dimensions
  - sensor_width
  - sensor_height
  - sensor_width_mm
  - sensor_height_mm
  - sensor_diagonal
  - sensor_diagonal_mm
  - aspect_ratio
  - aspect_ratio_decimal
  - aspect_ratio_fraction
  - pixel_size
  - pixel_pitch
  - pixel_size_um
  - resolution
  - width_pixels
  - height_pixels
  - megapixel
  - physical_sensor_size
  - sensor_format
  - sensor_class
  - what_is_sensor_size
  - sensor_mm
  - convert_pixels_to_mm
  - derive_sensor_size
  - sensor_diagonal_pixels
  - sensor_type
  - imx
  - sony_sensor
  - basler
  - flir
  - allied_vision
  - machine_vision
  - area_scan

required_inputs:
  - width_pixels
  - height_pixels
  - pixel_size_um

optional_inputs: []

description: "Calculate physical sensor dimensions (width, height, diagonal in mm) and aspect ratio from pixel count and pixel pitch"
chain_note: "Results (width_mm, height_mm, diagonal_mm) feed directly into fov_using_sensor_size, working_distance_using_sensor_size, focal_length, and o_ring"
---

# Purpose

Calculate the physical sensor dimensions — width, height, and diagonal in millimeters — along with sensor diagonal in pixels and aspect ratio (decimal and fraction), from the sensor resolution (pixels) and pixel pitch (µm).

This is the foundational geometry step. Use it when you have pixel count and pixel size but need physical millimeter dimensions — which are required by fov_using_sensor_size, working_distance_using_sensor_size, focal_length, and o_ring.

# Explanation

  sensor_width_mm  = width_pixels  × pixel_size_um / 1000
  sensor_height_mm = height_pixels × pixel_size_um / 1000
  sensor_diagonal_mm = sqrt(sensor_width_mm² + sensor_height_mm²)
  sensor_diagonal_pixels = round(sqrt(width_pixels² + height_pixels²))

  aspect_ratio_decimal  = width_pixels / height_pixels
  aspect_ratio_fraction = width_pixels/gcd : height_pixels/gcd
    where gcd = greatest common divisor of width_pixels and height_pixels

# Use Cases

- Convert camera datasheet specs (resolution + pixel pitch) into physical sensor dimensions needed for optical calculations.
- Determine sensor diagonal to check format compatibility with a lens image circle.
- Verify sensor aspect ratio before selecting a lens with sufficient image circle.
- Find sensor physical size when the manufacturer's "sensor format" (1/1.8") is ambiguous.
- Use as a preparatory step before running fov_using_sensor_size, working_distance_using_sensor_size, or focal_length.
- Understand the physical footprint of the imaging area.
- Compare sensors from different manufacturers on a physical size basis.
- Check if a lens image circle (specified in mm) covers the sensor diagonal.
- Determine the physical width and height of the image a sensor produces.
- Extract aspect ratio information from a camera specification.

# Example Queries

- What is the physical size of my sensor?
- What is the sensor diagonal?
- What aspect ratio does my sensor have?
- Sensor dimensions from pixel count and pixel size.
- Physical sensor width for 2448×2048 sensor with 3.45 µm pixels.
- What format is my sensor?
- Convert 1936×1216 pixels at 5.86 µm to millimeters.
- What is the sensor width in mm for a 4096×3000 sensor with 4.5 µm pixels?
- My camera is 2448×2048 at 3.45 µm pixel pitch — what is the sensor width and height in mm?
- Sensor diagonal for Sony IMX304 (5328×4608, 2.74 µm)?
- What is the physical sensor size for a 5 MP camera with 3.45 µm pixel pitch?
- Does a 2/3 inch lens image circle cover my sensor?
- Aspect ratio for 1920×1200 sensor.
- Physical size of a 4000×3000 pixel sensor with 4.8 µm pixel pitch.
- What is the sensor format equivalent (in inches) for my sensor?
- Sensor width for a Basler acA2040 (2040×2040 at 5.5 µm)?

# Input Meanings

width_pixels:
Number of active pixels across the sensor width (horizontal axis). Found on the camera datasheet as "image width" or "horizontal resolution". Examples: 1936, 2448, 2592, 4096, 5328.

height_pixels:
Number of active pixels down the sensor height (vertical axis). Found as "image height" or "vertical resolution". Examples: 1216, 2048, 2048, 3000, 4608.

pixel_size_um:
Physical size of one square pixel on the sensor die, in micrometers (µm). Also called pixel pitch. Found on the camera sensor datasheet. Common values in machine vision:
- 1.67 µm: Sony Starvis 2 (IMX585, IMX662, etc.)
- 2.74 µm: Sony IMX250, IMX253, IMX304
- 3.45 µm: Sony IMX174, IMX178, IMX183, IMX264, IMX265
- 4.5 µm: Sony IMX990 (SWIR)
- 4.8 µm: Sony IMX304 (12 MP)
- 5.5 µm: Sony IMX264, Basler acA2040 series
- 5.86 µm: Sony IMX174 (1936×1216)

# Gotchas

- pixel_size_um is NOT the same as sensor format size in inches. "1/2 inch", "2/3 inch", "1 inch" are legacy format designations inherited from vidicon tube cameras — they do not directly convert to physical diagonal. For a 1-inch sensor, the diagonal is approximately 16 mm, not 25.4 mm (1 inch).
- For non-square pixels (rare in machine vision but common in some scientific cameras), width and height pixel sizes differ. This calculator assumes square pixels. If pixel sizes differ between axes, calculate width and height separately.
- The sensor_diagonal_mm output is useful for checking lens image circle compatibility. The lens image circle diameter must be ≥ sensor_diagonal_mm to avoid vignetting. A 2/3" lens covers ~11 mm diagonal; a 1" lens covers ~16 mm.
- aspect_ratio_fraction uses the GCD simplification. A 4/3 sensor (4096×3072) would give "4:3". If the GCD is large, the fraction simplifies cleanly; irregular resolutions may not simplify to a recognizable ratio.
- This calculator output (sensor_width_mm, sensor_height_mm) is the primary input for fov_using_sensor_size, working_distance_using_sensor_size, and focal_length. It is effectively the bridge between pixel-domain specs and physical optical calculations.
- Non-standard sensor resolutions (e.g., ROI-cropped readout modes) give a different active area. Always use the full sensor resolution when computing the sensor format for lens selection.

# Related Calculators

- fov_using_pixel_size: Computes sensor geometry and FOV together in one step — if you only need FOV, skip sensor_geometry and use fov_using_pixel_size directly.
- fov_using_sensor_size: Use sensor_width_mm or sensor_height_mm from this output as input.
- working_distance_using_sensor_size: Same — use sensor_size_mm from this output.
- focal_length: Same — sensor_size_mm from here feeds focal_length.
- o_ring: sensor_size_mm from here can also feed o_ring.
