const std = @import("std");

const artifact_diff_source = @embedFile("artifact_diff.py");

fn has(needle: []const u8) bool {
    return std.mem.indexOf(u8, artifact_diff_source, needle) != null;
}

fn requireLiveArtifactDiff() !void {
    if (!has("MODE_CHOICES = (\"text\", \"json\", \"bytes\")")) {
        return error.SkipZigTest;
    }
    if (!has("format_utf8_error")) {
        return error.SkipZigTest;
    }
}

test "artifact diff JSON UTF-8 diagnostics keep side-specific stable markers" {
    try requireLiveArtifactDiff();

    try std.testing.expect(has("def format_utf8_error(path: Path, *, side: str, exc: UnicodeDecodeError) -> str:"));
    try std.testing.expect(has("return f\"{side}_UTF8_ERROR={path}:{exc.start}: {exc.reason}\""));
    try std.testing.expect(has("except UnicodeDecodeError as exc:"));
    try std.testing.expect(has("return None, format_utf8_error(path, side=side, exc=exc)"));

    const expected_marker = "EXPECTED_UTF8_ERROR={invalid_expected_utf8_json}:0: invalid start byte";
    const actual_marker = "ACTUAL_UTF8_ERROR={invalid_actual_utf8_json}:0: invalid start byte";
    try std.testing.expect(has(expected_marker));
    try std.testing.expect(has(actual_marker));
}

test "artifact diff JSON UTF-8 probes run before actual-side JSON parsing" {
    try requireLiveArtifactDiff();

    const expected_utf8 = std.mem.indexOf(u8, artifact_diff_source, "invalid_expected_utf8_json.write_bytes(b\"\\xff{\\n\")").?;
    const actual_utf8 = std.mem.indexOf(u8, artifact_diff_source, "invalid_actual_utf8_json.write_bytes(b\"\\xff{\\n\")").?;
    const expected_probe = std.mem.indexOf(u8, artifact_diff_source, "compare(\"json\", invalid_expected_utf8_json, actual_json)").?;
    const actual_probe = std.mem.indexOf(u8, artifact_diff_source, "compare(\"json\", expected_json, invalid_actual_utf8_json)").?;
    const both_probe = std.mem.indexOf(u8, artifact_diff_source, "compare(\"json\", invalid_expected_utf8_json, invalid_actual_utf8_json)").?;

    try std.testing.expect(expected_utf8 < expected_probe);
    try std.testing.expect(actual_utf8 < actual_probe);
    try std.testing.expect(expected_probe < actual_probe);
    try std.testing.expect(actual_probe < both_probe);
    try std.testing.expect(has("compare(\"json\", invalid_expected_utf8_json, invalid_actual_utf8_json).extra_lines"));
    try std.testing.expect(has("== [f\"EXPECTED_UTF8_ERROR={invalid_expected_utf8_json}:0: invalid start byte\"]"));
}

test "artifact diff self-test catalog keeps UTF-8 covered inside JSON invalid cases" {
    try requireLiveArtifactDiff();

    const cases_start = std.mem.indexOf(u8, artifact_diff_source, "SELF_TEST_CASES = [").?;
    const json_expected = std.mem.indexOfPos(u8, artifact_diff_source, cases_start, "\"json_invalid_expected\"").?;
    const json_actual = std.mem.indexOfPos(u8, artifact_diff_source, cases_start, "\"json_invalid_actual\"").?;
    const json_both = std.mem.indexOfPos(u8, artifact_diff_source, cases_start, "\"json_invalid_both\"").?;
    const missing_expected = std.mem.indexOfPos(u8, artifact_diff_source, cases_start, "\"json_missing_expected\"").?;

    try std.testing.expect(json_expected < json_actual);
    try std.testing.expect(json_actual < json_both);
    try std.testing.expect(json_both < missing_expected);

    const append_expected = std.mem.indexOf(u8, artifact_diff_source, "covered.append(\"json_invalid_expected\")").?;
    const append_actual = std.mem.indexOf(u8, artifact_diff_source, "covered.append(\"json_invalid_actual\")").?;
    const append_both = std.mem.indexOf(u8, artifact_diff_source, "covered.append(\"json_invalid_both\")").?;
    const self_test_order = std.mem.indexOf(u8, artifact_diff_source, "assert_case(covered == SELF_TEST_CASES, \"self_test_case_order\")").?;

    try std.testing.expect(append_expected < append_actual);
    try std.testing.expect(append_actual < append_both);
    try std.testing.expect(append_both < self_test_order);
}
