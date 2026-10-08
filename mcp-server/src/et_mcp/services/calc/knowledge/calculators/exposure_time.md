---
id: exposure_time

category: motion

tags:
  - exposure_time
  - exposure
  - shutter_speed
  - maximum_exposure
  - motion_blur
  - blur
  - blur_limit
  - pixel_blur
  - allowed_blur
  - conveyor
  - conveyor_speed
  - moving_object
  - moving_part
  - object_speed
  - line_speed
  - belt_speed
  - web_speed
  - fast_moving
  - high_speed
  - inspection_speed
  - strobe
  - flash
  - shutter
  - integration_time
  - freeze_motion
  - frozen_image
  - image_sharpness
  - dynamic_blur
  - motion_artifact
  - smear
  - motion_smear
  - how_long_exposure
  - max_shutter
  - safe_exposure

required_inputs:
  - object_length_mm
  - conveyor_speed_mm_s
  - sensor_pixels
  - allowed_blur_pixels

optional_inputs: []

description: "Calculate maximum exposure time to keep motion blur within a pixel limit when imaging a moving object"
---

# Purpose

Calculate the maximum allowable camera exposure (integration) time to keep motion blur within a specified pixel limit when imaging a moving object. Returns exposure time in milliseconds.

Answers: "How long can I keep the shutter open before the image blurs too much?"

# Explanation

The formula derives mm/pixel from the imaging setup, then calculates how many microseconds the object can move one allowed_blur amount:

  mm_per_pixel = object_length_mm / sensor_pixels
  max_object_movement_mm = allowed_blur_pixels × mm_per_pixel
  exposure_time_ms = (max_object_movement_mm / conveyor_speed_mm_s) × 1000

In plain terms: if one pixel represents 0.1 mm, and you allow 0.5 pixels of blur, the object can move at most 0.05 mm during the exposure. At 500 mm/s, that takes 0.1 ms. So maximum exposure = 0.1 ms.

# Use Cases

- Determine safe exposure time for a conveyor belt inspection system.
- Calculate maximum integration time before motion blur degrades OCR, barcode reading, or defect detection.
- Estimate whether a global shutter camera is needed (if calculated exposure is too short for available light).
- Evaluate whether LED strobe lighting is necessary (very short exposures need very bright strobes).
- Design exposure budget for high-speed inspection lines.
- Check if rolling shutter cameras are adequate or if global shutter is required.
- Determine if available lighting is sufficient for the required exposure time.
- Compare motion blur at different conveyor speeds.
- Size a strobe light based on the required short exposure time.
- Verify inspection system specs for a new production line speed requirement.
- Determine the maximum allowable line speed for a fixed camera and lighting setup.
- Evaluate whether increasing allowed_blur_pixels relaxes the lighting requirement acceptably.

# Example Queries

- What is the maximum exposure time before motion blur exceeds 1 pixel?
- Conveyor moving at 1000 mm/s — how long can I expose?
- Maximum exposure before blur exceeds 0.5 pixels.
- Motion blur calculation for inspection systems.
- What exposure time is safe at this conveyor speed?
- I have a 2 m/s belt and a 2448-pixel sensor spanning 300 mm — what is my max exposure?
- How long can I expose at 500 mm/s line speed with 1 pixel blur limit?
- My belt runs at 1.5 m/s — what is the maximum shutter speed?
- Exposure time for 800 mm/s conveyor, 200 mm object, 1024 pixels, 0.5 pixel blur.
- Freeze motion on a high-speed line — what exposure do I need?
- Will 0.1 ms exposure freeze a 2 m/s conveyor?
- My line runs at 3 m/s — do I need a strobe?
- What is the max integration time for my camera?
- How fast is the belt moving in mm/s? My line is 120 m/min.
- Calculate motion budget for printing inspection at 200 m/min.
- Web inspection at 5 m/s — max exposure time.

# Input Meanings

object_length_mm:
The physical length of the object (or field of view) along the direction of motion in millimeters. This is used to determine the mm/pixel scale. For a conveyor, this is the width of the inspection area in the direction the belt moves (usually the conveyor travel direction maps to the horizontal axis of the image).

conveyor_speed_mm_s:
Speed of the moving object or conveyor in millimeters per second.
- 1 m/s = 1000 mm/s
- 1 m/min = 16.67 mm/s
- 100 m/min = 1666.7 mm/s
- 300 m/min = 5000 mm/s (typical high-speed printing/web)

sensor_pixels:
Number of camera sensor pixels spanning the object_length_mm dimension. For a 2448-pixel-wide camera viewing a 300 mm wide area, sensor_pixels = 2448.

allowed_blur_pixels:
Maximum acceptable motion blur in pixels. Typical values:
- 1.0 pixel: standard for most machine vision inspection.
- 0.5 pixels: tighter requirement for sub-pixel measurement or fine feature detection.
- 2.0 pixels: acceptable for coarse presence/absence inspection.
- 0.3 pixels: for high-precision OCR, micro-defect detection.

# Gotchas

- conveyor_speed must be in mm/s, not m/s or m/min. Convert first: 1 m/s = 1000 mm/s, 1 m/min = 16.67 mm/s.
- The result is the maximum exposure time. Using shorter exposure is always safer but requires more light.
- Short exposure times (< 0.5 ms) typically require strobe lighting. Continuous lighting at those durations delivers very little light per frame.
- This calculator does not account for rolling shutter effects. A rolling shutter camera has additional motion distortion beyond blur — for fast objects on high lines speeds, global shutter is strongly preferred.
- The formula assumes the object moves in the same axis as sensor_pixels (typically horizontal). If the belt moves along the vertical axis, use the vertical pixel count.
- Very short exposures (< 0.05 ms) may require pulsed laser or high-intensity LED strobe with µs-precision timing.
- Motion blur from vibration of the camera mount is not accounted for. In practice, mechanical vibration can be the dominant blur source.
- Increasing allowed_blur_pixels relaxes the exposure requirement but degrades image sharpness. For dimensional measurement, keep it at 0.5 or less.
- This calculator gives the exposure time budget. Lighting engineers use this to size the strobe power, accounting for aperture and sensor sensitivity.

# Related Calculators

- depth_of_field: The DOF–exposure trade-off partner. Stopping down for DOF reduces light and may make the calculated exposure time unachievable.
- line_scan_frequency: For line scan cameras, exposure time per line is derived differently and tied to line rate.
- fov_using_pixel_size: Use to find mm/pixel independently, which also determines the motion blur scale.
