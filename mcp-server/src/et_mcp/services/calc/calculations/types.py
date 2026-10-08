from typing import Annotated

from pydantic import BaseModel, Field


# Advanced FOV
class AdvancedFOVInput(BaseModel):
    width_pixels: Annotated[
        int,
        Field(
            gt=0,
            description="Sensor image width in pixels."
        ),
    ]

    height_pixels: Annotated[
        int,
        Field(
            gt=0,
            description="Sensor image height in pixels."
        ),
    ]

    pixel_size_um: Annotated[
        float,
        Field(
            gt=0,
            description="Physical size of a single pixel on the sensor in micrometers (µm)."
        ),
    ]

    focal_length_mm: Annotated[
        float,
        Field(
            gt=0,
            description="Lens focal length in millimeters."
        ),
    ]

    working_distance_mm: Annotated[
        float,
        Field(
            gt=0,
            description="Distance from the lens to the target object in millimeters."
        ),
    ]


class AdvancedFOVOutput(BaseModel):
    sensor_width_mm: Annotated[
        float,
        Field(
            description="Calculated physical sensor width in millimeters."
        ),
    ]

    sensor_height_mm: Annotated[
        float,
        Field(
            description="Calculated physical sensor height in millimeters."
        ),
    ]

    sensor_diagonal_mm: Annotated[
        float,
        Field(
            description="Calculated physical sensor diagonal length in millimeters."
        ),
    ]

    sensor_diagonal_pixels: Annotated[
        int,
        Field(
            description="Sensor diagonal length measured in pixels."
        ),
    ]

    aspect_ratio_decimal: Annotated[
        float,
        Field(
            description="Aspect ratio expressed as width divided by height."
        ),
    ]

    aspect_ratio_fraction: Annotated[
        str,
        Field(
            description="Aspect ratio expressed as a simplified ratio such as '16:9' or '4:3'."
        ),
    ]

    fov_x_mm: Annotated[
        float,
        Field(
            description="Horizontal field of view at the specified working distance in millimeters."
        ),
    ]

    fov_y_mm: Annotated[
        float,
        Field(
            description="Vertical field of view at the specified working distance in millimeters."
        ),
    ]

    fov_diagonal_mm: Annotated[
        float,
        Field(
            description="Diagonal field of view at the specified working distance in millimeters."
        ),
    ]

    valid: Annotated[
        bool,
        Field(
            description="Whether the calculation produced a physically valid result."
        ),
    ]

    warning: Annotated[
        str | None,
        Field(
            description="Optional warning message describing assumptions, limitations, or unusual input conditions."
        ),
    ] = None


class AdvancedFOVCalculatorError(ValueError):
    """Raised when field-of-view calculations cannot be completed."""

# Advanced WD
class AdvancedWorkingDistanceInput(BaseModel):
    width_pixels: Annotated[
        int,
        Field(gt=0, description="Sensor image width in pixels."),
    ]

    height_pixels: Annotated[
        int,
        Field(gt=0, description="Sensor image height in pixels."),
    ]

    pixel_size_um: Annotated[
        float,
        Field(
            gt=0,
            description="Physical size of a single sensor pixel in micrometers (µm).",
        ),
    ]

    focal_length_mm: Annotated[
        float,
        Field(
            gt=0,
            description="Lens focal length in millimeters.",
        ),
    ]

    fov_x_mm: Annotated[
        float,
        Field(
            gt=0,
            description="Desired horizontal field of view in millimeters.",
        ),
    ]


