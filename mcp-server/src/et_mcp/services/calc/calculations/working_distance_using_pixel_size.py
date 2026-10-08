from math import gcd, sqrt

from .types import AdvancedWorkingDistanceInput, AdvancedWorkingDistanceOutput, AdvancedWorkingDistanceCalculatorError

def calculate_advanced_working_distance(
    inputs: AdvancedWorkingDistanceInput,
) -> AdvancedWorkingDistanceOutput:
    """
    Port of working-distance-adv.html
    """

    width_pixels = inputs.width_pixels
    height_pixels = inputs.height_pixels
    pixel_size_um = inputs.pixel_size_um
    focal_length_mm = inputs.focal_length_mm
    fov_x_mm = inputs.fov_x_mm

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
    # Main Formula
    # ----------------------------------

    working_distance_mm = (
        focal_length_mm
        * (
            fov_x_mm /
            sensor_width_mm
            + 1
        )
    )

    # ----------------------------------
    # Derived Outputs
    # ----------------------------------

    ratio = (
        width_pixels /
        height_pixels
    )

    fov_y_mm = (
        fov_x_mm /
        ratio
    )

    fov_diagonal_mm = sqrt(
        fov_x_mm**2 +
        fov_y_mm**2
    )

    # ----------------------------------
    # Layer 4
    # Business Rules
    # ----------------------------------

    working_distance_mm = round(
        working_distance_mm,
        2
    )

    sensor_width_mm = round(
        sensor_width_mm,
        2
    )

    sensor_height_mm = round(
        sensor_height_mm,
        2
    )

    sensor_diagonal_mm = round(
        sensor_diagonal_mm,
        2
    )

    fov_y_mm = round(
        fov_y_mm,
        2
    )

    fov_diagonal_mm = round(
        fov_diagonal_mm,
        2
    )

    ratio_decimal = round(
        ratio,
        2
    )

    divisor = gcd(
        width_pixels,
        height_pixels
    )

    ratio_fraction = (
        f"{width_pixels // divisor}:"
        f"{height_pixels // divisor}"
    )

    # fov_y is derived from fov_x and the pixel aspect ratio, so FOV X < FOV Y
    # only means a portrait sensor (more rows than columns). The original JS
    # rejected that; it is valid, but worth flagging in case width/height were swapped.
    warning = (
        "Sensor is taller than it is wide (portrait); check that width_pixels "
        "and height_pixels are not swapped."
        if fov_x_mm < fov_y_mm else None
    )

    return AdvancedWorkingDistanceOutput(
        working_distance_mm=working_distance_mm,

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
        warning=warning,
    )