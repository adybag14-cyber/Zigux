const std = @import("std");

const source = @embedFile("artifact_diff.py");

fn expectContains(needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, source, needle) != null);
}

fn expectOrder(before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, source, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, source, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "artifact diff keeps one public missing-input diagnostic" {
    try expectContains("MISSING_ARGUMENT_ERROR = (");
    try expectContains("artifact_diff.py: error: --mode, expected, and actual ");
    try expectContains("are required unless --self-test is set");
    try expectContains("\" \".join(missing_mode_value.stderr.split()) == MISSING_ARGUMENT_ERROR");
    try expectContains("\" \".join(missing_positionals.stderr.split()) == MISSING_ARGUMENT_ERROR");
}

test "parser rejects missing mode value before positional fallback" {
    try expectContains("if arg == \"--mode\":");
    try expectContains("if index + 1 >= len(argv):");
    try expectContains("print(MISSING_ARGUMENT_ERROR, file=sys.stderr)\n                return 2");
    try expectContains("missing_mode_value = run_parser_probe([\"--mode\"])");
    try expectContains("covered.append(\"missing_mode_value_rejected\")");
    try expectOrder("if index + 1 >= len(argv):", "mode = argv[index + 1]");
}

test "main rejects missing expected or actual paths before comparison" {
    try expectContains("missing_positionals = run_parser_probe([\"--mode\", \"text\"])");
    try expectContains("covered.append(\"missing_positional_arguments_rejected\")");
    try expectContains("if mode is None or expected_text is None or actual_text is None:");
    try expectContains("print(MISSING_ARGUMENT_ERROR, file=sys.stderr)\n        return 2");
    try expectOrder("if mode is None or expected_text is None or actual_text is None:", "expected = Path(expected_text)");
    try expectOrder("if mode is None or expected_text is None or actual_text is None:", "result = compare(mode, expected, actual)");
}
