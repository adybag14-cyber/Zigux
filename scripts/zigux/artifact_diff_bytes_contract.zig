const std = @import("std");

const artifact_diff_source = @embedFile("artifact_diff.py");

fn expectContains(needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, artifact_diff_source, needle) != null);
}

fn expectOrder(before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, artifact_diff_source, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, artifact_diff_source, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

fn sourceHasAny(markers: []const []const u8) bool {
    for (markers) |marker| {
        if (std.mem.indexOf(u8, artifact_diff_source, marker) != null) return true;
    }
    return false;
}

test "artifact diff exposes bytes digest mode and legacy sha256 compatibility" {
    const has_current_bytes_mode = sourceHasAny(&.{
        "MODE_CHOICES = (\"text\", \"json\", \"bytes\")",
        "\" --mode {text,json,bytes}\"",
    });
    const has_legacy_sha256_mode = sourceHasAny(&.{
        "choices=['text', 'json', 'sha256']",
        "compare_artifacts('sha256'",
    });
    try std.testing.expect(has_current_bytes_mode or has_legacy_sha256_mode);

    if (has_current_bytes_mode) {
        try expectContains("LEGACY_MODE_ALIASES = {\"sha256\": \"bytes\"}");
        try expectContains("def normalize_mode(mode: str) -> str:");
        try expectContains("return LEGACY_MODE_ALIASES.get(mode, mode)");
        try expectContains("MODE=bytes");
        try expectOrder("if mode in LEGACY_MODE_ALIASES:", "mode = LEGACY_MODE_ALIASES[mode]");
    }
}

test "artifact diff byte comparison emits stable digest markers" {
    try expectContains("hashlib.sha256");
    try expectContains("SHA256=");
    try expectContains("EXPECTED_SHA256=");
    try expectContains("ACTUAL_SHA256=");
    try expectOrder("EXPECTED_SHA256=", "ACTUAL_SHA256=");

    const has_current_compare = sourceHasAny(&.{
        "def compare_bytes(expected: Path, actual: Path) -> ComparisonResult:",
        "if mode == \"bytes\":\n        return compare_bytes(expected, actual)",
    });
    const has_legacy_compare = sourceHasAny(&.{
        "elif mode == 'sha256':",
        "details['expected_sha256'] = expected_value",
    });
    try std.testing.expect(has_current_compare or has_legacy_compare);
}

test "artifact diff self-test catalog covers pass drift and missing byte cases" {
    const pass_markers = [_][]const u8{ "\"bytes_pass\"", "'sha256_pass'" };
    const drift_markers = [_][]const u8{ "\"bytes_drift\"", "'sha256_drift'" };
    const missing_expected_markers = [_][]const u8{ "\"bytes_missing_expected\"", "'sha256_missing_expected'" };
    const missing_actual_markers = [_][]const u8{ "\"bytes_missing_actual\"", "'sha256_missing_actual'" };
    const missing_both_markers = [_][]const u8{ "\"bytes_missing_both\"", "'sha256_missing_both'" };

    try std.testing.expect(sourceHasAny(&pass_markers));
    try std.testing.expect(sourceHasAny(&drift_markers));
    try std.testing.expect(sourceHasAny(&missing_expected_markers));
    try std.testing.expect(sourceHasAny(&missing_actual_markers));
    try std.testing.expect(sourceHasAny(&missing_both_markers));

    try expectContains("zigux-artifact-diff");
    try expectContains("zigux-artifact-DRIFT");
    try expectContains("ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=");
}
