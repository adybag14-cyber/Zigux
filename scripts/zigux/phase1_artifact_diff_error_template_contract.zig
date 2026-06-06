const std = @import("std");
const testing = std.testing;

const artifact_diff_source = @embedFile("artifact_diff.py");

fn expectContains(needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, artifact_diff_source, needle) != null);
}

fn expectBefore(first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, artifact_diff_source, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, artifact_diff_source, second) orelse return error.MissingSecondMarker;
    try testing.expect(first_index < second_index);
}

fn occurrenceCount(needle: []const u8) usize {
    var count: usize = 0;
    var rest: []const u8 = artifact_diff_source;
    while (std.mem.indexOf(u8, rest, needle)) |index| {
        count += 1;
        rest = rest[index + needle.len ..];
    }
    return count;
}

test "artifact diff keeps stable CLI error template constants" {
    try expectContains("MISSING_ARGUMENT_ERROR = (");
    try expectContains("artifact_diff.py: error: --mode, expected, and actual ");
    try expectContains("are required unless --self-test is set");
    try expectContains("INVALID_MODE_ERROR_TEMPLATE = (");
    try expectContains("artifact_diff.py: error: argument --mode: invalid ");
    try expectContains("choice: {value!r} (choose from text, json, bytes)");
    try expectContains("TOO_MANY_ARGUMENTS_ERROR = (");
    try expectContains("artifact_diff.py: error: expected exactly two positional ");
    try expectContains("arguments");

    try expectBefore("MISSING_ARGUMENT_ERROR = (", "INVALID_MODE_ERROR_TEMPLATE = (");
    try expectBefore("INVALID_MODE_ERROR_TEMPLATE = (", "TOO_MANY_ARGUMENTS_ERROR = (");
}

test "artifact diff routes parser failures through shared templates" {
    try testing.expectEqual(@as(usize, 2), occurrenceCount("print(MISSING_ARGUMENT_ERROR, file=sys.stderr)"));
    try testing.expectEqual(@as(usize, 1), occurrenceCount("print(INVALID_MODE_ERROR_TEMPLATE.format(value=mode), file=sys.stderr)"));
    try testing.expectEqual(@as(usize, 1), occurrenceCount("print(TOO_MANY_ARGUMENTS_ERROR, file=sys.stderr)"));

    try expectBefore("if mode in LEGACY_MODE_ALIASES:", "print(INVALID_MODE_ERROR_TEMPLATE.format(value=mode), file=sys.stderr)");
    try expectBefore("if len(positionals) > 2:", "print(TOO_MANY_ARGUMENTS_ERROR, file=sys.stderr)");
    try expectContains(
        "if mode is None or expected_text is None or actual_text is None:\n" ++
            "        print(MISSING_ARGUMENT_ERROR, file=sys.stderr)\n" ++
            "        return 2",
    );
}

test "artifact diff self-test covers every CLI error template boundary" {
    try expectContains("\"missing_mode_value_rejected\"");
    try expectContains("\"missing_positional_arguments_rejected\"");
    try expectContains("\"invalid_mode_rejected\"");
    try expectContains("\"extra_positional_rejected\"");

    try expectContains("\" \".join(missing_mode_value.stderr.split()) == MISSING_ARGUMENT_ERROR");
    try expectContains("\" \".join(missing_positionals.stderr.split()) == MISSING_ARGUMENT_ERROR");
    try expectContains("\" \".join(extra_positional.stderr.split()) == TOO_MANY_ARGUMENTS_ERROR");
    try expectContains("assert_case(invalid_mode.returncode == 2, \"invalid_mode_rejected\")");
}
