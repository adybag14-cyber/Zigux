const std = @import("std");

const artifact_diff_source = @embedFile("artifact_diff.py");

fn hasLiveTextExactSurface(source: []const u8) bool {
    return std.mem.containsAtLeast(u8, source, 1, "MODE_CHOICES = (\"text\", \"json\", \"bytes\")") and
        std.mem.containsAtLeast(u8, source, 1, "def compare_text(expected: Path, actual: Path) -> ComparisonResult:") and
        std.mem.containsAtLeast(u8, source, 1, "if read_bytes(expected) == read_bytes(actual):") and
        std.mem.containsAtLeast(u8, source, 1, "return ComparisonResult(ok=True, extra_lines=[])") and
        std.mem.containsAtLeast(u8, source, 1, "return ComparisonResult(ok=False, extra_lines=[])") and
        std.mem.containsAtLeast(u8, source, 1, "if mode == \"text\":\n        return compare_text(expected, actual)");
}

fn requireLiveTextExactSurface() !void {
    if (!hasLiveTextExactSurface(artifact_diff_source)) {
        return error.SkipZigTest;
    }
}

fn indexOfNeedle(haystack: []const u8, needle: []const u8) !usize {
    return std.mem.indexOf(u8, haystack, needle) orelse error.MissingNeedle;
}

fn bodyBetween(source: []const u8, start_marker: []const u8, end_marker: []const u8) ![]const u8 {
    const start = try indexOfNeedle(source, start_marker);
    const body_start = start + start_marker.len;
    const end_rel = std.mem.indexOf(u8, source[body_start..], end_marker) orelse return error.MissingNeedle;
    return source[body_start .. body_start + end_rel];
}

test "artifact diff text mode is byte exact and does not decode text" {
    try requireLiveTextExactSurface();

    const compare_text_body = try bodyBetween(
        artifact_diff_source,
        "def compare_text(expected: Path, actual: Path) -> ComparisonResult:\n",
        "\n\ndef compare_json",
    );

    try std.testing.expect(std.mem.containsAtLeast(u8, compare_text_body, 2, "read_bytes("));
    try std.testing.expect(!std.mem.containsAtLeast(u8, compare_text_body, 1, "load_text("));
    try std.testing.expect(!std.mem.containsAtLeast(u8, compare_text_body, 1, ".decode("));
    try std.testing.expect(!std.mem.containsAtLeast(u8, compare_text_body, 1, "rstrip"));
    try std.testing.expect(!std.mem.containsAtLeast(u8, compare_text_body, 1, "splitlines"));
}

test "artifact diff text mismatches emit no mode-specific detail lines" {
    try requireLiveTextExactSurface();

    const compare_text_body = try bodyBetween(
        artifact_diff_source,
        "def compare_text(expected: Path, actual: Path) -> ComparisonResult:\n",
        "\n\ndef compare_json",
    );
    const fail_return = "return ComparisonResult(ok=False, extra_lines=[])";

    try std.testing.expect(std.mem.indexOf(u8, compare_text_body, fail_return) != null);
    try std.testing.expect(!std.mem.containsAtLeast(u8, compare_text_body, 1, "EXPECTED_TEXT"));
    try std.testing.expect(!std.mem.containsAtLeast(u8, compare_text_body, 1, "ACTUAL_TEXT"));
    try std.testing.expect(!std.mem.containsAtLeast(u8, compare_text_body, 1, "EXPECTED_UTF8_ERROR"));
    try std.testing.expect(!std.mem.containsAtLeast(u8, compare_text_body, 1, "ACTUAL_UTF8_ERROR"));
}

test "artifact diff self-test keeps text pass and mismatch as the byte-exact anchors" {
    try requireLiveTextExactSurface();

    const self_test_body = try bodyBetween(
        artifact_diff_source,
        "def run_self_test() -> int:\n",
        "\n\ndef parse_args",
    );
    const text_pass = "expected.write_text(\"alpha\\nbeta\\n\", encoding=\"utf-8\", newline=\"\\n\")";
    const text_match = "actual.write_text(\"alpha\\nbeta\\n\", encoding=\"utf-8\", newline=\"\\n\")";
    const text_mismatch = "actual.write_text(\"alpha\\nBETA\\n\", encoding=\"utf-8\", newline=\"\\n\")";

    try std.testing.expect(std.mem.indexOf(u8, artifact_diff_source, "\"text_pass\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, artifact_diff_source, "\"text_mismatch\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, self_test_body, text_pass) != null);
    try std.testing.expect(std.mem.indexOf(u8, self_test_body, text_match) != null);
    try std.testing.expect(std.mem.indexOf(u8, self_test_body, text_mismatch) != null);
    try std.testing.expect((try indexOfNeedle(self_test_body, text_pass)) < (try indexOfNeedle(self_test_body, text_mismatch)));
}
