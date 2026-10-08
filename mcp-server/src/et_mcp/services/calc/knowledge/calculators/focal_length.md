---
id: focal_length

category: optics

tags:
  - focal_length
  - lens
  - lens_selection
  - optics
  - fov
  - field_of_view
  - sensor_size
  - required_focal_length
  - which_lens
  - lens_choice
  - what_lens
  - select_lens
  - lens_sizing
  - optical_design
  - imaging_geometry
  - machine_vision
  - lens_mm
  - lens_recommendation
  - object_size
  - working_distance
  - coverage
  - pick_lens
  - choose_lens
  - best_lens
  - what_focal_length
  - how_much_focal_length
  - lens_calculator
  - lens_formula

required_inputs:
  - object_size_mm
  - working_distance_mm
  - sensor_size_mm

optional_inputs: []

description: "Calculate required lens focal length to image a given object size at a specified working distance"
chain_note: "Use sensor_geometry first if you have pixel count and pixel pitch but not sensor_size_mm"
---

# Purpose

Calculate the required lens focal length to image a given object size (field of view) at a specified working distance with a known physical sensor size.

Answers: "What focal length lens do I need?" — the most common starting question in machine vision system design.

# Explanation

Rearranges the thin-lens FOV formula to solve for focal length:

  focal_length_mm = sensor_size_mm × working_distance_mm / (object_size_mm + sensor_size_mm)

Equivalently:
  magnification = sensor_size_mm / object_size_mm   (sensor to object ratio)
  focal_length_mm = working_distance_mm × magnification / (1 + magnification)

The result is the ideal (theoretical) focal length. Because lenses come in standard focal lengths (6, 8, 12, 16, 25, 35, 50 mm), the actual lens chosen will be the nearest standard value. Choosing a shorter focal length gives a wider FOV than required (object appears smaller, more context visible). Choosing a longer focal length gives a narrower FOV (object fills more of the frame but may not fit entirely).

# Use Cases

- Select a lens focal length for a new machine vision system when object size and working distance are defined by the application.
- Determine what catalog lens is closest to the theoretical requirement.
- Evaluate the effect of changing working distance on required focal length.
- Verify that a standard focal length lens achieves the required coverage at a given distance.
- Design the optics for a robot vision system where arm reach defines working distance.
- Calculate focal length for each camera axis independently (pass sensor width + object width, then sensor height + object height).
- Size lenses for a multi-camera system with a fixed camera bar and varying object sizes.
- Determine what happens to coverage if the next standard focal length is used.
- Confirm that a physically compact lens (short focal length) is sufficient for a constrained working distance.
- Estimate lens requirements during the quotation phase before final sensor selection.

# Example Queries

- What focal length lens do I need?
- Which lens should I choose for this application?
- What lens do I need to capture a 300 mm wide object at 600 mm working distance?
- How much focal length is required for 400 mm FOV?
- What lens for 500 mm working distance, 8.8 mm sensor, 300 mm object?
- Calculate required focal length for a 2/3 inch sensor viewing a 200 mm PCB at 400 mm.
- My object is 500 mm wide, working distance is 800 mm, sensor is 11.3 mm — what lens?
- Recommend a focal length for inspecting a 300 mm conveyor belt at 600 mm height.
- I need to capture a 150 mm part at 300 mm distance with a 1/2 inch sensor — what lens?
- What is the focal length for 1000 mm FOV at 2 m distance with a 12.8 mm sensor?
- Lens selection for a 250 × 200 mm object at 500 mm WD with a 2/3 inch sensor.
- What focal length do I need for a 4/3 inch sensor to see 400 mm at 1.2 m?
- Which standard focal length lens is closest to the theoretical value?

# Input Meanings

object_size_mm:
Physical size of the object (or desired FOV) to be captured in the axis being calculated, in millimeters. For the horizontal axis: object width. For vertical: object height. This is what you want to see.

working_distance_mm:
Distance from the lens front principal plane to the object surface in millimeters. Must be known or fixed by the application constraints.

sensor_size_mm:
Physical sensor dimension in the same axis as object_size_mm, in millimeters. Use sensor width for horizontal, sensor height for vertical. If only pixel count and pixel size are known, use sensor_geometry first to derive this value. Common values: 2/3" sensor width ≈ 8.8 mm, 1" ≈ 12.8 mm, 4/3" ≈ 17.3 mm.

# Gotchas

- The result is a theoretical ideal focal length. Standard catalog lenses come in discrete values: 6, 8, 12, 16, 25, 35, 50 mm. The actual lens to order is the nearest standard value — choosing shorter means slightly wider FOV (object may not fill the frame), choosing longer means slightly narrower FOV (object may be clipped if too close).
- This is a single-axis calculation. For a 2D system, compute it for width and height separately. The more constraining axis determines the lens choice.
- If you get a very short focal length (< 6 mm), the required FOV at that distance cannot be achieved with a standard machine vision lens — either increase the working distance or accept a different FOV.
- Very long focal lengths (> 50 mm) are physically large and expensive. If the result is > 50 mm, consider increasing working distance or using a larger sensor.
- The calculation assumes sensor physical size is already known. If you only have pixel count and pixel pitch, use sensor_geometry to get sensor_size_mm first.
- Different axes may imply different focal lengths. Take the smaller value (wider FOV) to ensure the whole object fits within both width and height.
- Lens distortion is not modeled. Wide-angle lenses (< 8 mm) may show significant barrel distortion, causing edge pixels to represent a larger area than the formula predicts.

# Related Calculators

- fov_using_sensor_size: The inverse — given focal length, find FOV.
- working_distance_using_sensor_size: Another inverse — given desired FOV and sensor size, find required working distance.
- sensor_geometry: If sensor_size_mm needs to be derived from pixel count and pixel pitch first.
- fov_using_pixel_size: Full forward calculation (FOV from pixels + pixel size + focal length + WD) — useful for verifying the chosen focal length.
