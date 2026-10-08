from typing import Type
from pydantic import BaseModel

from .types import (
    AdvancedFOVInput,
    AdvancedFOVOutput,
    AdvancedWorkingDistanceInput,
    AdvancedWorkingDistanceOutput,
    DepthOfFieldInput,
    DepthOfFieldOutput,
    ExposureTimeInput,
    ExposureTimeOutput,
    FOVInput,
    FOVOutput,
    FocalLengthInput,
    FocalLengthOutput,
    LineScanInput,
    LineScanOutput,
    MeasurementAccuracyInput,
    MeasurementAccuracyOutput,
    ORingInput,
    ORingOutput,
    SensorGeometryInput,
    SensorGeometryOutput,
    WorkingDistanceInput,
    WorkingDistanceOutput,
)


class FormulaMetadata(BaseModel):
    description: str
    when_to_use: str
    example_questions: list[str]
    input_model: Type[BaseModel]
    output_model: Type[BaseModel]


FORMULA_REGISTRY: dict[str, FormulaMetadata] = {
    "fov_using_pixel_size": FormulaMetadata(
        description="Calculates complete sensor geometry and horizontal, vertical, and diagonal field of view.",
        when_to_use="Use when sensor resolution, pixel size, focal length, and working distance are known and you need the resulting field of view.",
        example_questions=[
            "What field of view will I get with a 12 mm lens?",
            "How much area can my camera see at 500 mm working distance?",
            "What are the horizontal and vertical FOV dimensions for my sensor?",
        ],
        input_model=AdvancedFOVInput,
        output_model=AdvancedFOVOutput,
    ),

    "working_distance_using_pixel_size": FormulaMetadata(
        description="Calculates the working distance required to achieve a desired field of view using full sensor geometry.",
        when_to_use="Use when sensor resolution, pixel size, focal length, and desired field of view are known but working distance is unknown.",
        example_questions=[
            "How far should my camera be to capture 300 mm width?",
            "What working distance is required for a 500 mm field of view?",
            "How far back should I mount the camera?",
        ],
        input_model=AdvancedWorkingDistanceInput,
        output_model=AdvancedWorkingDistanceOutput,
    ),

    "depth_of_field": FormulaMetadata(
        description="Calculates magnification, hyperfocal distance, near focus limit, far focus limit, and total depth of field.",
        when_to_use="Use when determining acceptable focus range for a given lens, aperture, pixel size, and working distance.",
        example_questions=[
            "What depth of field do I get at f/8?",
            "Will my object remain fully in focus?",
            "What are the near and far focus limits?",
        ],
        input_model=DepthOfFieldInput,
        output_model=DepthOfFieldOutput,
    ),

    "exposure_time": FormulaMetadata(
        description="Calculates the maximum exposure time allowed to stay within a motion blur limit.",
        when_to_use="Use when imaging moving objects and motion blur must be limited.",
        example_questions=[
            "How fast can my exposure be before motion blur exceeds 1 pixel?",
            "What exposure time is safe for a conveyor moving at 1000 mm/s?",
            "How much exposure can I use without blur?",
        ],
        input_model=ExposureTimeInput,
        output_model=ExposureTimeOutput,
    ),

    "fov_using_sensor_size": FormulaMetadata(
        description="Calculates field of view from sensor size, focal length, and working distance.",
        when_to_use="Use when only a single sensor dimension is relevant and a simple FOV calculation is needed.",
        example_questions=[
            "What field of view will I get with this lens?",
            "How much width will the camera see?",
            "What is the FOV at this distance?",
        ],
        input_model=FOVInput,
        output_model=FOVOutput,
    ),

    "focal_length": FormulaMetadata(
        description="Calculates required focal length for a desired field of view.",
        when_to_use="Use when object size and working distance are known but lens focal length must be selected.",
        example_questions=[
            "What focal length lens do I need?",
            "Which lens should I choose for this application?",
            "How much focal length is required to see a 400 mm object?",
        ],
        input_model=FocalLengthInput,
        output_model=FocalLengthOutput,
    ),

    "line_scan": FormulaMetadata(
        description="Calculates line scan camera resolution, line rate, exposure time, and data throughput requirements.",
        when_to_use="Use for line-scan camera sizing and conveyor inspection applications.",
        example_questions=[
            "How many pixels does my line scan camera need?",
            "What line rate is required for this conveyor speed?",
            "Can my acquisition system handle the required throughput?",
        ],
        input_model=LineScanInput,
        output_model=LineScanOutput,
    ),

    "measurement_accuracy": FormulaMetadata(
        description="Estimates achievable measurement accuracy based on resolution, Nyquist sampling, and subpixel precision.",
        when_to_use="Use when determining whether a vision system can measure a feature accurately enough.",
        example_questions=[
            "Can I measure a 0.05 mm feature accurately?",
            "What measurement accuracy can I achieve?",
            "How many pixels per millimeter do I need?",
        ],
        input_model=MeasurementAccuracyInput,
        output_model=MeasurementAccuracyOutput,
    ),

    "o_ring": FormulaMetadata(
        description="Determines whether an extension ring is required and estimates the required extension length.",
        when_to_use="Use when evaluating close-focus imaging setups and extension ring requirements.",
        example_questions=[
            "Do I need an extension ring?",
            "How much extension is required for this setup?",
            "Can this lens focus close enough?",
        ],
        input_model=ORingInput,
        output_model=ORingOutput,
    ),

    "sensor_geometry": FormulaMetadata(
        description="Calculates physical sensor dimensions, diagonal size, and aspect ratio from pixel dimensions and pixel size.",
        when_to_use="Use when sensor geometry must be derived from resolution and pixel pitch.",
        example_questions=[
            "What is the physical size of my sensor?",
            "What is the sensor diagonal?",
            "What aspect ratio does my sensor have?",
        ],
        input_model=SensorGeometryInput,
        output_model=SensorGeometryOutput,
    ),

    "working_distance_using_sensor_size": FormulaMetadata(
        description="Calculates working distance from object size, sensor size, and focal length.",
        when_to_use="Use when object size, sensor size, and lens focal length are known but camera distance is unknown.",
        example_questions=[
            "How far should the camera be from the object?",
            "What working distance is required?",
            "Where should I mount the camera?",
        ],
        input_model=WorkingDistanceInput,
        output_model=WorkingDistanceOutput,
    ),
}