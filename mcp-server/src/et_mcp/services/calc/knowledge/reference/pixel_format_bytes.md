---
id: pixel_format_bytes

category: reference

tags:
  - bytes_per_pixel
  - pixel_format
  - image_format
  - bit_depth
  - bits_per_pixel
  - image_encoding
  - mono
  - monochrome
  - grayscale
  - greyscale
  - color
  - rgb
  - bayer
  - yuv
  - pixel_encoding
  - mono8
  - mono10
  - mono12
  - mono16
  - bayer8
  - yuv16
  - rgb24
  - 8_bit
  - 10_bit
  - 12_bit
  - 16_bit
  - 24_bit
  - 32_bit
  - 48_bit
  - image_data_size
  - pixel_size_bytes
  - bandwidth_calculation
  - throughput_calculation
  - data_rate
  - mb_per_second
  - camera_link_bandwidth
  - gige_bandwidth
  - coaxpress_bandwidth
  - usb3_bandwidth
  - interface_bandwidth
  - frame_size_bytes
  - image_size_bytes
  - how_many_bytes
  - bytes_per_image
  - image_memory
  - storage_requirement
  - line_scan_bit_depth
  - area_scan_bit_depth
  - genicam
  - pixel_format_genicam
  - packed_format
  - unpacked_format

required_inputs: []
optional_inputs: []
description: "Bytes per pixel by pixel format (Mono8=1, RGB24=3, Bit32=4, etc.) for bandwidth and frame size calculations"
notes:
  packed_formats: "Mono10 packed = 1.25 B/px, Mono12 packed = 1.5 B/px; Bayer10 packed = 1.25 B/px, Bayer12 packed = 1.5 B/px"
  color_handling: "Bayer 8 is 1 B/px raw from sensor; host-side memory for demosaiced image is 3 B/px"
common_uses:
  - "Calculate frame size in bytes: width × height × bytes_per_pixel"
  - "Estimate camera interface bandwidth: pixel_rate_mpix_s × bytes_per_pixel = data_rate_mb_s"
  - "Check interface sufficiency: GigE ~118 MB/s, USB3 ~350 MB/s, 10GigE ~1180 MB/s"
---

# Purpose

Lookup table mapping camera pixel format (image encoding, bit depth) to bytes per pixel. Used to calculate raw image data throughput, bandwidth requirements, memory usage, and storage requirements.

Use this when the line_scan_frequency calculator or any bandwidth calculation requires bytes_per_pixel and the user has specified an image format like "Mono 8" or "RGB 24" rather than a raw number.

# Pixel Format → Bytes Per Pixel

| Format / Encoding    | Bits Per Pixel | Bytes Per Pixel | Notes                                  |
| -------------------- | -------------: | --------------: | -------------------------------------- |
| Mono 8               |              8 |               1 | Standard 8-bit grayscale. Most common. |
| Bayer 8              |              8 |               1 | Raw color (Bayer pattern), 8-bit       |
| Mono 10 (unpacked)   |             16 |               2 | 10-bit stored in 16-bit container      |
| Mono 12 (unpacked)   |             16 |               2 | 12-bit stored in 16-bit container      |
| Mono 16              |             16 |               2 | Full 16-bit grayscale                  |
| YUV 4:2:2 / YUV 16   |             16 |               2 | Color, YCbCr encoding                  |
| Bayer 12 (unpacked)  |             16 |               2 | Raw color 12-bit in 16-bit container   |
| RGB 24               |             24 |               3 | 8 bits each R, G, B                    |
| BGR 24               |             24 |               3 | Same as RGB, different channel order   |
| 32-bit               |             32 |               4 | RGBA or padded 10/12-bit               |
| RGB 48               |             48 |               6 | 16 bits each R, G, B                   |
| 48-bit               |             48 |               6 | Full 16-bit color                      |

# JSON Lookup

```json
{
  "bytes_per_pixel": {
    "Mono8":        1,
    "Bayer8":       1,
    "Mono10":       2,
    "Mono12":       2,
    "Mono16":       2,
    "YUV16":        2,
    "Bayer12":      2,
    "RGB24":        3,
    "BGR24":        3,
    "Bit32":        4,
    "RGB48":        6,
    "Bit48":        6
  }
}
```

