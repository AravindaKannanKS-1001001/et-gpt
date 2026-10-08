---
id: f_stop_values

category: reference

tags:
  - f_stop
  - f_number
  - fnumber
  - aperture
  - aperture_stop
  - f_stop_lookup
  - f_stop_values
  - f_stop_table
  - aperture_values
  - lens_aperture
  - f1
  - f1.4
  - f2
  - f2.8
  - f4
  - f5.6
  - f8
  - f11
  - f16
  - f22
  - stop_value
  - half_stop
  - full_stop
  - exposure_stop
  - depth_of_field_aperture
  - dof_aperture
  - circle_of_confusion
  - coc
  - light_gathering
  - exposure_calculation
  - what_is_f_stop
  - f_stop_number
  - f_stop_exact_value
  - aperture_exact_value
  - aperture_in_decimals
  - f_number_decimal
  - lens_speed
  - fast_lens
  - slow_lens
  - machine_vision_aperture
  - industrial_lens_aperture
  - sqrt2
  - power_of_sqrt2

required_inputs: []
optional_inputs: []
description: "Standard f-stop display labels (f/5.6, f/11) to exact decimal values for depth of field calculations"
common_uses:
  - "Get exact f_number decimal for depth_of_field calculator input"
  - "Determine how many stops apart two apertures are"
  - "Choose aperture based on DOF or exposure requirements"
---

# Purpose

Lookup table of standard photographic f-stop designations and their exact internal numeric values.

Use this when a user specifies an aperture as "f/8" or "f/2.8" and the calculation requires the exact decimal value for depth_of_field or exposure_time computations.

# Why F-Stops Are Not Round Numbers

F-stops follow a geometric progression where each full stop doubles or halves the light:
  f_number = √2 ^ n   (where n = 0, 1, 2, 3, ...)

This means each step multiplies the f-number by √2 ≈ 1.414. The "display" values (f/1.4, f/2.8, f/5.6, f/11) are rounded for readability, but calculations should use the exact value.

# F-Stop Lookup Table

| Display Label | Exact Value | Relative Light (stops) | Relative Exposure |
| ------------- | ----------: | ---------------------: | ----------------: |
| f/1           |    1.000000 |                      0 |               1×  |
| f/1.4         |    1.414214 |                     +1 |             1/2×  |
| f/2           |    2.000000 |                     +2 |             1/4×  |
| f/2.8         |    2.828427 |                     +3 |             1/8×  |
| f/4           |    4.000000 |                     +4 |            1/16×  |
| f/5.6         |    5.656854 |                     +5 |            1/32×  |
| f/8           |    8.000000 |                     +6 |            1/64×  |
| f/11          |   11.313708 |                     +7 |           1/128×  |
| f/16          |   16.000000 |                     +8 |           1/256×  |
| f/22          |   22.627417 |                     +9 |           1/512×  |

# JSON Lookup

```json
{
  "f_stops": {
    "f1":   1.0,
    "f1.4": 1.414214,
    "f2":   2.0,
    "f2.8": 2.828427,
    "f4":   4.0,
    "f5.6": 5.656854,
    "f8":   8.0,
    "f11":  11.313708,
    "f16":  16.0,
    "f22":  22.627417
  }
}
```

# F-Stop Effect on Depth of Field

Depth of field scales approximately with f-number:
- Higher f-number (smaller aperture) → more depth of field
- Lower f-number (larger aperture, "wider open") → less depth of field, more light

Doubling the f-number (one full stop, e.g., f/4 → f/8) approximately doubles the depth of field but halves the light — requiring 4× longer exposure or 4× brighter lighting to maintain the same image brightness.

| F-Stop | DOF     | Light   | Typical Use in Machine Vision        |
| ------ | ------- | ------- | ------------------------------------ |
| f/1.4  | Minimum | Maximum | Very bright, thin DOF, high-speed    |
| f/2.8  | Small   | High    | High-speed inspection, good light    |
| f/4    | Small   | Moderate| Fast inspection with adequate light  |
| f/5.6  | Moderate| Moderate| General machine vision               |
| f/8    | Good    | Lower   | Common default in machine vision     |
| f/11   | Deep    | Low     | Deep DOF needed, ample lighting      |
| f/16   | Deeper  | Very low| Maximum DOF, requires bright strobe  |
| f/22   | Maximum | Minimum | Rarely used — diffraction kicks in   |

# Gotchas

- f/22 and beyond: diffraction begins to limit optical resolution. For high-resolution machine vision sensors with small pixels (< 3.5 µm), diffraction softening may appear at f/11–f/16 already.
- The "display" values like "f/5.6" and "f/11" are rounded. Using 5.6 instead of 5.656854 in DOF calculations introduces a small but non-zero error. Use exact values from this table in precise calculations.
- Machine vision lenses typically support f/1.4 to f/16. Some industrial fixed-focus lenses are not adjustable and have a fixed aperture.
- Effective f-number at close focus: when magnification is significant (close-up imaging), effective_f = f_number × (1 + magnification). This is already accounted for in the depth_of_field calculator.

# Common Example Queries This Knowledge Resolves

- What is the exact value of f/5.6?
- What is the f-number for f/11?
- Convert f-stop display to numeric value for calculation.
- What is f/2.8 in decimal?
- How many stops between f/4 and f/16?
- Which f-stop lets in twice as much light as f/8?
- What is the internal value for f/11.3?
- List all standard f-stop values.
- What f-stops does a machine vision lens typically support?
