const std = @import("std");

const artifact_diff_source = @embedFile("artifact_diff.py");

fn has(needle: []const u8) bool {
    return std.mem.indexOf(u8, artifact_diff_source, needle) != null;
}

fn requireMarker(needle: []const u8) !void {
    try std.testing.expect(has(needle));
}

fn requireOrder(before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, artifact_diff_source, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, artifact_diff_source, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

fn requireCount(needle: []const u8, expected: usize) !void {
    var index: usize = 0;
    var count: usize = 0;
    while (std.mem.indexOfPos(u8, artifact_diff_source, index, needle)) |found| {
        count += 1;
        index = found + needle.len;
    }
    try std.testing.expectEqual(expected, count);
}

test "parser probe invokes this helper as a captured subprocess" {
    try requireMarker("def run_parser_probe(args: list[str]) -> subprocess.CompletedProcess[str]:");
    try requireMarker("return subprocess.run(");
    try requireMarker("[sys.executable, __file__, *args]");
    try requireMarker("check=False");
    try requireMarker("capture_output=True");
    try requireMarker("text=True");

    try requireOrder("def run_parser_probe(args: list[str]) -> subprocess.CompletedProcess[str]:", "return subprocess.run(");
    try requireOrder("return subprocess.run(", "[sys.executable, __file__, *args]");
    try requireOrder("[sys.executable, __file__, *args]", "capture_output=True");
    try requireOrder("capture_output=True", "text=True");
}

test "self-test routes parser-only cases through parser probe" {
    try requireMarker("legacy_alias = run_parser_probe([\"--mode\", \"sha256\", str(blob_a), str(blob_a)])");
    try requireMarker("missing_mode_value = run_parser_probe([\"--mode\"])");
    try requireMarker("missing_positionals = run_parser_probe([\"--mode\", \"text\"])");
    try requireMarker("invalid_mode = run_parser_probe([\"--mode\", \"yaml\", str(expected), str(actual)])");
    try requireMarker("extra_positional = run_parser_probe(");
    try requireMarker("[\"--mode\", \"text\", str(expected), str(actual), str(missing)]");

    try requireOrder("legacy_alias = run_parser_probe", "missing_mode_value = run_parser_probe");
    try requireOrder("missing_mode_value = run_parser_probe", "missing_positionals = run_parser_probe");
    try requireOrder("missing_positionals = run_parser_probe", "invalid_mode = run_parser_probe");
    try requireOrder("invalid_mode = run_parser_probe", "extra_positional = run_parser_probe");
}

test "parser probe assertions inspect stdout stderr and exit status" {
    try requireMarker("assert_case(legacy_alias.returncode == 0, \"legacy_sha256_alias\")");
    try requireMarker("assert_case(\"ARTIFACT_DIFF=pass\" in legacy_alias.stdout, \"legacy_sha256_alias\")");
    try requireMarker("assert_case(\"MODE=bytes\" in legacy_alias.stdout, \"legacy_sha256_alias\")");
    try requireMarker("assert_case(missing_mode_value.returncode == 2, \"missing_mode_value_rejected\")");
    try requireMarker("\" \".join(missing_mode_value.stderr.split()) == MISSING_ARGUMENT_ERROR");
    try requireMarker("assert_case(missing_positionals.returncode == 2, \"missing_positional_arguments_rejected\")");
    try requireMarker("\" \".join(missing_positionals.stderr.split()) == MISSING_ARGUMENT_ERROR");
    try requireMarker("assert_case(invalid_mode.returncode == 2, \"invalid_mode_rejected\")");
    try requireMarker("assert_case(extra_positional.returncode == 2, \"extra_positional_rejected\")");
    try requireMarker("\" \".join(extra_positional.stderr.split()) == TOO_MANY_ARGUMENTS_ERROR");

    try requireCount("run_parser_probe(", 6);
    try requireOrder("legacy_alias.returncode == 0", "legacy_alias.stdout");
    try requireOrder("missing_mode_value.returncode == 2", "missing_mode_value.stderr");
    try requireOrder("missing_positionals.returncode == 2", "missing_positionals.stderr");
    try requireOrder("extra_positional.returncode == 2", "extra_positional.stderr");
}
