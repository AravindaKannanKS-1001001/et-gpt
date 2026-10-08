---
id: line_scan_sensor_widths

category: reference

tags:
  - line_scan
  - line_scan_camera
  - line_scan_sensor
  - line_scan_width
  - sensor_width_mm
  - line_scan_resolution
  - 0.5k
  - 1k
  - 2k
  - 4k
  - 6k
  - 8k
  - 12k
  - pixels_per_line
  - line_pixels
  - linescan_format
  - linescan_sensor_size
  - linescan_physical_width
  - linear_sensor
  - linear_array
  - 1d_sensor
  - tdi
  - tdi_camera
  - web_inspection
  - print_inspection
  - web_width
  - sensor_width
  - pixel_pitch
  - 5_um
  - 7_um
  - 10_um
  - 14_um
  - how_wide_is_line_scan
  - line_scan_sensor_mm
  - line_scan_coverage
  - basler_sprint
  - dalsa_piranha
  - teledyne
  - vieworks_line_scan
  - camera_link
  - coaxpress_line_scan
  - what_sensor_width
  - line_scan_physical_size

required_inputs: []
optional_inputs: []
description: "Physical sensor width (mm) for standard line scan resolutions (1K–12K) and pixel pitches (5–14 µm)"
common_uses:
  - "Get sensor_size_mm for fov_using_sensor_size to compute cross-scan coverage width"
  - "Get sensor_size_mm for focal_length to find required lens for a target coverage width"
  - "Get sensor_size_mm for working_distance_using_sensor_size to find mounting distance"
---

# Purpose

Lookup table mapping line scan camera sensor resolution and pixel pitch to the physical sensor width in millimeters.

Use this when calculating the lens and optical geometry for a line scan system. The physical sensor width (in mm) determines the coverage at a given working distance — same optical formulae as area scan cameras (fov_using_sensor_size), but applied to the cross-scan (width) axis only.

# Line Scan Sensor Width Reference

| Sensor Type  | Resolution | Pixel Pitch | Width (mm) |
| ------------ | ---------: | ----------: | ---------: |
| 0.5K @ 14 µm |        512 |       14 µm |        7.2 |
| 1K @ 10 µm   |       1024 |       10 µm |       10.2 |
| 1K @ 14 µm   |       1024 |       14 µm |       14.3 |
| 2K @ 10 µm   |       2048 |       10 µm |       20.5 |
| 2K @ 14 µm   |       2048 |       14 µm |       28.7 |
| 4K @ 7 µm    |       4096 |        7 µm |       28.7 |
| 4K @ 10 µm   |       4096 |       10 µm |       41.0 |
| 6K @ 7 µm    |       6144 |        7 µm |       43.0 |
| 8K @ 7 µm    |       8192 |        7 µm |       57.3 |
| 12K @ 5 µm   |      12288 |        5 µm |       61.4 |

# JSON Lookup

```json
{
  "line_scan_sensor_width_mm": {
    "0.5K_14um": 7.2,
    "1K_10um": 10.2,
    "1K_14um": 14.3,
    "2K_10um": 20.5,
    "2K_14um": 28.7,
    "4K_7um": 28.7,
    "4K_10um": 41.0,
    "6K_7um": 43.0,
    "8K_7um": 57.3,
    "12K_5um": 61.4
  }
}
```

# How to Use in Optical Calculations

Line scan cameras have a 1D sensor. The sensor_width_mm is used exactly like a regular area scan sensor width for the cross-scan axis:

1. Find your sensor type → get sensor_width_mm from this table
2. Use sensor_width_mm as sensor_size_mm in fov_using_sensor_size to compute cross-scan FOV (coverage width)
3. Use sensor_width_mm in working_distance_using_sensor_size to find required mounting distance for a desired coverage width
4. Use sensor_width_mm in focal_length to find the required lens focal length

The along-scan direction is not bounded by the sensor — it is determined by conveyor speed and line rate. Use line_scan_frequency to compute line rate, resolution, and throughput.

# Optical Geometry for Line Scan

Cross-scan axis (sensor width axis):
- Works identically to an area scan camera
- Coverage width at working distance = fov_using_sensor_size(sensor_width_mm, focal_length_mm, working_distance_mm)
- Required lens focal length = focal_length(object_width_mm, working_distance_mm, sensor_width_mm)

Along-scan axis (conveyor direction):
- There is no sensor boundary — coverage is unlimited
- Resolution in this direction = conveyor_speed_mm_s / line_frequency_hz (mm per line)
- For square pixels: line_frequency_hz = conveyor_speed_mm_s × pixels_per_mm

# Pixel Pitch and FOV Trade-offs

| Pixel Pitch | Benefit                                  | Trade-off                              |
| ----------- | ---------------------------------------- | -------------------------------------- |
| 5–7 µm      | High resolution, compact sensor          | Shorter sensor, smaller coverage width |
| 10 µm       | Good balance of resolution and coverage  | Moderate line rate requirement         |
| 14 µm       | Larger pixels, better light sensitivity  | Lower spatial resolution per mm        |

Larger pixel pitch → more light per pixel → easier to achieve short exposure times at high line rates. Critical for high-speed web inspection where exposure per line may be < 5 µs.

# Common Example Queries This Knowledge Resolves

- What is the physical width of a 4K line scan sensor?
- How wide is a 2048-pixel line scan sensor with 10 µm pixel pitch?
- What sensor width does a 4K @ 7 µm line scan camera have?
- Physical size of a 8K line scan camera sensor.
- What focal length lens do I need for a 4K line scan camera at 600 mm distance to cover 500 mm?
- What is the sensor_size_mm for a line scan camera?
- What coverage width does a 6K line scan sensor get with a 35 mm lens at 800 mm?
- My line scan camera is 4096 pixels at 10 µm pixel pitch — what is sensor width?
- What working distance for a 2K @ 14 µm line scan sensor to cover a 300 mm belt?
