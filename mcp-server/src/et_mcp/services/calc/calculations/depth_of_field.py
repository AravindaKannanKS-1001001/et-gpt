from .types import DepthOfFieldInput, DepthOfFieldOutput, DepthOfFieldCalculatorError

def calculate_depth_of_field(
    inputs: DepthOfFieldInput,
) -> DepthOfFieldOutput:
    """
    Port of depth-of-field.html
    """

    working_distance_mm = (
        inputs.working_distance_mm
    )

    pixel_size_um = (
        inputs.pixel_size_um
    )

    focal_length_mm = (
        inputs.focal_length_mm
    )

    f_number = (
        inputs.f_number
    )

    # ----------------------------------
    # Original JS Rule
    #
    # AMin = 2 * focal length
    # ----------------------------------

    minimum_distance = (
        focal_length_mm * 2
    )

    if working_distance_mm < minimum_distance:
        return DepthOfFieldOutput(
            magnification=0,
            aperture_nominal=f_number,
            aperture_effective=0,
            hyperfocal_distance_mm=0,
            dof_near_mm=0,
            dof_far_mm=None,
            total_dof_mm=None,
            valid=False,
            warning=(
                "Working distance must be "
                "at least 2× focal length."
            ),
        )

    # ----------------------------------
    # Layer 3
    # Magnification
    # ----------------------------------

    magnification = (
        focal_length_mm /
        (
            working_distance_mm -
            focal_length_mm
        )
    )

    # ----------------------------------
    # Effective Aperture
    # ----------------------------------

    aperture_effective = (
        f_number *
        (
            1 +
            magnification
        )
    )

    # ----------------------------------
    # Circle of Confusion
    #
    # JS uses pixel size
    # directly as acceptable blur.
    # ----------------------------------

    coc_mm = (
        pixel_size_um / 1000
    )

    # ----------------------------------
    # Hyperfocal Distance
    # ----------------------------------

    hyperfocal_mm = (
        (
            focal_length_mm ** 2
        )
        /
        (
            aperture_effective *
            coc_mm
        )
    )

    hyperfocal_mm += (
        focal_length_mm
    )

    # ----------------------------------
    # Near Limit
    # ----------------------------------

    dof_near_mm = (
        hyperfocal_mm *
        working_distance_mm
    ) / (
        hyperfocal_mm +
        (
            working_distance_mm -
            focal_length_mm
        )
    )

    # ----------------------------------
    # Far Limit
    # ----------------------------------

    denominator = (
        hyperfocal_mm -
        (
            working_distance_mm -
            focal_length_mm
        )
    )

    if denominator <= 0:
        dof_far_mm = None
        total_dof_mm = None

    else:
        dof_far_mm = (
            hyperfocal_mm *
            working_distance_mm
        ) / denominator

        total_dof_mm = (
            dof_far_mm -
            dof_near_mm
        )

    # ----------------------------------
    # Layer 4
    # Business Rules
    # ----------------------------------

    magnification = round(
        magnification,
        4
    )

    aperture_effective = round(
        aperture_effective,
        2
    )

    hyperfocal_mm = round(
        hyperfocal_mm,
        2
    )

    dof_near_mm = round(
        dof_near_mm,
        2
    )

    if dof_far_mm is not None:
        dof_far_mm = round(
            dof_far_mm,
            2
        )

    if total_dof_mm is not None:
        total_dof_mm = round(
            total_dof_mm,
            2
        )

    return DepthOfFieldOutput(
        magnification=magnification,

        aperture_nominal=f_number,
        aperture_effective=
            aperture_effective,

        hyperfocal_distance_mm=
            hyperfocal_mm,

        dof_near_mm=dof_near_mm,
        dof_far_mm=dof_far_mm,

        total_dof_mm=total_dof_mm,

        valid=True,
        warning=None,
    )