const std = @import("std");

const source = @embedFile("artifact_diff.py");

fn requireContains(needle: []const u8) !void {
    try std.testing.expect(std.mem.containsAtLeast(u8, source, 1, needle));
}

fn requireOrdered(before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, source, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, source, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

fn hasLiveArtifactDiffParser() bool {
    return std.mem.containsAtLeast(u8, source, 1, "def parse_args(argv: list[str])") and
        std.mem.containsAtLeast(u8, source, 1, "def main() -> int:") and
        std.mem.containsAtLeast(u8, source, 1, "ARTIFACT_DIFF_SELF_TEST=pass");
}

test "artifact diff self-test flag is parsed independently of positionals" {
    if (!hasLiveArtifactDiffParser()) return error.SkipZigTest;

    try requireContains(
        \\def parse_args(argv: list[str]) -> tuple[bool, str | None, str | None, str | None] | int:
    );
    try requireContains(
        \\        if arg == "--self-test":
        \\            self_test = True
        \\            index += 1
        \\            continue
    );
    try requireContains(
        \\        positionals.append(arg)
        \\        index += 1
    );
    try requireOrdered(
        \\        if arg == "--self-test":
    ,
        \\        positionals.append(arg)
    );
    try requireContains(
        \\    return self_test, mode, expected, actual
    );
}

test "artifact diff main dispatches self-test before required input failures" {
    if (!hasLiveArtifactDiffParser()) return error.SkipZigTest;

    try requireContains(
        \\    self_test, mode, expected_text, actual_text = parsed
        \\    if self_test:
        \\        return run_self_test()
        \\
        \\    if mode is None or expected_text is None or actual_text is None:
        \\        print(MISSING_ARGUMENT_ERROR, file=sys.stderr)
        \\        return 2
    );
    try requireOrdered(
        \\    if self_test:
        \\        return run_self_test()
    ,
        \\    if mode is None or expected_text is None or actual_text is None:
    );
}

test "artifact diff self-test catalog includes parser misuse precedence cases" {
    if (!hasLiveArtifactDiffParser()) return error.SkipZigTest;

    try requireContains(
        \\    "missing_mode_value_rejected",
        \\    "missing_positional_arguments_rejected",
        \\    "invalid_mode_rejected",
        \\    "extra_positional_rejected",
    );
    try requireContains(
        \\    missing_mode_value = run_parser_probe(["--mode"])
    );
    try requireContains(
        \\    missing_positionals = run_parser_probe(["--mode", "text"])
    );
    try requireContains(
        \\    extra_positional = run_parser_probe(
        \\        ["--mode", "text", str(expected), str(actual), str(missing)]
        \\    )
    );
    try requireContains(
        \\    assert_case(covered == SELF_TEST_CASES, "self_test_case_order")
    );
}
