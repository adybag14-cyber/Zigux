const std = @import("std");

const artifact_diff_source = @embedFile("artifact_diff.py");

fn contains(text: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, text, needle) != null;
}

fn requireContains(text: []const u8, needle: []const u8) !void {
    try std.testing.expect(contains(text, needle));
}

fn requireBefore(text: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, text, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, text, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

fn countOccurrences(text: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOf(u8, text[offset..], needle)) |relative_index| {
        count += 1;
        offset += relative_index + needle.len;
    }
    return count;
}

fn isCurrentResultEnvelopeSource(text: []const u8) bool {
    return contains(text, "def emit_result(status: str, mode: str, expected: Path, actual: Path, extra_lines: list[str]) -> int:");
}

test "artifact diff result envelope prints stable header fields before extras" {
    if (!isCurrentResultEnvelopeSource(artifact_diff_source)) return error.SkipZigTest;

    try requireContains(artifact_diff_source, "print(f\"ARTIFACT_DIFF={status}\")");
    try requireContains(artifact_diff_source, "print(f\"MODE={mode}\")");
    try requireContains(artifact_diff_source, "print(f\"EXPECTED={expected}\")");
    try requireContains(artifact_diff_source, "print(f\"ACTUAL={actual}\")");
    try requireContains(artifact_diff_source, "for line in extra_lines:");
    try requireContains(artifact_diff_source, "print(line)");

    try requireBefore(artifact_diff_source, "print(f\"ARTIFACT_DIFF={status}\")", "print(f\"MODE={mode}\")");
    try requireBefore(artifact_diff_source, "print(f\"MODE={mode}\")", "print(f\"EXPECTED={expected}\")");
    try requireBefore(artifact_diff_source, "print(f\"EXPECTED={expected}\")", "print(f\"ACTUAL={actual}\")");
    try requireBefore(artifact_diff_source, "print(f\"ACTUAL={actual}\")", "for line in extra_lines:");
    try requireBefore(artifact_diff_source, "for line in extra_lines:", "print(line)");
}

test "artifact diff result envelope keeps status exit mapping centralized" {
    if (!isCurrentResultEnvelopeSource(artifact_diff_source)) return error.SkipZigTest;

    try requireContains(artifact_diff_source, "return 0 if status == \"pass\" else 1");
    try requireContains(artifact_diff_source, "return emit_result(\"pass\" if result.ok else \"fail\", mode, expected, actual, result.extra_lines)");
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(artifact_diff_source, "ARTIFACT_DIFF={status}"));
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(artifact_diff_source, "return 0 if status == \"pass\" else 1"));
}

test "artifact diff self-test catalog covers pass drift and diagnostic envelopes" {
    if (!isCurrentResultEnvelopeSource(artifact_diff_source)) return error.SkipZigTest;

    const required_cases = [_][]const u8{
        "\"text_pass\"",
        "\"text_mismatch\"",
        "\"json_pass\"",
        "\"json_mismatch\"",
        "\"json_invalid_expected\"",
        "\"json_invalid_actual\"",
        "\"json_invalid_both\"",
        "\"bytes_pass\"",
        "\"bytes_drift\"",
        "\"text_missing_expected\"",
        "\"json_missing_both\"",
        "\"bytes_missing_actual\"",
        "\"legacy_sha256_alias\"",
    };
    for (required_cases) |case_name| {
        try requireContains(artifact_diff_source, case_name);
    }

    try requireContains(artifact_diff_source, "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}");
    try requireContains(artifact_diff_source, "\"ARTIFACT_DIFF_SELF_TEST_CASES=\" + \",\".join(SELF_TEST_CASES)");
}
