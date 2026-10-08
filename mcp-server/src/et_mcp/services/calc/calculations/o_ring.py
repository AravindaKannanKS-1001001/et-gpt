from .types import ORingInput, ORingOutput, ORingCalculatorError



def calculate_o_ring(
    inputs: ORingInput,
) -> ORingOutput:
    """
    Port of o-ring-calc.html

    Parameters
    ----------
    object_size_mm:
        Desired field of view

    minimum_object_distance_mm:
        Lens MOD

    sensor_size_mm:
        Sensor dimension

    focal_length_mm:
        Lens focal length
    """

    object_size_mm = (
        inputs.object_size_mm
    )

    minimum_object_distance_mm = (
        inputs.minimum_object_distance_mm
    )

    sensor_size_mm = (
        inputs.sensor_size_mm
    )

    focal_length_mm = (
        inputs.focal_length_mm
    )

    # ----------------------------------
    # Layer 2
    # Validation
    # ----------------------------------

    if sensor_size_mm >= 200:
        raise ORingCalculatorError(
            "Sensor size exceeds calculator limit."
        )

    if focal_length_mm >= 2000:
        raise ORingCalculatorError(
            "Focal length exceeds calculator limit."
        )

    # ----------------------------------
    # Layer 3
    # Desired Working Distance
    # ----------------------------------

    required_working_distance_mm = (
        focal_length_mm
        * (
            object_size_mm /
            sensor_size_mm
            + 1
        )
    )

    # Compare unrounded; round only what is reported.
    reported_working_distance_mm = round(
        required_working_distance_mm
    )

    # ----------------------------------
    # Layer 4
    # Business Rules
    # ----------------------------------

    # Lens can already focus there

    if (
        minimum_object_distance_mm
        <=
        required_working_distance_mm
    ):
        return ORingOutput(
            required_working_distance_mm=
                reported_working_distance_mm,

            extension_ring_required=False,

            extension_ring_mm=0.0,

            valid=True,

            warning="Extension ring not needed."
        )

    # ----------------------------------
    # Extension Ring Calculation
    # ----------------------------------

    object_size_at_mod = (
        sensor_size_mm
        *
        (
            minimum_object_distance_mm /
            focal_length_mm
            - 1
        )
    )

    beta_mod = (
        sensor_size_mm /
        object_size_at_mod
    )

    beta_target = (
        sensor_size_mm /
        object_size_mm
    )

    beta_difference = (
        beta_target -
        beta_mod
    )

    extension_ring_mm = (
        focal_length_mm *
        beta_difference
    )

    extension_ring_mm = round(
        extension_ring_mm,
        1
    )

    return ORingOutput(
        required_working_distance_mm=
            reported_working_distance_mm,

        extension_ring_required=True,

        extension_ring_mm=
            extension_ring_mm,

        valid=True,

        warning=None,
    )