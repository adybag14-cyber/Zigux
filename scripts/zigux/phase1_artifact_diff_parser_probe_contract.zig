const std = @import("std");

const artifact_diff_source = @embedFile("artifact_diff.py");

fn hasLiveParserProbeSurface(source: []const u8) bool {
    return std.mem.containsAtLeast(u8, source, 1, "def run_parser_probe(args: list[str]) -> subprocess.CompletedProcess[str]:") and
        std.mem.containsAtLeast(u8, source, 1, "[sys.executable, __file__, *args]") and
        std.mem.containsAtLeast(u8, source, 1, "capture_output=True") and
        std.mem.containsAtLeast(u8, source, 1, "missing_mode_value = run_parser_probe([\"--mode\"])") and
        std.mem.containsAtLeast(u8, source, 1, "legacy_alias = run_parser_probe([\"--mode\", \"sha256\", str(blob_a), str(blob_a)])");
}

fn requireLiveParserProbeSurface() !void {
    if (!hasLiveParserProbeSurface(artifact_diff_source)) {
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

test "parser probe re-enters the current script through python" {
    try requireLiveParserProbeSurface();

    const probe_body = try bodyBetween(
        artifact_diff_source,
        "def run_parser_probe(args: list[str]) -> subprocess.CompletedProcess[str]:\n",
        "\n\ndef assert_case",
    );

    try std.testing.expect(std.mem.indexOf(u8, probe_body, "return subprocess.run(\n") != null);
    try std.testing.expect(std.mem.indexOf(u8, probe_body, "        [sys.executable, __file__, *args],\n") != null);
    try std.testing.expect((try indexOfNeedle(probe_body, "[sys.executable, __file__, *args]")) < (try indexOfNeedle(probe_body, "check=False")));
    try std.testing.expect((try indexOfNeedle(probe_body, "check=False")) < (try indexOfNeedle(probe_body, "capture_output=True")));
    try std.testing.expect((try indexOfNeedle(probe_body, "capture_output=True")) < (try indexOfNeedle(probe_body, "text=True")));
}

test "parser probes intentionally keep failing invocations observable" {
    try requireLiveParserProbeSurface();

    const probe_body = try bodyBetween(
        artifact_diff_source,
        "def run_parser_probe(args: list[str]) -> subprocess.CompletedProcess[str]:\n",
        "\n\ndef assert_case",
    );

    try std.testing.expect(std.mem.indexOf(u8, probe_body, "check=False") != null);
    try std.testing.expect(std.mem.indexOf(u8, probe_body, "capture_output=True") != null);
    try std.testing.expect(std.mem.indexOf(u8, probe_body, "text=True") != null);
    try std.testing.expect(std.mem.indexOf(u8, probe_body, "check=True") == null);
    try std.testing.expect(std.mem.indexOf(u8, probe_body, "stdout=subprocess.PIPE") == null);
    try std.testing.expect(std.mem.indexOf(u8, probe_body, "stderr=subprocess.PIPE") == null);
}

test "self-test parser probes cover alias and parser failures" {
    try requireLiveParserProbeSurface();

    const self_test_body = try bodyBetween(
        artifact_diff_source,
        "def run_self_test() -> int:\n",
        "\n\ndef parse_args",
    );

    try std.testing.expect(std.mem.indexOf(u8, self_test_body, "legacy_alias = run_parser_probe([\"--mode\", \"sha256\", str(blob_a), str(blob_a)])") != null);
    try std.testing.expect(std.mem.indexOf(u8, self_test_body, "assert_case(legacy_alias.returncode == 0, \"legacy_sha256_alias\")") != null);
    try std.testing.expect(std.mem.indexOf(u8, self_test_body, "missing_mode_value = run_parser_probe([\"--mode\"])") != null);
    try std.testing.expect(std.mem.indexOf(u8, self_test_body, "missing_positionals = run_parser_probe([\"--mode\", \"text\"])") != null);
    try std.testing.expect(std.mem.indexOf(u8, self_test_body, "invalid_mode = run_parser_probe([\"--mode\", \"yaml\", str(expected), str(actual)])") != null);
    try std.testing.expect(std.mem.indexOf(u8, self_test_body, "extra_positional = run_parser_probe(") != null);
    try std.testing.expect((try indexOfNeedle(self_test_body, "legacy_alias = run_parser_probe")) < (try indexOfNeedle(self_test_body, "missing_mode_value = run_parser_probe")));
    try std.testing.expect((try indexOfNeedle(self_test_body, "missing_mode_value = run_parser_probe")) < (try indexOfNeedle(self_test_body, "extra_positional = run_parser_probe")));
}