class AdvancedWorkingDistanceOutput(BaseModel):
    working_distance_mm: Annotated[
        float,
        Field(
            description="Calculated working distance required to achieve the specified horizontal field of view.",
        ),
    ]

    sensor_width_mm: Annotated[
        float,
        Field(
            description="Calculated physical sensor width in millimeters.",
        ),
    ]

    sensor_height_mm: Annotated[
        float,
        Field(
            description="Calculated physical sensor height in millimeters.",
        ),
    ]

    sensor_diagonal_mm: Annotated[
        float,
        Field(
            description="Calculated physical sensor diagonal length in millimeters.",
        ),
    ]

    sensor_diagonal_pixels: Annotated[
        int,
        Field(
            description="Sensor diagonal length measured in pixels.",
        ),
    ]

    aspect_ratio_decimal: Annotated[
        float,
        Field(
            description="Aspect ratio expressed as width divided by height.",
        ),
    ]

    aspect_ratio_fraction: Annotated[
        str,
        Field(
            description="Aspect ratio expressed as a simplified ratio such as '16:9' or '4:3'.",
        ),
    ]

    fov_x_mm: Annotated[
        float,
        Field(
            description="Horizontal field of view in millimeters.",
        ),
    ]

    fov_y_mm: Annotated[
        float,
        Field(
            description="Vertical field of view in millimeters, derived from the sensor aspect ratio.",
        ),
    ]

    fov_diagonal_mm: Annotated[
        float,
        Field(
            description="Diagonal field of view in millimeters.",
        ),
    ]

    valid: Annotated[
        bool,
        Field(
            description="Whether the calculation produced a physically valid result.",
        ),
    ]

    warning: Annotated[
        str | None,
        Field(
            description="Optional warning message describing assumptions, limitations, or unusual input conditions.",
        ),
    ] = None


class AdvancedWorkingDistanceCalculatorError(ValueError):
    pass

# DOF

class DepthOfFieldInput(BaseModel):
    working_distance_mm: Annotated[
        float,
        Field(
            gt=0,
            description="Distance from the lens to the subject in millimeters.",
        ),
    ]

    pixel_size_um: Annotated[
        float,
        Field(
            gt=0,
            description="Physical size of a single sensor pixel in micrometers (µm).",
        ),
    ]

    focal_length_mm: Annotated[
        float,
        Field(
            gt=0,
            description="Lens focal length in millimeters.",
        ),
    ]

    f_number: Annotated[
        float,
        Field(
            gt=0,
            description="Lens f-number (f-stop), such as 2.8, 4, 8, or 16.",
        ),
    ]


class DepthOfFieldOutput(BaseModel):
    magnification: Annotated[
        float,
        Field(
            description="Calculated optical magnification at the specified working distance.",
        ),
    ]

    aperture_nominal: Annotated[
        float,
        Field(
            description="Nominal lens aperture (f-number) provided as input.",
        ),
    ]

    aperture_effective: Annotated[
        float,
        Field(
            description="Effective aperture accounting for magnification effects.",
        ),
    ]

    hyperfocal_distance_mm: Annotated[
        float,
        Field(
            description="Calculated hyperfocal distance in millimeters.",
        ),
    ]

    dof_near_mm: Annotated[
        float,
        Field(
            description="Nearest distance from the lens that remains acceptably in focus.",
        ),
    ]

    dof_far_mm: Annotated[
        float | None,
        Field(
            description="Farthest distance from the lens that remains acceptably in focus. May be null when the far limit is effectively infinite.",
        ),
    ]

    total_dof_mm: Annotated[
        float | None,
        Field(
            description="Total depth of field in millimeters. May be null when the far limit is infinite.",
        ),
    ]

    valid: Annotated[
        bool,
        Field(
            description="Whether the calculation produced a physically valid result.",
        ),
    ]

    warning: Annotated[
        str | None,
        Field(
            description="Optional warning message describing assumptions, limitations, or unusual input conditions.",
        ),
    ] = None


class DepthOfFieldCalculatorError(ValueError):
    pass

# ET

class ExposureTimeInput(BaseModel):
    object_length_mm: Annotated[
        float,
        Field(
            gt=0,
            description="Physical length of the object along the camera field of view in millimeters.",
        ),
    ]

    conveyor_speed_mm_s: Annotated[
        float,
        Field(
            gt=0,
            description="Speed of the moving object or conveyor in millimeters per second.",
        ),
    ]

    sensor_pixels: Annotated[
        int,
        Field(
            gt=0,
            description="Number of sensor pixels spanning the measured object dimension.",
        ),
    ]

    allowed_blur_pixels: Annotated[
        float,
        Field(
            gt=0,
            description="Maximum acceptable motion blur expressed in pixels.",
        ),
    ]


