---
id: depth_of_field

category: optics

tags:
  - depth_of_field
  - dof
  - focus
  - focus_range
  - focal_range
  - near_focus
  - far_focus
  - near_limit
  - far_limit
  - in_focus
  - sharpness
  - acceptable_sharpness
  - hyperfocal
  - hyperfocal_distance
  - aperture
  - f_number
  - f_stop
  - f_number
  - fnumber
  - blur
  - circle_of_confusion
  - coc
  - magnification
  - effective_aperture
  - will_object_be_in_focus
  - focus_limits
  - depth_of_focus
  - inspection_depth
  - 3d_object
  - height_variation
  - surface_variation
  - tall_object
  - curved_object
  - machine_vision
  - industrial_optics
  - how_much_depth
  - can_i_focus
  - focus_depth
  - focus_budget

required_inputs:
  - working_distance_mm
  - focal_length_mm
  - f_number
  - pixel_size_um

optional_inputs: []

description: "Calculate near/far focus limits and total depth of field for a given lens, aperture, and working distance"
---

# Purpose

Calculate the total depth of field (DOF), near focus limit, far focus limit, hyperfocal distance, magnification, and effective aperture for a given lens–aperture–sensor configuration at a specified working distance.

Answers the question: "If my camera is focused at distance D, what range of depths will appear acceptably sharp?"

# Explanation

The calculation uses pixel_size_um as the circle of confusion (CoC) diameter — the standard practice in machine vision, where one pixel is the sharpness limit.

Step 1 — Magnification:
  magnification = focal_length_mm / (working_distance_mm − focal_length_mm)

Step 2 — Effective aperture (accounts for close-focus light falloff):
  aperture_effective = f_number × (1 + magnification)

Step 3 — Hyperfocal distance (uses the effective aperture):
  hyperfocal_mm = (focal_length_mm² / (aperture_effective × coc_mm)) + focal_length_mm
  where coc_mm = pixel_size_um / 1000

Step 4 — Near and far focus limits from hyperfocal (u = working_distance_mm − focal_length_mm):
  dof_near_mm = (hyperfocal_mm × working_distance_mm) / (hyperfocal_mm + u)
  dof_far_mm  = (hyperfocal_mm × working_distance_mm) / (hyperfocal_mm − u)
  total_dof_mm = dof_far_mm − dof_near_mm

If hyperfocal_mm ≤ working_distance_mm − focal_length_mm, the far limit is effectively infinity and total_dof is null.

# Use Cases

- Determine whether a 3D object with height variation will be fully in focus.
- Check if a tilted or curved part fits within the focus range.
- Evaluate the effect of changing f-number on depth of field.
- Confirm that height variation on a conveyor (e.g., product stacking, lids, caps) stays within focus.
- Assess whether DOF is adequate before ordering optics and committing to a mounting position.
- Find the deepest DOF achievable with a given lens by identifying the optimal f-number.
- Check if two objects at different depths can both be in focus simultaneously.
- Evaluate telecentric lens focus depth for high-precision metrology.
- Understand the trade-off between aperture (DOF) and exposure time (light).
- Determine the usable focus depth for a robot picking objects of varying height.
- Verify that a PCB with tall components (connectors, capacitors) fits within DOF.
- Confirm focus range for a camera mounted at a fixed position inspecting parts of varying thickness.

# Example Queries

- What depth of field do I get at f/8?
- Will the object stay in focus?
- Find near and far focus limits at 500 mm working distance.
- How much DOF do I have at this working distance?
- What aperture gives me at least 10 mm depth of field?
- Is my 3D object within the focus range?
- My product has 15 mm height variation — will it stay in focus?
- Depth of field for 16 mm lens at f/8, 500 mm working distance, 3.45 µm sensor.
- How does DOF change if I stop down from f/4 to f/8?
- What is the hyperfocal distance for this configuration?
- My part is 30 mm tall — does it stay in focus at f/11?
- What is the near focus and far focus limit?
- Can I focus from 480 mm to 520 mm with this setup?
- I need at least 20 mm of DOF — what f-number do I need?
- Effective aperture at close focus distance.
- How much depth of field does a 50 mm lens give at f/16?

# Input Meanings

working_distance_mm:
Distance from the lens front principal plane to the point of focus (the object surface), in millimeters. The DOF is centered around this distance.

focal_length_mm:
Lens focal length in millimeters.

f_number:
Lens aperture expressed as f-number (f-stop). Higher f-number = smaller aperture = more depth of field but less light. Common values: 1.4, 2, 2.8, 4, 5.6, 8, 11, 16. Machine vision lenses commonly range f/1.4 to f/16.

pixel_size_um:
Physical size of one sensor pixel in micrometers (µm). This defines the circle of confusion — the largest acceptable blur spot on the sensor. Using one pixel as CoC is standard practice in machine vision (unlike photography, which uses a fraction of the diagonal).

# Gotchas

- More DOF always comes at a cost: stopping down (larger f-number) reduces light reaching the sensor, requiring longer exposure or higher gain. This creates a DOF–motion-blur–noise trade-off.
- At very close working distances (high magnification), the effective aperture increases significantly. A nominal f/8 lens at 1:1 magnification behaves like f/16 for exposure purposes. This is captured in aperture_effective.
- When working_distance approaches or exceeds hyperfocal_distance, the far limit is infinite and total_dof is undefined (null). This is not an error — it means everything beyond dof_near_mm is acceptably sharp.
- The circle of confusion here is set to pixel_size_um. This gives a sharp/not-sharp boundary at the pixel level. For sub-pixel accuracy applications, your effective DOF is shallower.
- DOF is not symmetric around the focus point — the far side has more DOF than the near side. Near limit is closer to the focus point than the far limit.
- This calculator does not account for vibration or camera shake, which effectively reduces practical DOF.
- Telecentric lenses behave differently from standard entocentric lenses. This calculator models standard entocentric geometry.
- Increasing focal length reduces DOF (at the same working distance and f-number). To maintain DOF when switching to a longer lens, increase f-number or increase working distance.

# Related Calculators

- fov_using_pixel_size: Get the FOV at the same working distance — often needed alongside DOF to confirm the full imaging geometry.
- exposure_time: DOF trade-off partner — stopping down for DOF may require longer exposure, which may cause motion blur.
- measurement_accuracy: If measuring object dimensions, DOF must be adequate to keep features in focus.
