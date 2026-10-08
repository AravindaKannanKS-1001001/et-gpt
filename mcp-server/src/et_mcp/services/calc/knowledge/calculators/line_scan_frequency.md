---
id: line_scan_frequency

category: line_scan

tags:
  - line_scan
  - line_scan_camera
  - line_rate
  - line_frequency
  - lines_per_second
  - khz
  - conveyor
  - conveyor_speed
  - throughput
  - data_rate
  - bandwidth
  - data_bandwidth
  - mb_per_second
  - megabytes_per_second
  - pixels_per_mm
  - resolution
  - required_pixels
  - sensor_pixels
  - camera_selection
  - web_inspection
  - print_inspection
  - fabric_inspection
  - food_inspection
  - pharmaceutical_inspection
  - continuous_web
  - moving_web
  - belt_inspection
  - 1d_sensor
  - linear_sensor
  - linescan
  - bytes_per_pixel
  - grayscale
  - color
  - acquisition_system
  - frame_grabber
  - interface_bandwidth
  - camera_link
  - gige
  - coaxpress
  - how_many_pixels
  - required_line_rate
  - what_line_rate
  - exposure_per_line

required_inputs:
  - object_width_mm
  - pixels_per_mm
  - bytes_per_pixel
  - conveyor_speed_mm_s

optional_inputs: []

description: "Calculate required line rate (kHz), sensor pixel count, exposure time per line, and data throughput for a line scan system"
chain_note: "Use the pixel_format_bytes reference (search_lookups → lookup) to get bytes_per_pixel if user specifies a format name like Mono8 or RGB24"
---

# Purpose

Calculate required number of sensor pixels, recommended standard camera model class, required line acquisition rate (kHz), maximum exposure time per line (ms and µs), and raw data throughput (MPix/s and MB/s) for a line scan camera application.

Line scan cameras capture one line at a time as objects move past them. This calculator sizes the camera for a given inspection width and conveyor speed.

# Explanation

Step 1 — Required sensor pixels:
  required_pixels = ceil(object_width_mm × pixels_per_mm)

Step 2 — Recommended camera: the smallest standard line scan resolution that meets required_pixels. Standard sizes: 512, 1024, 2048, 4096, 6144, 8192 pixels.

Step 3 — Required line frequency:
  pixels_per_mm determines the physical size per pixel in the conveyor direction.
  To maintain square pixels (equal resolution in both directions):
  line_frequency_khz = conveyor_speed_mm_s × pixels_per_mm / 1000

Step 4 — Exposure time per line:
  exposure_time_ms = 1 / line_frequency_khz  (maximum available exposure)
  exposure_time_us = exposure_time_ms × 1000

Step 5 — Data throughput:
  data_rate_mpix_s = sensor_pixels × line_frequency_khz / 1000
  data_rate_mb_s = data_rate_mpix_s × bytes_per_pixel

# Use Cases

- Size a line scan camera for a conveyor or web inspection application.
- Determine the required line acquisition frequency for a given belt speed and resolution.
- Estimate whether the interface bandwidth (GigE, Camera Link, CoaXPress) is sufficient for the data rate.
- Check if exposure time per line is long enough to collect sufficient light.
- Compare camera options (4K vs. 8K) for a given inspection width.
- Size the frame grabber or image acquisition system based on throughput.
- Determine whether the application is feasible at a given line speed.
- Evaluate the data storage and processing requirements for an inspection system.
- Design print inspection, fabric inspection, or pharmaceutical blister pack inspection systems.
- Calculate bandwidth for multi-camera line scan arrays.
- Check if GigE Vision (1 Gbps) is sufficient or CoaXPress/Camera Link is required.
- Estimate if the required line rate is within camera specifications.

# Example Queries

- What line rate is required for this conveyor speed?
- How many pixels does my line scan camera need?
- Required line frequency for conveyor inspection at 500 mm/s.
- Can my acquisition system handle the required throughput?
- Camera resolution for line scan application.
- Data throughput estimation for line scan setup.
- My belt runs at 1 m/s and I need 10 pixels/mm — what line rate do I need?
- I need 5 pixels/mm resolution over a 500 mm wide belt at 200 mm/s — size the camera.
- What is the required line frequency for a 400 mm belt at 300 mm/s and 8 px/mm?
- Will GigE Vision handle my line scan throughput?
- What is the data rate for a 4096-pixel camera at 20 kHz?
- My web runs at 100 m/min and I need 10 px/mm — what camera do I need?
- Print inspection at 200 m/min, need 20 px/mm — what line rate and data rate?
- Fabric inspection: 2 m wide web at 3 m/s, 5 px/mm — size the system.
- Can I use a standard USB3 camera interface for this line scan setup?
- Exposure time per line for 20 kHz line rate.

# Input Meanings

object_width_mm:
Width of the object or inspection area in the axis perpendicular to the direction of motion, in millimeters. For a conveyor, this is the cross-belt width (the full width that must be imaged).

pixels_per_mm:
Required imaging resolution expressed as pixels per millimeter in the cross-belt direction. Also determines the along-belt resolution (square pixels assumption). Examples: 2 px/mm for coarse inspection, 5 px/mm for general, 10 px/mm for fine detail, 20 px/mm for high-resolution print or pharmaceutical.

bytes_per_pixel:
Image data generated per pixel.
- 1: 8-bit grayscale (most common for machine vision)
- 2: 16-bit grayscale (HDR or scientific imaging)
- 3: 8-bit RGB color
- 4: 10-bit or 12-bit packed, or RGBA

conveyor_speed_mm_s:
Speed of the moving object or belt in millimeters per second.
- 1 m/s = 1000 mm/s
- 1 m/min = 16.67 mm/s
- 100 m/min = 1666.7 mm/s
- 200 m/min = 3333 mm/s

# Gotchas

- conveyor_speed must be in mm/s. Convert from m/min: divide by 60, then multiply by 1000.
- The exposure_time_ms output is the maximum available time per line — the actual exposure must be ≤ this value. Very high line rates leave almost no exposure time (e.g., 100 kHz = 10 µs max exposure), requiring very bright lighting.
- Line rates above 100 kHz are demanding. Very few cameras support >80 kHz at full resolution. Always verify the camera's maximum line rate spec.
- Data throughput above 800 MB/s requires CoaXPress or Camera Link HS. GigE Vision is limited to ~118 MB/s effective. USB3 Vision to ~350 MB/s.
- This calculator assumes square pixels (equal spatial resolution in cross-belt and along-belt directions). If isotropic resolution is not required, the along-belt resolution is: conveyor_speed_mm_s / line_frequency_khz / 1000 mm/line.
- The formula determines what the camera must achieve, not what it can achieve. Always cross-check the line_frequency_khz result against the camera's maximum line rate specification.
- For very wide objects (> 1000 mm), a single 8K camera may still have insufficient resolution. Multiple cameras or a stitched array may be required.
- Lighting is critical: exposure per line must be sufficient to achieve adequate SNR. Very short exposures require very intense (and often strobed) illumination.

# Related Calculators

- exposure_time: For area scan cameras on moving conveyors — equivalent motion blur calculation.
- measurement_accuracy: Check if the pixels_per_mm value achieves the required measurement precision.
- fov_using_pixel_size: Not directly applicable to line scan (which has no discrete frame), but useful for understanding the cross-belt imaging geometry.
