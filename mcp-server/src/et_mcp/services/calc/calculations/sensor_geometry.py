from math import gcd, sqrt

from .types import SensorGeometryInput, SensorGeometryOutput, SensorCalculatorError


def calculate_sensor_geometry(
    inputs: SensorGeometryInput,
) -> SensorGeometryOutput:
    """
    Port of sensor-calc.html

    Inputs
    -------
    width_pixels:
        Horizontal resolution

    height_pixels:
        Vertical resolution

    pixel_size_um:
        Pixel size in microns

    Returns
    -------
    SensorGeometryOutput
    """

    width_pixels = inputs.width_pixels
    height_pixels = inputs.height_pixels
    pixel_size_um = inputs.pixel_size_um

    # --------------------------------------------------
    # Layer 3
    # Formula
    # --------------------------------------------------

    diagonal_pixels = sqrt(
        width_pixels**2 +
        height_pixels**2
    )

    width_mm = (
        width_pixels *
        pixel_size_um
    ) / 1000

    height_mm = (
        height_pixels *
        pixel_size_um
    ) / 1000

    diagonal_mm = (
        diagonal_pixels *
        pixel_size_um
    ) / 1000

    aspect_ratio_decimal = (
        width_pixels /
        height_pixels
    )

    # --------------------------------------------------
    # Layer 4
    # Business Rules
    # --------------------------------------------------

    width_mm = round(width_mm, 2)

    height_mm = round(height_mm, 2)

    diagonal_mm = round(
        diagonal_mm,
        2
    )

    diagonal_pixels = round(
        diagonal_pixels,
        2
    )

    aspect_ratio_decimal = round(
        aspect_ratio_decimal,
        2
    )

    divisor = gcd(
        width_pixels,
        height_pixels
    )

    reduced_x = width_pixels // divisor
    reduced_y = height_pixels // divisor

    aspect_ratio_fraction = (
        f"{reduced_x}:{reduced_y}"
    )

    return SensorGeometryOutput(
        width_mm=width_mm,
        height_mm=height_mm,
        diagonal_mm=diagonal_mm,

        width_pixels=width_pixels,
        height_pixels=height_pixels,
        diagonal_pixels=diagonal_pixels,

        aspect_ratio_decimal=aspect_ratio_decimal,
        aspect_ratio_fraction=aspect_ratio_fraction,

        valid=True,
        warning=None,
    )