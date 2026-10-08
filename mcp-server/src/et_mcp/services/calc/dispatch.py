"""
Dispatch: map formula_id → (input_model, calculation_function).
Supports both 'line_scan' and 'line_scan_frequency' as aliases.
"""

from .calculations.types import (
    AdvancedFOVInput,
    AdvancedWorkingDistanceInput,
    DepthOfFieldInput,
    ExposureTimeInput,
    FOVInput,
    FocalLengthInput,
    LineScanInput,
    MeasurementAccuracyInput,
    ORingInput,
    SensorGeometryInput,
    WorkingDistanceInput,
)
from .calculations.fov_using_pixel_size import calculate_advanced_fov
from .calculations.fov_using_sensor_size import calculate_fov
from .calculations.working_distance_using_pixel_size import calculate_advanced_working_distance
from .calculations.working_distance_using_sensor_size import calculate_working_distance
from .calculations.depth_of_field import calculate_depth_of_field
from .calculations.exposure_time import calculate_exposure_time
from .calculations.focal_length import calculate_focal_length
from .calculations.line_scan_frequency import calculate_line_scan
from .calculations.measurement_accuracy import calculate_measurement_accuracy
from .calculations.o_ring import calculate_o_ring
from .calculations.sensor_geometry import calculate_sensor_geometry


DISPATCH: dict = {
    "fov_using_pixel_size":               (AdvancedFOVInput,               calculate_advanced_fov),
    "fov_using_sensor_size":              (FOVInput,                        calculate_fov),
    "working_distance_using_pixel_size":  (AdvancedWorkingDistanceInput,    calculate_advanced_working_distance),
    "working_distance_using_sensor_size": (WorkingDistanceInput,            calculate_working_distance),
    "depth_of_field":                     (DepthOfFieldInput,               calculate_depth_of_field),
    "exposure_time":                      (ExposureTimeInput,               calculate_exposure_time),
    "focal_length":                       (FocalLengthInput,                calculate_focal_length),
    "line_scan":                          (LineScanInput,                   calculate_line_scan),
    "line_scan_frequency":                (LineScanInput,                   calculate_line_scan),
    "measurement_accuracy":               (MeasurementAccuracyInput,        calculate_measurement_accuracy),
    "o_ring":                             (ORingInput,                      calculate_o_ring),
    "sensor_geometry":                    (SensorGeometryInput,             calculate_sensor_geometry),
}

_AVAILABLE = sorted(set(DISPATCH.keys()))


def run_calculation(formula_id: str, args: dict) -> dict:
    if formula_id not in DISPATCH:
        raise ValueError(
            f"Unknown formula_id {formula_id!r}. Available: {_AVAILABLE}"
        )
    input_model, fn = DISPATCH[formula_id]
    result = fn(input_model(**args))
    return result.model_dump()


def get_inputs(formula_id: str) -> dict:
    if formula_id not in DISPATCH:
        raise ValueError(
            f"Unknown formula_id {formula_id!r}. Available: {_AVAILABLE}"
        )
    input_model, _ = DISPATCH[formula_id]
    schema = input_model.model_json_schema()
    required = schema.get("required", [])
    all_fields = list(schema.get("properties", {}).keys())
    optional = [f for f in all_fields if f not in required]
    return {"required": required, "optional": optional}


def validate(formula_id: str, args: dict) -> dict:
    if formula_id not in DISPATCH:
        raise ValueError(
            f"Unknown formula_id {formula_id!r}. Available: {_AVAILABLE}"
        )
    inputs_meta = get_inputs(formula_id)
    missing = [f for f in inputs_meta["required"] if f not in args]
    return {"valid": len(missing) == 0, "missing": missing}
