from .types import FOVInput, FOVOutput, FOVCalculatorError


def calculate_fov(
    inputs: FOVInput,
) -> FOVOutput:
    """
    Port of fov.html
    """

    sensor_size_mm = inputs.sensor_size_mm
    working_distance_mm = (
        inputs.working_distance_mm
    )
    focal_length_mm = (
        inputs.focal_length_mm
    )

    # ----------------------------------
    # Layer 2
    # Validation
    # ----------------------------------

    # JS hard limits

    if sensor_size_mm >= 200:
        raise FOVCalculatorError(
            "Sensor size exceeds calculator limit."
        )

    if focal_length_mm >= 2000:
        raise FOVCalculatorError(
            "Focal length exceeds calculator limit."
        )

    # ----------------------------------
    # Layer 3
    # Formula
    # ----------------------------------

    ratio = (
        working_distance_mm
        / focal_length_mm
    )

    fov = sensor_size_mm * (
        ratio - 1
    )

    # ----------------------------------
    # Layer 4
    # Business Rules
    # ----------------------------------

    fov = round(fov, 2)

    # JS rejects negative values

    if fov <= 0:
        return FOVOutput(
            fov_mm=fov,
            valid=False,
            warning=(
                f"Invalid optical configuration: working distance ({working_distance_mm:g} mm) "
                f"must be larger than focal length ({focal_length_mm:g} mm). "
                "If the focal length is what you need to find, use the focal_length "
                "calculator with sensor size, working distance and target size instead."
            ),
        )

    # JS limits

    if fov <= 2:
        return FOVOutput(
            fov_mm=fov,
            valid=False,
            warning="FOV below calculator range."
        )

    if fov > 50000:
        return FOVOutput(
            fov_mm=fov,
            valid=False,
            warning="FOV exceeds calculator range."
        )

    return FOVOutput(
        fov_mm=fov,
        valid=True,
        warning=None
    )