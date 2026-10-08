"""Calculator and reference-table behaviour (no network, no DB)."""
from et_mcp.tools import calc


def test_focal_length():
    out = calc.calculate("focal_length", {"object_size_mm": 300, "working_distance_mm": 500, "sensor_size_mm": 8.8})
    assert out["valid"] is True and out["focal_length_mm"] == 14.2


def test_fov_using_sensor_size_matches_chatbot_fixture():
    out = calc.calculate("fov_using_sensor_size", {"sensor_size_mm": 8.8, "working_distance_mm": 500, "focal_length_mm": 12})
    assert out["fov_mm"] == 357.87


def test_invalid_and_unknown_inputs_return_errors():
    assert "error" in calc.calculate("focal_length", {"object_size_mm": 0, "working_distance_mm": 500, "sensor_size_mm": 8.8})
    assert "error" in calc.calculate("nope", {})


def test_impossible_config_names_values_and_points_to_solver():
    out = calc.calculate("fov_using_sensor_size", {"sensor_size_mm": 7, "working_distance_mm": 100, "focal_length_mm": 100})
    assert out["valid"] is False and "100" in out["warning"] and "focal_length" in out["warning"]


def test_line_scan_rounds_pixels_up_and_keeps_small_rates():
    out = calc.calculate("line_scan_frequency", {"object_width_mm": 100.4, "pixels_per_mm": 1, "bytes_per_pixel": 1, "conveyor_speed_mm_s": 1})
    assert out["required_pixels"] == 101
    assert out["line_frequency_khz"] == 0.001 and out["data_rate_mpix_s"] > 0
    assert out["valid"] is True and out["warning"] is None


def test_line_scan_multi_camera_is_flagged():
    out = calc.calculate("line_scan_frequency", {"object_width_mm": 2000, "pixels_per_mm": 10, "bytes_per_pixel": 1, "conveyor_speed_mm_s": 100})
    assert out["valid"] is False and "stitched" in out["warning"]


def test_line_scan_alias_has_a_definition():
    assert calc.get_calculator("line_scan")["id"] == "line_scan_frequency"


def test_measurement_accuracy_warns_below_nyquist():
    out = calc.calculate("measurement_accuracy", {"object_size_mm": 10, "sensor_pixels": 2048, "nyquist_factor": 0.5, "subpixel_factor": 1})
    assert out["warning"] and "below 2" in out["warning"]


def test_portrait_sensor_is_valid_with_warning():
    out = calc.calculate("working_distance_using_pixel_size", {"width_pixels": 2048, "height_pixels": 2448, "pixel_size_um": 3.45, "focal_length_mm": 16, "fov_x_mm": 100})
    assert out.get("valid") is True and "portrait" in (out.get("warning") or ""), out


def test_sensor_format_lookup_has_real_dimensions_and_tolerant_keys():
    for key in ("2/3", '2/3"', "2/3 inch", "2/3-in"):
        value = calc.lookup("sensor_format_sizes", key)["value"]
        assert value == {"diagonal_mm": 11.0, "width_mm": 8.8, "height_mm": 6.6}
    assert calc.lookup("sensor_format_sizes", "1 inch")["value"]["diagonal_mm"] == 16.0
    assert calc.lookup("sensor_format_sizes", "full frame")["value"]["diagonal_mm"] == 43.3
    assert "error" in calc.lookup("sensor_format_sizes", "5/7")
