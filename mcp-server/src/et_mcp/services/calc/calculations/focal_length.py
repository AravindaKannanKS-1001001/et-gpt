from .types import FocalLengthInput, FocalLengthOutput, FocalLengthCalculatorError

def calculate_focal_length(
    inputs: FocalLengthInput,
) -> FocalLengthOutput:
    """
    Port of focal-length.html

    Inputs
    -------
    object_size_mm:
        Object width / FOV in mm

    working_distance_mm:
        Distance from lens to object

    sensor_size_mm:
        Sensor dimension being used
        (width, height, or diagonal)

    Returns
    -------
    FocalLengthOutput
    """

    object_size_mm = inputs.object_size_mm
    working_distance_mm = (
        inputs.working_distance_mm
    )
    sensor_size_mm = (
        inputs.sensor_size_mm
    )

    # --------------------------------------------------
    # Layer 2
    # Validation
    # --------------------------------------------------

    # JS calculator hard limit

    if sensor_size_mm >= 200:
        raise FocalLengthCalculatorError(
            "Sensor size exceeds calculator limit (200 mm)."
        )

    # --------------------------------------------------
    # Layer 3
    # Formula
    # --------------------------------------------------

    magnification_term = (
        object_size_mm /
        sensor_size_mm
    )

    focal_length = (
        working_distance_mm
        / (magnification_term + 1)
    )

    # --------------------------------------------------
    # Layer 4
    # Business Rules
    # --------------------------------------------------

    # JS behavior:
    # result=result*10;
    # result=Math.round(result);
    # result=result/10;

    focal_length = round(
        focal_length,
        1
    )

    # calculator accepts:
    # 1.4 < focal <= 500

    if focal_length <= 1.4:
        return FocalLengthOutput(
            focal_length_mm=focal_length,
            valid=False,
            warning=(
                "Calculated focal length "
                "below supported range."
            ),
        )

    if focal_length > 500:
        return FocalLengthOutput(
            focal_length_mm=focal_length,
            valid=False,
            warning=(
                "Calculated focal length "
                "above supported range."
            ),
        )

    return FocalLengthOutput(
        focal_length_mm=focal_length,
        valid=True,
        warning=None,
    )