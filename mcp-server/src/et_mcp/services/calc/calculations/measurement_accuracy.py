from .types import MeasurementAccuracyInput, MeasurementAccuracyOutput, MeasurementAccuracyCalculatorError


def calculate_measurement_accuracy(
    inputs: MeasurementAccuracyInput,
) -> MeasurementAccuracyOutput:
    """
    Port of camera-measurement-accuracy.html
    """

    object_size_mm = (
        inputs.object_size_mm
    )

    sensor_pixels = (
        inputs.sensor_pixels
    )

    nyquist_factor = (
        inputs.nyquist_factor
    )

    subpixel_factor = (
        inputs.subpixel_factor
    )

    # ----------------------------------
    # Layer 3
    # Formula
    # ----------------------------------

    measurement_accuracy_mm = (
        (
            object_size_mm /
            sensor_pixels
        )
        * subpixel_factor
        * nyquist_factor
    )

    pixels_per_mm = (
        sensor_pixels /
        object_size_mm
    )

    mm_per_pixel = (
        1 /
        pixels_per_mm
    )

    nyquist_pixels_per_mm = (
        pixels_per_mm /
        nyquist_factor
    )

    nyquist_mm_per_pixel = (
        1 /
        nyquist_pixels_per_mm
    )

    # ----------------------------------
    # Layer 4
    # Business Rules
    # ----------------------------------

    pixels_per_mm = round(
        pixels_per_mm,
        2
    )

    # Six decimals keep micron-scale resolution (0.0005 mm) visible.
    mm_per_pixel = round(
        mm_per_pixel,
        6
    )

    nyquist_pixels_per_mm = round(
        nyquist_pixels_per_mm,
        3
    )

    nyquist_mm_per_pixel = round(
        nyquist_mm_per_pixel,
        6
    )

    measurement_accuracy_mm = round(
        measurement_accuracy_mm,
        4
    )

    return MeasurementAccuracyOutput(
        pixels_per_mm=pixels_per_mm,
        mm_per_pixel=mm_per_pixel,

        nyquist_pixels_per_mm=
            nyquist_pixels_per_mm,

        nyquist_mm_per_pixel=
            nyquist_mm_per_pixel,

        measurement_accuracy_mm=
            measurement_accuracy_mm,

        valid=True,
        warning=(
            f"nyquist_factor {nyquist_factor} is below 2; features smaller than "
            "two pixels cannot be measured reliably."
            if nyquist_factor < 2 else None
        ),
    )