class ExposureTimeOutput(BaseModel):
    exposure_time_ms: Annotated[
        float,
        Field(
            description="Maximum allowable camera exposure time in milliseconds to keep motion blur within the specified limit.",
        ),
    ]

    valid: Annotated[
        bool,
        Field(
            description="Whether the calculation produced a physically valid result.",
        ),
    ]

    warning: Annotated[
        str | None,
        Field(
            description="Optional warning message describing assumptions, limitations, or unusual input conditions.",
        ),
    ] = None


class ExposureTimeCalculatorError(ValueError):
    pass

# FOV

class FOVInput(BaseModel):
    sensor_size_mm: Annotated[
        float,
        Field(
            gt=0,
            description="Physical size of the sensor dimension being evaluated (width, height, or diagonal) in millimeters.",
        ),
    ]

    working_distance_mm: Annotated[
        float,
        Field(
            gt=0,
            description="Distance from the lens to the target object in millimeters.",
        ),
    ]

    focal_length_mm: Annotated[
        float,
        Field(
            gt=0,
            description="Lens focal length in millimeters.",
        ),
    ]


class FOVOutput(BaseModel):
    fov_mm: Annotated[
        float,
        Field(
            description="Calculated field of view corresponding to the provided sensor dimension at the specified working distance, in millimeters.",
        ),
    ]

    valid: Annotated[
        bool,
        Field(
            description="Whether the calculation produced a physically valid result.",
        ),
    ]

    warning: Annotated[
        str | None,
        Field(
            description="Optional warning message describing assumptions, limitations, or unusual input conditions.",
        ),
    ] = None


class FOVCalculatorError(ValueError):
    pass

# FL
class FocalLengthInput(BaseModel):
    object_size_mm: Annotated[
        float,
        Field(
            gt=0,
            description="Physical size of the object or field of view dimension to be captured, in millimeters.",
        ),
    ]

    working_distance_mm: Annotated[
        float,
        Field(
            gt=0,
            description="Distance from the lens to the target object in millimeters.",
        ),
    ]

    sensor_size_mm: Annotated[
        float,
        Field(
            gt=0,
            description="Physical sensor dimension being used for the calculation (width, height, or diagonal), in millimeters.",
        ),
    ]


class FocalLengthOutput(BaseModel):
    focal_length_mm: Annotated[
        float,
        Field(
            description="Calculated focal length required to achieve the specified field of view and working distance.",
        ),
    ]

    valid: Annotated[
        bool,
        Field(
            description="Whether the calculation produced a physically valid result.",
        ),
    ]

    warning: Annotated[
        str | None,
        Field(
            description="Optional warning message describing assumptions, limitations, or unusual input conditions.",
        ),
    ] = None


class FocalLengthCalculatorError(ValueError):
    pass

# LSF

class LineScanInput(BaseModel):
    object_width_mm: Annotated[
        float,
        Field(
            gt=0,
            description="Width of the object or inspection area to be captured in millimeters.",
        ),
    ]

    pixels_per_mm: Annotated[
        float,
        Field(
            gt=0,
            description="Required imaging resolution expressed as pixels per millimeter.",
        ),
    ]

    bytes_per_pixel: Annotated[
        float,
        Field(
            gt=0,
            description="Image data size generated per pixel, typically 1 for 8-bit grayscale, 2 for 16-bit grayscale, or 3 for RGB.",
        ),
    ]

    conveyor_speed_mm_s: Annotated[
        float,
        Field(
            gt=0,
            description="Speed of the moving object or conveyor in millimeters per second.",
        ),
    ]


