const std = @import("std");

const artifact_diff = @embedFile("artifact_diff.py");

fn has(needle: []const u8) bool {
    return std.mem.indexOf(u8, artifact_diff, needle) != null;
}

fn requireMarker(needle: []const u8) !void {
    try std.testing.expect(has(needle));
}

fn requireOrder(before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, artifact_diff, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, artifact_diff, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

fn count(needle: []const u8) usize {
    var total: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOf(u8, artifact_diff[offset..], needle)) |relative| {
        total += 1;
        offset += relative + needle.len;
    }
    return total;
}

fn skipIfLegacyArtifactDiff() !void {
    if (!has("def run_parser_probe(args: list[str]) -> subprocess.CompletedProcess[str]:")) {
        return error.SkipZigTest;
    }
}

test "parser probe re-enters the current helper with captured non-raising subprocesses" {
    try skipIfLegacyArtifactDiff();

    try requireMarker("import subprocess");
    try requireMarker("def run_parser_probe(args: list[str]) -> subprocess.CompletedProcess[str]:");
    try requireMarker("[sys.executable, __file__, *args]");
    try requireMarker("check=False,");
    try requireMarker("capture_output=True,");
    try requireMarker("text=True,");
    try requireOrder("def run_parser_probe(args: list[str]) -> subprocess.CompletedProcess[str]:", "def run_self_test() -> int:");
}

test "self-test parser cases all route through run_parser_probe" {
    try skipIfLegacyArtifactDiff();

    const expected_calls = [_][]const u8{
        "legacy_alias = run_parser_probe([\"--mode\", \"sha256\", str(blob_a), str(blob_a)])",
        "missing_mode_value = run_parser_probe([\"--mode\"])",
        "missing_positionals = run_parser_probe([\"--mode\", \"text\"])",
        "invalid_mode = run_parser_probe([\"--mode\", \"yaml\", str(expected), str(actual)])",
        "extra_positional = run_parser_probe(",
    };
    for (expected_calls) |marker| {
        try requireMarker(marker);
    }

    try std.testing.expect(count("run_parser_probe(") == 6);
    try requireOrder("legacy_alias = run_parser_probe", "covered.append(\"legacy_sha256_alias\")");
    try requireOrder("missing_mode_value = run_parser_probe", "covered.append(\"missing_mode_value_rejected\")");
    try requireOrder("missing_positionals = run_parser_probe", "covered.append(\"missing_positional_arguments_rejected\")");
    try requireOrder("invalid_mode = run_parser_probe", "covered.append(\"invalid_mode_rejected\")");
    try requireOrder("extra_positional = run_parser_probe", "covered.append(\"extra_positional_rejected\")");
}

test "parser probe keeps CLI diagnostics coupled to captured stderr and stdout" {
    try skipIfLegacyArtifactDiff();

    try requireMarker("assert_case(legacy_alias.returncode == 0, \"legacy_sha256_alias\")");
    try requireMarker("assert_case(\"ARTIFACT_DIFF=pass\" in legacy_alias.stdout, \"legacy_sha256_alias\")");
    try requireMarker("assert_case(\"MODE=bytes\" in legacy_alias.stdout, \"legacy_sha256_alias\")");
    try requireMarker("\" \".join(missing_mode_value.stderr.split()) == MISSING_ARGUMENT_ERROR");
    try requireMarker("\" \".join(missing_positionals.stderr.split()) == MISSING_ARGUMENT_ERROR");
    try requireMarker("\" \".join(extra_positional.stderr.split()) == TOO_MANY_ARGUMENTS_ERROR");
    try requireMarker("assert_case(invalid_mode.returncode == 2, \"invalid_mode_rejected\")");
}
