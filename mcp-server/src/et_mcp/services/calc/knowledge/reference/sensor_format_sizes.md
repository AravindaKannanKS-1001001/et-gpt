---
id: sensor_format_sizes

category: reference

tags:
  - sensor_size
  - sensor_format
  - sensor_diagonal
  - sensor_diagonal_mm
  - sensor_size_mm
  - sensor_format_inches
  - sensor_format_lookup
  - inch_format
  - optical_format
  - sensor_class
  - sensor_type
  - imager_format
  - imager_size
  - 1/4_inch
  - 1/3_inch
  - 1/2.5_inch
  - 1/2_inch
  - 1/1.8_inch
  - 2/3_inch
  - 1_inch
  - 1.2_inch
  - 4/3_inch
  - aps_c
  - full_frame
  - what_is_sensor_size
  - sensor_size_in_mm
  - convert_sensor_format
  - inch_to_mm
  - sensor_diagonal_from_format
  - optical_format_mm
  - lens_image_circle
  - image_circle_coverage
  - which_lens_covers
  - format_compatibility
  - lens_format_match
  - sensor_format_mm
  - how_big_is_sensor
  - sensor_physical_size
  - imx_sensor_format
  - basler_format
  - flir_format
  - area_scan_format
  - machine_vision_sensor
  - quarter_inch
  - half_inch
  - two_thirds_inch
  - one_inch
  - four_thirds
  - micro_four_thirds

required_inputs: []
optional_inputs: []
description: "Sensor optical format (1/4\", 2/3\", 1\", APS-C, etc.) to physical width, height and diagonal in mm"
common_uses:
  - "Get sensor_diagonal_mm to check lens image circle coverage"
  - "Get width_mm for input to fov_using_sensor_size or focal_length"
  - "Verify a lens image circle covers the sensor diagonal"
---

# Purpose

