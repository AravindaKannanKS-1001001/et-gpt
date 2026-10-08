from .types import WorkingDistanceInput, WorkingDistanceOutput, WorkingDistanceCalculatorError

def calculate_working_distance(
    inputs: WorkingDistanceInput,
) -> WorkingDistanceOutput:
    """
    Port of working-distance.html

    Inputs
    -------
    object_size_mm:
        Object width / FOV in mm

    sensor_size_mm:
        Sensor dimension in mm

    focal_length_mm:
        Lens focal length in mm

    Returns
    -------
    WorkingDistanceOutput
    """

    object_size_mm = inputs.object_size_mm
    sensor_size_mm = inputs.sensor_size_mm
    focal_length_mm = inputs.focal_length_mm

    # --------------------------------------------------
    # Layer 2
    # Validation
    # --------------------------------------------------

    # Original JS calculator limits

    if sensor_size_mm >= 200:
        raise WorkingDistanceCalculatorError(
            "Sensor size exceeds calculator limit (200 mm)."
        )

    if focal_length_mm > 2000:
        raise WorkingDistanceCalculatorError(
            "Focal length exceeds calculator limit (2000 mm)."
        )

    # --------------------------------------------------
    # Layer 3
    # Formula
    # --------------------------------------------------

    magnification_term = (
        object_size_mm / sensor_size_mm
    )

    working_distance = (
        focal_length_mm
        * (magnification_term + 1)
    )

    # --------------------------------------------------
    # Layer 4
    # Business Rules
    # --------------------------------------------------

    # Original JS:
    #
    # result=result*10;
    # result=Math.round(result);
    # result=result/10;

    working_distance = round(
        working_distance,
        1
    )

    # Original calculator limits:
    #
    # result > 50
    # result <= 500000

    if working_distance <= 50:
        return WorkingDistanceOutput(
            working_distance_mm=working_distance,
            valid=False,
            warning=(
                "Working distance below "
                "calculator range."
            ),
        )

    if working_distance > 500000:
        return WorkingDistanceOutput(
            working_distance_mm=working_distance,
            valid=False,
            warning=(
                "Working distance exceeds "
                "calculator range."
            ),
        )

    return WorkingDistanceOutput(
        working_distance_mm=working_distance,
        valid=True,
        warning=None,
    )