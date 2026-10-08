import math

from .types import LineScanInput, LineScanOutput

STANDARD_SENSORS = (512, 1024, 2048, 4096, 6144, 8192, 12288)
# Beyond this, stitching more line-scan cameras is rarely practical.
MAX_MULTI_CAMERA_PIXELS = 49152


def _select_camera(required_pixels: int):
    """Smallest standard line-scan resolution that covers required_pixels."""
    for pixels in STANDARD_SENSORS:
        if required_pixels <= pixels:
            label = f"{pixels} pix line scan camera" if pixels < 1024 else f"{pixels // 1024}K line scan camera"
            return label, pixels, None
    if required_pixels <= MAX_MULTI_CAMERA_PIXELS:
        cameras = math.ceil(required_pixels / 12288)
        return (f"{cameras} x 12K line scan cameras", required_pixels,
                f"{required_pixels} pixels exceed a single 12K sensor; about {cameras} stitched cameras would be needed.")
    return ("No standard line scan setup", required_pixels,
            f"{required_pixels} pixels across the object is beyond practical multi-camera setups; check the object width and resolution.")


def calculate_line_scan(
    inputs: LineScanInput,
) -> LineScanOutput:
    """
    Port of camera-line-scan-frequency.html.
    Intermediate values stay unrounded; rounding is applied only to outputs.
    """

    object_width_mm = inputs.object_width_mm
    pixels_per_mm = inputs.pixels_per_mm
    bytes_per_pixel = inputs.bytes_per_pixel
    conveyor_speed_mm_s = inputs.conveyor_speed_mm_s

    # Every millimetre of width must be covered, so partial pixels round up.
    required_pixels = math.ceil(round(object_width_mm * pixels_per_mm, 9))

    camera_name, sensor_pixels, warning = _select_camera(required_pixels)

    # JS: frequenz = Pix * BandMM / 1000
    line_frequency_khz = pixels_per_mm * conveyor_speed_mm_s / 1000

    # JS: belzeit = 1000/(Pix*BandMM)
    exposure_time_ms = 1000 / (pixels_per_mm * conveyor_speed_mm_s)

    # JS: datenrate = sensor*frequenz/1000
    data_rate_mpix_s = sensor_pixels * line_frequency_khz / 1000

    return LineScanOutput(
        required_pixels=required_pixels,
        recommended_camera=camera_name,
        sensor_pixels=sensor_pixels,
        line_frequency_khz=round(line_frequency_khz, 4),
        exposure_time_ms=round(exposure_time_ms, 4),
        exposure_time_us=round(exposure_time_ms * 1000, 1),
        data_rate_mpix_s=round(data_rate_mpix_s, 4),
        data_rate_mb_s=round(data_rate_mpix_s * bytes_per_pixel, 4),
        valid=warning is None,
        warning=warning,
    )
