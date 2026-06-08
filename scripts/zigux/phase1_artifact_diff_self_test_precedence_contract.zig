const std = @import("std");

const artifact_diff_source = @embedFile("artifact_diff.py");

fn requireMarker(needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, artifact_diff_source, needle) != null);
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

test "self-test flag bypasses required mode and path arguments in main" {
    try requireMarker("def main() -> int:");
    try requireMarker("parsed = parse_args(sys.argv[1:])");
    try requireMarker("self_test, mode, expected_text, actual_text = parsed");
    try requireMarker("if self_test:");
    try requireMarker("return run_self_test()");
    try requireMarker("if mode is None or expected_text is None or actual_text is None:");
    try requireMarker("print(MISSING_ARGUMENT_ERROR, file=sys.stderr)");
    try requireMarker("return 2");

    try requireOrder("self_test, mode, expected_text, actual_text = parsed", "if self_test:");
    try requireOrder("if self_test:", "return run_self_test()");
    try requireOrder("return run_self_test()", "if mode is None or expected_text is None or actual_text is None:");
    try requireOrder("if mode is None or expected_text is None or actual_text is None:", "print(MISSING_ARGUMENT_ERROR, file=sys.stderr)");
}

test "argument parser keeps self-test independent from normal comparison mode" {
    try requireMarker("def parse_args(argv: list[str]) -> tuple[bool, str | None, str | None, str | None] | int:");
    try requireMarker("self_test = False");
    try requireMarker("mode: str | None = None");
    try requireMarker("positionals: list[str] = []");
    try requireMarker("if arg == \"--self-test\":");
    try requireMarker("self_test = True");
    try requireMarker("if arg == \"--mode\":");
    try requireMarker("if mode is not None and mode not in MODE_CHOICES:");
    try requireMarker("expected = positionals[0] if len(positionals) >= 1 else None");
    try requireMarker("actual = positionals[1] if len(positionals) >= 2 else None");
    try requireMarker("return self_test, mode, expected, actual");

    try requireOrder("if arg == \"--self-test\":", "if arg == \"--mode\":");
    try requireOrder("self_test = True", "positionals.append(arg)");
    try requireOrder("if mode is not None and mode not in MODE_CHOICES:", "expected = positionals[0] if len(positionals) >= 1 else None");
    try requireOrder("if len(positionals) > 2:", "return self_test, mode, expected, actual");
}

test "self-test catalog records parser-precedence cases in stable order" {
    try requireMarker("SELF_TEST_CASES = [");
    try requireMarker("\"legacy_sha256_alias\"");
    try requireMarker("\"missing_mode_value_rejected\"");
    try requireMarker("\"missing_positional_arguments_rejected\"");
    try requireMarker("\"invalid_mode_rejected\"");
    try requireMarker("\"extra_positional_rejected\"");
    try requireMarker("assert_case(covered == SELF_TEST_CASES, \"self_test_case_order\")");
    try requireMarker("print(\"ARTIFACT_DIFF_SELF_TEST=pass\")");
    try requireMarker("print(f\"ARTIFACT_DIFF_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}\")");
    try requireMarker("print(\"ARTIFACT_DIFF_SELF_TEST_CASES=\" + \",\".join(SELF_TEST_CASES))");

    try requireOrder("\"legacy_sha256_alias\"", "\"missing_mode_value_rejected\"");
    try requireOrder("\"missing_mode_value_rejected\"", "\"missing_positional_arguments_rejected\"");
    try requireOrder("\"missing_positional_arguments_rejected\"", "\"invalid_mode_rejected\"");
    try requireOrder("\"invalid_mode_rejected\"", "\"extra_positional_rejected\"");
    try requireOrder("assert_case(covered == SELF_TEST_CASES, \"self_test_case_order\")", "print(\"ARTIFACT_DIFF_SELF_TEST=pass\")");
    try requireCount("print(\"ARTIFACT_DIFF_SELF_TEST=pass\")", 1);
}
