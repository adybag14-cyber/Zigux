const std = @import("std");

const artifact_diff_path = "scripts/zigux/artifact_diff.py";

const required_mode_markers = [_][]const u8{
    "MODE_CHOICES = (\"text\", \"json\", \"bytes\")",
    "LEGACY_MODE_ALIASES = {\"sha256\": \"bytes\"}",
    "--mode {text,json,bytes}",
    "Compare two artifacts in a stable mode.",
    "ARTIFACT_DIFF={status}",
    "MODE={mode}",
    "EXPECTED={expected}",
    "ACTUAL={actual}",
    "SHA256={expected_digest}",
    "EXPECTED_SHA256={expected_digest}",
    "ACTUAL_SHA256={actual_digest}",
};

const required_self_test_cases = [_][]const u8{
    "text_pass",
    "text_mismatch",
    "json_pass",
    "json_mismatch",
    "json_invalid_expected",
    "json_invalid_actual",
    "json_invalid_both",
    "json_missing_expected",
    "json_missing_actual",
    "json_missing_both",
    "bytes_pass",
    "bytes_drift",
    "text_missing_expected",
    "text_missing_actual",
    "text_missing_both",
    "bytes_missing_expected",
    "bytes_missing_actual",
    "bytes_missing_both",
    "legacy_sha256_alias",
    "missing_mode_value_rejected",
    "missing_positional_arguments_rejected",
    "invalid_mode_rejected",
    "extra_positional_rejected",
};

const required_parser_markers = [_][]const u8{
    "MISSING_ARGUMENT_ERROR",
    "INVALID_MODE_ERROR_TEMPLATE",
    "TOO_MANY_ARGUMENTS_ERROR",
    "parse_args(argv: list[str])",
    "return 2",
    "if argv == [\"--help\"] or argv == [\"-h\"]:",
    "if self_test:",
    "return run_self_test()",
    "ARTIFACT_DIFF_SELF_TEST=pass",
    "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT=",
    "ARTIFACT_DIFF_SELF_TEST_CASES=",
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

fn readArtifactDiff(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        artifact_diff_path,
        allocator,
        .limited(1024 * 1024),
    );
}

test "phase1 artifact diff CLI keeps canonical modes and output fields" {
    const artifact_diff = try readArtifactDiff(std.testing.allocator);
    defer std.testing.allocator.free(artifact_diff);

    for (required_mode_markers) |marker| {
        try expectContains(artifact_diff, marker);
    }

    try expectOrdered(artifact_diff, "MODE_CHOICES", "LEGACY_MODE_ALIASES");
    try expectOrdered(artifact_diff, "def normalize_mode", "def compare(mode");
    try expectOrdered(artifact_diff, "ARTIFACT_DIFF={status}", "for line in extra_lines:");
}

test "phase1 artifact diff self-test catalog covers gate outcomes" {
    const artifact_diff = try readArtifactDiff(std.testing.allocator);
    defer std.testing.allocator.free(artifact_diff);

    try expectContains(artifact_diff, "SELF_TEST_CASES = [");
    for (required_self_test_cases) |case_name| {
        try expectContains(artifact_diff, case_name);
    }

    try expectOrdered(artifact_diff, "SELF_TEST_CASES = [", "def run_self_test() -> int:");
    try expectOrdered(artifact_diff, "covered.append(\"legacy_sha256_alias\")", "covered.append(\"missing_mode_value_rejected\")");
    try expectOrdered(artifact_diff, "covered.append(\"invalid_mode_rejected\")", "covered.append(\"extra_positional_rejected\")");
}

test "phase1 artifact diff parser keeps fail-closed CLI errors stable" {
    const artifact_diff = try readArtifactDiff(std.testing.allocator);
    defer std.testing.allocator.free(artifact_diff);

    for (required_parser_markers) |marker| {
        try expectContains(artifact_diff, marker);
    }

    try expectOrdered(artifact_diff, "def parse_args(argv: list[str])", "def main() -> int:");
    try expectOrdered(artifact_diff, "if len(positionals) > 2:", "print(TOO_MANY_ARGUMENTS_ERROR, file=sys.stderr)");
    try expectOrdered(artifact_diff, "if mode is None or expected_text is None or actual_text is None:", "print(MISSING_ARGUMENT_ERROR, file=sys.stderr)");
}
