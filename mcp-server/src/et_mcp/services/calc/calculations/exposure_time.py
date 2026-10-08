from .types import ExposureTimeInput, ExposureTimeOutput, ExposureTimeCalculatorError

def calculate_exposure_time(
    inputs: ExposureTimeInput,
) -> ExposureTimeOutput:
    """
    Port of camera-exposure-time.html
    """

    object_length_mm = (
        inputs.object_length_mm
    )

    conveyor_speed_mm_s = (
        inputs.conveyor_speed_mm_s
    )

    sensor_pixels = (
        inputs.sensor_pixels
    )

    allowed_blur_pixels = (
        inputs.allowed_blur_pixels
    )

    # ----------------------------------
    # Layer 3
    # Formula
    # ----------------------------------

    resolution_px_per_mm = (
        sensor_pixels /
        object_length_mm
    )

    motion_px_per_second = (
        resolution_px_per_mm *
        conveyor_speed_mm_s
    )

    exposure_time_ms = (
        1 /
        motion_px_per_second
    ) * allowed_blur_pixels * 1000

    # ----------------------------------
    # Layer 4
    # Business Rules
    # ----------------------------------

    exposure_time_ms = round(
        exposure_time_ms,
        4
    )

    # Original JS warnings

    if exposure_time_ms < 0.03:
        return ExposureTimeOutput(
            exposure_time_ms=exposure_time_ms,
            valid=True,
            warning=(
                "Check minimum shutter "
                "time supported by camera."
            ),
        )

    if exposure_time_ms > 500:
        return ExposureTimeOutput(
            exposure_time_ms=exposure_time_ms,
            valid=True,
            warning=(
                "Value exceeds reasonable "
                "operating range."
            ),
        )

    return ExposureTimeOutput(
        exposure_time_ms=exposure_time_ms,
        valid=True,
        warning=None,
    )