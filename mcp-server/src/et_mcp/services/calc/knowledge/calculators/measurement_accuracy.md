---
id: measurement_accuracy

category: metrology

tags:
  - measurement_accuracy
  - accuracy
  - precision
  - metrology
  - dimensional_measurement
  - subpixel
  - subpixel_accuracy
  - nyquist
  - nyquist_criterion
  - nyquist_sampling
  - resolution
  - pixels_per_mm
  - mm_per_pixel
  - spatial_resolution
  - feature_size
  - defect_size
  - minimum_feature
  - smallest_detectable
  - detection_limit
  - can_i_measure
  - measurement_limit
  - optical_resolution
  - vision_accuracy
  - gauge
  - gauging
  - dimensional_inspection
  - tolerance
  - measurement_tolerance
  - surface_inspection
  - defect_detection
  - crack_detection
  - scratch_detection
  - gap_measurement
  - width_measurement
  - edge_detection
  - edge_accuracy
  - how_accurate
  - achievable_accuracy
  - required_resolution
  - pixels_required

required_inputs:
  - object_size_mm
  - sensor_pixels
  - nyquist_factor
  - subpixel_factor

optional_inputs: []

description: "Estimate dimensional measurement accuracy (mm) from FOV, pixel count, Nyquist factor, and subpixel factor"
chain_note: "Usually call fov_using_pixel_size first to get object_size_mm (the FOV in mm spanning the inspection area)"
---

# Purpose

Estimate the achievable dimensional measurement accuracy of a vision system given the object size, sensor pixel count, Nyquist sampling factor, and subpixel interpolation capability.

Returns: pixels/mm, mm/pixel, effective Nyquist resolution, and final measurement accuracy in mm.

Answers: "Can I detect or measure a feature this small with this setup?"

# Explanation

Step 1 — Raw resolution:
  pixels_per_mm = sensor_pixels / object_size_mm
  mm_per_pixel = 1 / pixels_per_mm

Step 2 — Nyquist-limited resolution (how many resolved line pairs per mm):
  nyquist_pixels_per_mm = pixels_per_mm / nyquist_factor
  nyquist_mm_per_pixel = 1 / nyquist_pixels_per_mm

  The Nyquist theorem states that to faithfully represent a feature, you need at least 2 pixels per feature (spatial frequency). A nyquist_factor of 2 means: one pixel sees the feature, one pixel sees the background. Features smaller than nyquist_mm_per_pixel cannot be reliably distinguished.

Step 3 — Measurement accuracy with subpixel interpolation:
  measurement_accuracy_mm = nyquist_mm_per_pixel × subpixel_factor

  Modern edge-detection algorithms can locate an edge to a fraction of a pixel (subpixel precision). A subpixel_factor of 0.1 means the algorithm can resolve 1/10 of a pixel. Typical achievable values: 0.1–0.3 pixels with good contrast and calibrated optics.

# Use Cases

- Determine whether a vision system can measure a feature or gap to within a required tolerance.
- Calculate required pixels/mm for a metrology application.
- Verify that sensor resolution and FOV combination is adequate for a defect size specification.
- Estimate the smallest crack, scratch, or gap the system can detect.
- Size the camera for a dimensional gauging application given tolerance requirements.
- Evaluate whether subpixel processing is needed to meet accuracy requirements.
- Compare two camera resolutions for a given FOV in terms of measurement capability.
- Determine if a 5 MP camera is adequate or a 12 MP camera is needed.
- Estimate the measurement accuracy for a given mm/pixel scale.
- Calculate required image resolution to inspect pharmaceutical tablet dimensions.
- Evaluate a PCB inspection setup for detecting traces of a given minimum width.
- Determine the pixel budget needed to measure a part to ±0.05 mm.

# Example Queries

- Can I measure 0.05 mm defects accurately?
- What measurement accuracy can I achieve?
- How many pixels per millimeter do I need for 0.1 mm accuracy?
- Expected measurement precision for this setup.
- Required imaging resolution for metrology.
- Will my system detect a 50 µm feature?
- My FOV is 200 mm and I have 2048 pixels — what accuracy can I achieve?
- I need to measure to ±0.1 mm — how many pixels do I need across 150 mm?
- Can I detect 0.2 mm cracks with 1024 pixels over 100 mm?
- Measurement accuracy for 2448 pixels over 300 mm object.
- I need ±0.05 mm accuracy — is 5 MP enough for a 200 mm FOV?
- What is the mm/pixel for this setup?
- Smallest detectable feature size at this resolution.
- I have 10 pixels/mm — what is my measurement accuracy?
- Will this camera detect a 0.1 mm gap?
- Required camera resolution for measuring a 10 mm diameter hole to ±0.02 mm.
- Can this system pass a 0.03 mm gauge R&R requirement?

# Input Meanings

object_size_mm:
Physical size of the object or field of view being measured, in millimeters. This determines the mm/pixel scale: a smaller FOV with the same pixel count gives finer resolution. Example: 200 mm wide object imaged with a 2448-pixel-wide camera → 2448/200 = 12.24 pixels/mm.

sensor_pixels:
Number of pixels spanning the object_size_mm dimension. Typically the sensor width in pixels for horizontal measurements. For vertical: use sensor height. For a line scan: number of pixels per line.

nyquist_factor:
The sampling factor applied for the Nyquist criterion. Use 2 as the standard value — it means at least 2 pixels per feature cycle (one on feature, one on background). Some applications use higher values (3–4) for conservative design. Do not use values below 2 — under-sampling produces aliasing.

subpixel_factor:
Fraction of a pixel that the image processing algorithm can resolve. Values:
- 1.0: pixel-level accuracy only (no subpixel interpolation).
- 0.5: coarse subpixel — simple centroid or gradient methods.
- 0.3: typical for well-tuned edge detection on high-contrast features.
- 0.1: excellent subpixel accuracy — requires calibrated optics, good contrast, and robust algorithm.
- 0.05: research-grade, usually not achievable in industrial conditions.

# Gotchas

- This calculator gives the theoretical achievable accuracy under ideal conditions (perfect focus, good contrast, no noise). Real-world accuracy is always worse due to optical aberrations, noise, lighting variation, and calibration errors.
- Nyquist applies to the detection limit: a feature must be at least 2 pixels wide to be reliably detected. For reliable measurement (not just detection), features should ideally be 5–10 pixels wide.
- Subpixel accuracy degrades with: poor focus (DOF violation), low contrast, noise, lens distortion, and inadequate calibration. A 0.1 pixel claim requires careful optical and algorithmic design.
- Measurement accuracy refers to the ability to locate an edge or centroid, not the ability to detect a feature's presence. A 0.05 mm feature can be detected with much coarser resolution than it can be measured.
- This does not account for lens distortion, which can cause mm-scale systematic errors across the FOV. Proper camera calibration (with a calibration target) is required for metrology applications.
- The result is accuracy for one measurement. Repeatability (gauge R&R) and absolute accuracy are different metrics. System-level factors (calibration, temperature, vibration) dominate in practice.
- If nyquist_factor < 2, results become physically unreliable. The formula will compute a value, but it violates the sampling theorem.

# Related Calculators

- fov_using_pixel_size: Use to find the mm/pixel scale for a given sensor and working distance, which feeds into this calculation.
- depth_of_field: Measurement accuracy is only achievable if the object is within the depth of field.
- sensor_geometry: Use to understand the physical sensor dimensions.
- line_scan_frequency: For line scan systems, pixels_per_mm defines resolution in both axes.