Lookup table mapping sensor optical format designations (1/4", 2/3", 1", etc.) to their physical width, height and diagonal in millimeters.

Use this table when a camera datasheet specifies a sensor format like "2/3 inch" and you need the physical dimensions in mm for optical calculations (fov_using_sensor_size, focal_length, lens image circle compatibility checks).

# Important: Sensor Format Is NOT a Direct Measurement

The sensor "inch" format designations are a historical legacy from vidicon vacuum tube cameras. The format number does NOT equal the actual diagonal. A "1 inch" sensor is about 12.8 × 9.6 mm with a 16 mm diagonal — not 25.4 mm. This is one of the most common sources of error in machine vision optical calculations.

The diagonal listed is an approximation of the inscribed circle diameter of the tube that would house a sensor of that size. Always use these values as a starting point and verify with the specific camera datasheet.

# Sensor Format → Dimensions (mm)

| Sensor Format  | Diagonal (mm) | Width (mm) | Height (mm) |
| -------------- | ------------: | ---------: | ----------: |
| 1/4"           |           4.0 |        3.2 |         2.4 |
| 1/3"           |           6.0 |        4.8 |         3.6 |
| 1/2.5"         |          7.18 |       5.76 |        4.29 |
| 1/2"           |           8.0 |        6.4 |         4.8 |
| 1/1.8"         |          8.93 |       7.18 |        5.32 |
| 2/3"           |          11.0 |        8.8 |         6.6 |
| 10.5 mm Format |          10.5 |        8.4 |         6.3 |
| 1/1.2"         |          13.3 |      11.25 |        7.03 |
| 1"             |          16.0 |       12.8 |         9.6 |
| 15.3 mm Format |          15.3 |      12.24 |        9.18 |
| 4/3"           |          21.6 |       17.3 |        13.0 |
| APS-C          |          28.4 |       23.6 |        15.8 |
| Full Frame     |          43.3 |       36.0 |        24.0 |

Note: values are the nominal dimensions of each optical format (4:3 for the inch formats; 1/1.2" is the 16:10 IMX174/IMX249 class, also listed under the legacy key `1.2in`). Actual dimensions vary by sensor model — use the camera datasheet when it gives exact values.

# JSON Lookup

```json
{
  "sensor_format_mm": {
    "1/4": {
      "diagonal_mm": 4.0,
      "width_mm": 3.2,
      "height_mm": 2.4
    },
    "1/3": {
      "diagonal_mm": 6.0,
      "width_mm": 4.8,
      "height_mm": 3.6
    },
    "1/2.5": {
      "diagonal_mm": 7.18,
      "width_mm": 5.76,
      "height_mm": 4.29
    },
    "1/2": {
      "diagonal_mm": 8.0,
      "width_mm": 6.4,
      "height_mm": 4.8
    },
    "1/1.8": {
      "diagonal_mm": 8.93,
      "width_mm": 7.18,
      "height_mm": 5.32
    },
    "2/3": {
      "diagonal_mm": 11.0,
      "width_mm": 8.8,
      "height_mm": 6.6
    },
    "10.5mm": {
      "diagonal_mm": 10.5,
      "width_mm": 8.4,
      "height_mm": 6.3
    },
    "1/1.2": {
      "diagonal_mm": 13.3,
      "width_mm": 11.25,
      "height_mm": 7.03
    },
    "1in": {
      "diagonal_mm": 16.0,
      "width_mm": 12.8,
      "height_mm": 9.6
    },
    "15.3mm": {
      "diagonal_mm": 15.3,
      "width_mm": 12.24,
      "height_mm": 9.18
    },
    "4/3": {
      "diagonal_mm": 21.6,
      "width_mm": 17.3,
      "height_mm": 13.0
    },
    "APS-C": {
      "diagonal_mm": 28.4,
      "width_mm": 23.6,
      "height_mm": 15.8
    },
    "FullFrame": {
      "diagonal_mm": 43.3,
      "width_mm": 36.0,
      "height_mm": 24.0
    },
    "1.2in": {
      "diagonal_mm": 13.3,
      "width_mm": 11.25,
      "height_mm": 7.03
    }
  }
}
```

# How to Use in Optical Calculations

When a user says "I have a 2/3 inch sensor" and needs FOV or working distance:
1. Look up the format: 2/3" → width 8.8 mm, height 6.6 mm, diagonal 11.0 mm
2. For horizontal FOV calculations: use width_mm = 8.8 mm (or the exact datasheet value)
3. For diagonal FOV calculations: use diagonal_mm = 11.0 mm
4. Feed into fov_using_sensor_size, working_distance_using_sensor_size, or focal_length

# Lens Image Circle Requirements

The lens image circle diameter must be ≥ sensor diagonal to avoid vignetting (dark corners):

| Lens Format | Image Circle (mm) | Covers Sensors Up To |
| ----------- | ----------------: | -------------------- |
| C-mount 1/3"  |             6.0 | 1/3" and smaller     |
| C-mount 1/2"  |             8.0 | 1/2" and smaller     |
| C-mount 2/3"  |            11.0 | 2/3" and smaller     |
| C-mount 1"    |            16.0 | 1" and smaller       |
| F-mount       |            43.3 | Full frame and below |
| 4/3" mount    |            21.6 | 4/3" and smaller     |

# Common Example Queries This Knowledge Resolves

- What is the physical size of a 2/3 inch sensor?
- How big is a 1 inch sensor in mm?
- Convert 1/1.8 inch sensor format to mm.
- What sensor diagonal does a 2/3" camera have?
- Is a 1" lens sufficient to cover my 2/3" sensor?
- What does 4/3 inch sensor mean in millimeters?
- My camera is listed as 1/2 inch format — what is the actual sensor size?
- Does a 2/3" C-mount lens cover a 1" sensor? (No — image circle too small)
- What format is 11 mm diagonal?
- Sensor format for IMX174 (Sony 1/1.2" format → approximately 13.4 mm diagonal)
