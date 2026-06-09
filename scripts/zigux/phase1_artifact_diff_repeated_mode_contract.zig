const std = @import("std");

const artifact_diff_source = @embedFile("artifact_diff.py");

fn expectContains(needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, artifact_diff_source, needle) != null);
}

fn expectMissing(needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, artifact_diff_source, needle) == null);
}

fn expectOrdered(before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, artifact_diff_source, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, artifact_diff_source, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "parser keeps repeated mode options as a last-value-wins boundary" {
    try expectOrdered(
        \\    mode: str | None = None
    ,
        \\        if arg == "--mode":
    );
    try expectContains(
        \\        if arg == "--mode":
        \\            if index + 1 >= len(argv):
        \\                print(MISSING_ARGUMENT_ERROR, file=sys.stderr)
        \\                return 2
        \\            mode = argv[index + 1]
        \\            index += 2
        \\            continue
    );
    try expectMissing(
        \\mode is not None and arg == "--mode"
    );
}

test "mode validation and legacy alias normalization use the final parsed value" {
    try expectOrdered(
        \\            mode = argv[index + 1]
    ,
        \\    if mode is not None and mode not in MODE_CHOICES:
    );
    try expectContains(
        \\    if mode is not None and mode not in MODE_CHOICES:
        \\        if mode in LEGACY_MODE_ALIASES:
        \\            mode = LEGACY_MODE_ALIASES[mode]
        \\        else:
        \\            print(INVALID_MODE_ERROR_TEMPLATE.format(value=mode), file=sys.stderr)
        \\            return 2
    );
    try expectOrdered(
        \\    if mode is not None and mode not in MODE_CHOICES:
    ,
        \\    return self_test, mode, expected, actual
    );
}

test "main compares and emits the final parser mode without recomputing it" {
    try expectContains(
        \\    self_test, mode, expected_text, actual_text = parsed
    );
    try expectOrdered(
        \\    self_test, mode, expected_text, actual_text = parsed
    ,
        \\    result = compare(mode, expected, actual)
    );
    try expectOrdered(
        \\    result = compare(mode, expected, actual)
    ,
        \\    return emit_result("pass" if result.ok else "fail", mode, expected, actual, result.extra_lines)
    );
}
