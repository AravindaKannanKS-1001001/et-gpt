---
id: o_ring

category: optics

tags:
  - extension_ring
  - o_ring
  - extension_tube
  - close_focus
  - close_up
  - macro
  - macro_imaging
  - minimum_object_distance
  - mod
  - minimum_working_distance
  - min_wd
  - lens_extension
  - close_range
  - close_distance
  - short_working_distance
  - small_object
  - small_part
  - high_magnification
  - near_focus
  - can_lens_focus
  - focus_close_enough
  - will_it_focus
  - do_i_need_extension
  - extension_required
  - extension_length
  - ring_thickness
  - adapter_ring
  - spacer_ring
  - c_mount
  - cs_mount
  - f_mount
  - lens_adapter
  - near_macro
  - small_field_of_view
  - tiny_fov

required_inputs:
  - object_size_mm
  - minimum_object_distance_mm
  - sensor_size_mm
  - focal_length_mm

optional_inputs: []

description: "Determine if an extension ring is needed for close-focus imaging and calculate the required ring length in mm"
chain_note: "Use sensor_geometry first if you have pixel count and pixel pitch but not sensor_size_mm"
---

# Purpose

Determine whether an extension ring (extension tube / spacer ring) is required for a close-focus imaging setup, and estimate the required extension ring length in millimeters.

Answers: "Can this lens focus at the required working distance, and if not, how much extension do I need?"

# Explanation

Step 1 — Required working distance for the desired FOV:
  required_wd_mm = focal_length_mm × (object_size_mm / sensor_size_mm + 1)
  (same formula as working_distance_using_sensor_size)

Step 2 — Compare to lens MOD:
  If required_wd_mm ≥ minimum_object_distance_mm: no extension ring needed.
  If required_wd_mm < minimum_object_distance_mm: extension is required.

Step 3 — Extension ring length estimate:
  extension_ring_mm ≈ focal_length_mm² / (required_wd_mm − focal_length_mm)
  − focal_length_mm² / (minimum_object_distance_mm − focal_length_mm)

  This calculates how much additional back-focal-distance is needed to shift the image plane inward enough to focus at the required (closer) working distance.

# Use Cases

- Check if a standard machine vision lens can focus at the working distance required to image a small part.
- Evaluate lens choice for imaging small PCBs, electronic components, coins, seeds, or pills at close range.
- Determine extension ring thickness when a lens cannot focus at the required distance.
- Assess whether a fixed focal length lens can image a small object without additional optical elements.
- Evaluate the feasibility of a close-focus inspection setup before purchasing hardware.
- Determine if a telecentric objective is needed instead of a standard lens (telecentric lenses have their own working distance constraints).
- Check ring requirements when imaging small parts on a robot end-effector at close range.
- Compare lens options for their native minimum object distance vs. required working distance.
- Estimate extension ring requirements when imaging labels, markings, or engravings on small parts.
- Determine the optical stack-up (lens + extension ring thickness) for a compact camera housing.

# Example Queries

- Do I need an extension ring?
- How much extension is required for this setup?
- Can this lens focus close enough?
- Close-focus imaging setup evaluation.
- Required extension length estimation.
- Will the lens focus at this working distance?
- My working distance is 100 mm but the lens MOD is 200 mm — do I need an extension ring?
- I need to image a 10 mm object at 80 mm distance — do I need an extension tube?
- Extension ring needed for 25 mm lens at 150 mm working distance viewing a 20 mm part?
- My lens MOD is 300 mm but I need to work at 200 mm — how much extension do I need?
- Can a 50 mm lens focus on a 5 mm chip at 80 mm distance with a 2/3 inch sensor?
- How much extension ring for imaging a 30 mm object at 200 mm with a 35 mm lens?
- My minimum working distance constraint is 150 mm — can I use a 50 mm lens?
- What extension tube length for close-up PCB inspection at 120 mm?
- Will a C-mount lens adapter ring work or do I need a special macro lens?

# Input Meanings

object_size_mm:
Physical size of the object (or desired FOV dimension) to be captured in one axis, in millimeters. Determines the required working distance via the thin-lens formula.

minimum_object_distance_mm:
Minimum allowable distance between the lens front element and the object, in millimeters. This is the lens MOD (Minimum Object Distance) from the lens datasheet. If the required working distance is less than this value, the lens cannot focus at that distance without an extension ring. Note: MOD is measured from the front of the lens barrel, not the front principal plane — there may be a small offset between these.

sensor_size_mm:
Physical sensor dimension in the same axis as object_size_mm (width for horizontal, height for vertical), in millimeters.

focal_length_mm:
Lens focal length in millimeters.

# Gotchas

- minimum_object_distance_mm is the MOD from the lens datasheet — measure carefully. It is typically from the front of the lens barrel, not from the sensor plane or principal plane. Some datasheets define it differently.
- extension_ring_mm is an estimate. The exact value depends on lens construction (where the principal plane is, helicoid travel, etc.). Always verify focus with the actual extension ring in hardware.
- Adding extension rings changes the effective focal length behavior and may introduce vignetting. Very thick extension rings (> 30–40% of focal length) can cause significant light falloff.
- Extension rings cannot fix insufficient magnification — they only shift the focus distance closer. If the lens is already at MOD and still cannot see a small enough FOV, a macro or telecentric lens may be needed.
- Very close working distances (<50 mm) usually require telecentric or macro lenses with purpose-built close-focus design. Standard C-mount machine vision lenses are not optimized for working distances less than ~100 mm.
- Extension rings reduce the maximum focus distance: with extension added, the lens may no longer focus at infinity or at long working distances.
- This calculator assumes a simple thin-lens model. Actual extension ring requirements should be validated empirically with the specific lens.
- For high-precision metrology, a true telecentric lens is preferred over a standard lens with extension ring — telecentric lenses have zero perspective error across the field.

# Related Calculators

- working_distance_using_sensor_size: Computes the required_wd_mm (Step 1 above) for cross-referencing with MOD.
- fov_using_sensor_size: Verify what FOV you actually get at the computed working distance.
- focal_length: If the current lens proves inadequate, use this to find a more suitable focal length.
- depth_of_field: At close working distances, DOF is typically very shallow — always check DOF for close-focus setups.