# Packed vs Unpacked Formats

Some cameras offer "packed" variants that save bandwidth by not padding to byte boundaries:

| Format          | Packed Bytes/Pixel | Unpacked Bytes/Pixel |
| --------------- | -----------------: | -------------------: |
| Mono 10 packed  |              1.25  |                  2.0 |
| Mono 12 packed  |              1.5   |                  2.0 |
| Bayer 10 packed |              1.25  |                  2.0 |
| Bayer 12 packed |              1.5   |                  2.0 |

For bandwidth calculations with packed formats, use the packed value. Most frame grabbers and GigE cameras support both; CoaXPress typically uses packed.

# How to Use in Throughput Calculations

With line_scan_frequency calculator:
  data_rate_mb_s = data_rate_mpix_s × bytes_per_pixel

Example:
- 4K line scan at 20 kHz, Mono 8:
  4096 pixels × 20000 lines/s = 81.92 MPix/s × 1 byte = 81.92 MB/s → GigE is sufficient (limit ~118 MB/s)

- Same camera, RGB 24:
  81.92 MPix/s × 3 bytes = 245.76 MB/s → GigE is NOT sufficient, need USB3 or Camera Link

# Interface Bandwidth Guide

| Interface          | Max Effective Throughput | Notes                          |
| ------------------ | -----------------------: | ------------------------------ |
| GigE Vision        |              ~118 MB/s   | 1 Gbps Ethernet, common        |
| USB3 Vision        |              ~350 MB/s   | USB 3.0, plug-and-play         |
| 5GigE Vision       |              ~590 MB/s   | 5 Gbps Ethernet                |
| Camera Link Base   |              ~255 MB/s   | Older standard, still used     |
| Camera Link Full   |              ~680 MB/s   | High-speed industrial          |
| CoaXPress 1.0 ×1  |              ~125 MB/s   | Single coax cable              |
| CoaXPress 2.0 ×4  |            ~2500 MB/s    | 4× coax, very high speed       |
| 10GigE Vision      |             ~1180 MB/s   | 10 Gbps Ethernet               |

# Choosing Bit Depth

| Bit Depth | When to Use                                                              |
| --------- | ------------------------------------------------------------------------ |
| 8-bit     | Standard inspection, presence/absence, sufficient for most tasks         |
| 10-bit    | Better dynamic range for high-contrast scenes (specular surfaces)        |
| 12-bit    | Precision metrology, subtle gray-level differences, HDR                  |
| 16-bit    | Scientific imaging, fluorescence, very low light                         |
| Color (Bayer/RGB) | Color-based defect detection, label inspection, food color grading |

# Gotchas

- Mono 10 and Mono 12 "unpacked" formats use 2 bytes per pixel even though the data only has 10 or 12 significant bits. The upper bits are padded with zeros. Some systems can use "packed" format to save bandwidth but require compatible frame grabbers.
- RGB 24 is 3× the bandwidth of Mono 8 at the same resolution and frame rate. Many GigE systems cannot sustain RGB 24 at full resolution without frame drops.
- Color via Bayer mosaic (Bayer 8) is 1 byte/pixel raw but requires demosaicing, which inflates it to 3 bytes/pixel in processed form. Use 1 byte/pixel for camera-side bandwidth, 3 bytes/pixel for host-side memory estimation.
- bytes_per_pixel is the raw sensor output. Processing pipelines (e.g., 32-bit float per channel) will require more memory per image for intermediate buffers.

# Common Example Queries This Knowledge Resolves

- How many bytes per pixel is Mono 8?
- What is bytes_per_pixel for RGB 24?
- What encoding should I use for my line scan camera?
- How much bandwidth does a Mono 12 camera require?
- What is the data rate for a 4K line scan camera in Mono 8?
- How many MB/s does my camera produce?
- Is GigE sufficient for my camera at RGB 24?
- Bytes per pixel for 16-bit grayscale.
- What pixel format for high dynamic range inspection?
- How much storage does one image frame require?
- Convert pixel format to bytes for bandwidth calculation.
- What is bytes_per_pixel for YUV 16?
