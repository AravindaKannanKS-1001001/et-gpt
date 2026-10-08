from math import gcd, sqrt

from .types import AdvancedFOVInput, AdvancedFOVOutput, AdvancedFOVCalculatorError

def calculate_advanced_fov(
    inputs: AdvancedFOVInput,
) -> AdvancedFOVOutput:
    """
    Port of fov-adv.html
    """

    width_pixels = inputs.width_pixels
    height_pixels = inputs.height_pixels
    pixel_size_um = inputs.pixel_size_um
    focal_length_mm = inputs.focal_length_mm
    working_distance_mm = inputs.working_distance_mm

    # ----------------------------------
    # Layer 3
    # Sensor Geometry
    # ----------------------------------

    sensor_width_mm = (
        width_pixels *
        pixel_size_um
    ) / 1000

    sensor_height_mm = (
        height_pixels *
        pixel_size_um
    ) / 1000

    sensor_diagonal_pixels = round(
        sqrt(
            width_pixels**2 +
            height_pixels**2
        )
    )

    sensor_diagonal_mm = (
        sqrt(
            width_pixels**2 +
            height_pixels**2
        )
        * pixel_size_um
        / 1000
    )

    # ----------------------------------
    # Layer 3
    # Optical Formula
    # ----------------------------------

    magnification_term = (
        working_distance_mm /
        focal_length_mm
    ) - 1

    fov_x_mm = (
        sensor_width_mm *
        magnification_term
    )

    fov_y_mm = (
        sensor_height_mm *
        magnification_term
    )

    fov_diagonal_mm = (
        sensor_diagonal_mm *
        magnification_term
    )

    # ----------------------------------
    # Layer 4
    # Business Rules
    # ----------------------------------

    sensor_width_mm = round(sensor_width_mm, 2)
    sensor_height_mm = round(sensor_height_mm, 2)
    sensor_diagonal_mm = round(sensor_diagonal_mm, 2)

    fov_x_mm = round(fov_x_mm, 2)
    fov_y_mm = round(fov_y_mm, 2)
    fov_diagonal_mm = round(fov_diagonal_mm, 2)

    if (
        fov_x_mm <= 0
        or fov_y_mm <= 0
        or fov_diagonal_mm <= 0
    ):
        return AdvancedFOVOutput(
            sensor_width_mm=sensor_width_mm,
            sensor_height_mm=sensor_height_mm,
            sensor_diagonal_mm=sensor_diagonal_mm,
            sensor_diagonal_pixels=sensor_diagonal_pixels,
            aspect_ratio_decimal=0,
            aspect_ratio_fraction="",
            fov_x_mm=fov_x_mm,
            fov_y_mm=fov_y_mm,
            fov_diagonal_mm=fov_diagonal_mm,
            valid=False,
            warning=(
                "Invalid optical configuration: working distance must be larger than "
                "focal length. If the focal length is what you need to find, use the "
                "focal_length calculator with sensor size, working distance and target "
                "size instead."
            ),
        )

    ratio_decimal = round(
        width_pixels / height_pixels,
        2,
    )

    divisor = gcd(
        width_pixels,
        height_pixels,
    )

    ratio_fraction = (
        f"{width_pixels // divisor}:"
        f"{height_pixels // divisor}"
    )

    return AdvancedFOVOutput(
        sensor_width_mm=sensor_width_mm,
        sensor_height_mm=sensor_height_mm,
        sensor_diagonal_mm=sensor_diagonal_mm,
        sensor_diagonal_pixels=sensor_diagonal_pixels,
        aspect_ratio_decimal=ratio_decimal,
        aspect_ratio_fraction=ratio_fraction,
        fov_x_mm=fov_x_mm,
        fov_y_mm=fov_y_mm,
        fov_diagonal_mm=fov_diagonal_mm,
        valid=True,
        warning=None,
    )