class LineScanOutput(BaseModel):
    required_pixels: Annotated[
        int,
        Field(
            description="Minimum number of sensor pixels required across the object width to achieve the requested resolution.",
        ),
    ]

    recommended_camera: Annotated[
        str,
        Field(
            description="Recommended standard line-scan camera resolution that meets or exceeds the required pixel count.",
        ),
    ]

    sensor_pixels: Annotated[
        int,
        Field(
            description="Pixel count of the recommended line-scan camera sensor.",
        ),
    ]

    line_frequency_khz: Annotated[
        float,
        Field(
            description="Required line acquisition frequency in kilohertz to maintain the specified spatial resolution at the given conveyor speed.",
        ),
    ]

    exposure_time_ms: Annotated[
        float,
        Field(
            description="Maximum available exposure time per line in milliseconds.",
        ),
    ]

    exposure_time_us: Annotated[
        float,
        Field(
            description="Maximum available exposure time per line in microseconds.",
        ),
    ]

    data_rate_mpix_s: Annotated[
        float,
        Field(
            description="Estimated image data throughput in megapixels per second.",
        ),
    ]

    data_rate_mb_s: Annotated[
        float,
        Field(
            description="Estimated raw image data throughput in megabytes per second.",
        ),
    ]

    valid: Annotated[
        bool,
        Field(
            description="Whether a single standard line-scan camera can meet the requirement."
        ),
    ] = True

    warning: Annotated[
        str | None,
        Field(
            description="Optional warning describing multi-camera setups or implausible inputs."
        ),
    ] = None


class LineScanCalculatorError(ValueError):
    pass

# MA

class MeasurementAccuracyInput(BaseModel):
    object_size_mm: Annotated[
        float,
        Field(
            gt=0,
            description="Physical size of the object or field of view dimension being measured, in millimeters.",
        ),
    ]

    sensor_pixels: Annotated[
        int,
        Field(
            gt=0,
            description="Number of sensor pixels spanning the specified object size.",
        ),
    ]

    nyquist_factor: Annotated[
        float,
        Field(
            gt=0,
            description="Sampling factor used to satisfy the Nyquist criterion. Common values are 2 or greater.",
        ),
    ]

    subpixel_factor: Annotated[
        float,
        Field(
            gt=0,
            description="Expected subpixel measurement capability, expressed as the fraction of a pixel that can be resolved.",
        ),
    ]


class MeasurementAccuracyOutput(BaseModel):
    pixels_per_mm: Annotated[
        float,
        Field(
            description="Image resolution expressed as pixels per millimeter.",
        ),
    ]

    mm_per_pixel: Annotated[
        float,
        Field(
            description="Physical size represented by a single pixel, in millimeters per pixel.",
        ),
    ]

    nyquist_pixels_per_mm: Annotated[
        float,
        Field(
            description="Effective pixels per millimeter after applying the Nyquist sampling factor.",
        ),
    ]

    nyquist_mm_per_pixel: Annotated[
        float,
        Field(
            description="Effective millimeters per pixel after applying the Nyquist sampling factor.",
        ),
    ]

    measurement_accuracy_mm: Annotated[
        float,
        Field(
            description="Estimated measurement accuracy in millimeters after accounting for subpixel precision.",
        ),
    ]

    valid: Annotated[
        bool,
        Field(
            description="Whether the calculation produced a physically valid result.",
        ),
    ]

    warning: Annotated[
        str | None,
        Field(
            description="Optional warning message describing assumptions, limitations, or unusual input conditions.",
        ),
    ] = None


class MeasurementAccuracyCalculatorError(ValueError):
    pass

# OR

class ORingInput(BaseModel):
    object_size_mm: Annotated[
        float,
        Field(
            gt=0,
            description="Physical size of the object or feature that must fit within the camera field of view, in millimeters.",
        ),
    ]

    minimum_object_distance_mm: Annotated[
        float,
        Field(
            gt=0,
            description="Minimum allowable distance between the lens and the object, in millimeters.",
        ),
    ]

    sensor_size_mm: Annotated[
        float,
        Field(
            gt=0,
            description="Physical sensor dimension being used for the calculation (width, height, or diagonal), in millimeters.",
        ),
    ]

    focal_length_mm: Annotated[
        float,
        Field(
            gt=0,
            description="Lens focal length in millimeters.",
        ),
    ]


class ORingOutput(BaseModel):
    required_working_distance_mm: Annotated[
        float,
        Field(
            description="Working distance required to achieve the desired field of view for the specified object size.",
        ),
    ]

    extension_ring_required: Annotated[
        bool,
        Field(
            description="Indicates whether an extension ring is required to achieve the requested imaging geometry.",
        ),
    ]

    extension_ring_mm: Annotated[
        float,
        Field(
            description="Estimated extension ring length required, in millimeters. Zero if no extension ring is needed.",
        ),
    ]

    valid: Annotated[
        bool,
        Field(
            description="Whether the calculation produced a physically valid result.",
        ),
    ]

    warning: Annotated[
        str | None,
        Field(
            description="Optional warning message describing assumptions, limitations, or unusual input conditions.",
        ),
    ] = None


class ORingCalculatorError(ValueError):
    pass

# SG

class SensorGeometryInput(BaseModel):
    width_pixels: Annotated[
        int,
        Field(
            gt=0,
            description="Sensor image width in pixels.",
        ),
    ]

    height_pixels: Annotated[
        int,
        Field(
            gt=0,
            description="Sensor image height in pixels.",
        ),
    ]

    pixel_size_um: Annotated[
        float,
        Field(
            gt=0,
            description="Physical size of a single sensor pixel in micrometers (µm).",
        ),
    ]


class SensorGeometryOutput(BaseModel):
    width_mm: Annotated[
        float,
        Field(
            description="Calculated physical sensor width in millimeters.",
        ),
    ]

    height_mm: Annotated[
        float,
        Field(
            description="Calculated physical sensor height in millimeters.",
        ),
    ]

    diagonal_mm: Annotated[
        float,
        Field(
            description="Calculated physical sensor diagonal length in millimeters.",
        ),
    ]

    width_pixels: Annotated[
        int,
        Field(
            description="Sensor width in pixels.",
        ),
    ]

    height_pixels: Annotated[
        int,
        Field(
            description="Sensor height in pixels.",
        ),
    ]

    diagonal_pixels: Annotated[
        float,
        Field(
            description="Sensor diagonal length measured in pixels.",
        ),
    ]

    aspect_ratio_decimal: Annotated[
        float,
        Field(
            description="Aspect ratio expressed as width divided by height.",
        ),
    ]

    aspect_ratio_fraction: Annotated[
        str,
        Field(
            description="Aspect ratio expressed as a simplified ratio such as '16:9' or '4:3'.",
        ),
    ]

    valid: Annotated[
        bool,
        Field(
            description="Whether the calculation produced a physically valid result.",
        ),
    ]

    warning: Annotated[
        str | None,
        Field(
            description="Optional warning message describing assumptions, limitations, or unusual input conditions.",
        ),
    ] = None


class SensorCalculatorError(ValueError):
    pass

# WD

class WorkingDistanceInput(BaseModel):
    object_size_mm: Annotated[
        float,
        Field(
            gt=0,
            description="Physical size of the object or field of view dimension to be captured, in millimeters.",
        ),
    ]

    sensor_size_mm: Annotated[
        float,
        Field(
            gt=0,
            description="Physical sensor dimension being used for the calculation (width, height, or diagonal), in millimeters.",
        ),
    ]

    focal_length_mm: Annotated[
        float,
        Field(
            gt=0,
            description="Lens focal length in millimeters.",
        ),
    ]


class WorkingDistanceOutput(BaseModel):
    working_distance_mm: Annotated[
        float,
        Field(
            description="Calculated working distance required to image the specified object size with the given sensor dimension and focal length.",
        ),
    ]

    valid: Annotated[
        bool,
        Field(
            description="Whether the calculation produced a physically valid result.",
        ),
    ]

    warning: Annotated[
        str | None,
        Field(
            description="Optional warning message describing assumptions, limitations, or unusual input conditions.",
        ),
    ] = None


class WorkingDistanceCalculatorError(ValueError):
    pass