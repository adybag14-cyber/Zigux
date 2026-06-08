const std = @import("std");

const artifact_diff_source = @embedFile("artifact_diff.py");

fn expectContains(needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, artifact_diff_source, needle) != null);
}

fn expectOrdered(before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, artifact_diff_source, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, artifact_diff_source, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "invalid mode diagnostic keeps public choice wording stable" {
    try expectContains(
        \\INVALID_MODE_ERROR_TEMPLATE = (
    );
    try expectContains(
        \\"usage: artifact_diff.py [-h] [--mode {{text,json,bytes}}] [--self-test] "
    );
    try expectContains(
        \\"[expected] [actual] artifact_diff.py: error: argument --mode: invalid "
    );
    try expectContains(
        \\"choice: {value!r} (choose from text, json, bytes)"
    );
}

test "parser rejects non-choice modes after legacy alias normalization" {
    try expectOrdered(
        \\if mode is not None and mode not in MODE_CHOICES:
    ,
        \\        if mode in LEGACY_MODE_ALIASES:
    );
    try expectOrdered(
        \\        if mode in LEGACY_MODE_ALIASES:
    ,
        \\        else:
    );
    try expectContains(
        \\        else:
        \\            print(INVALID_MODE_ERROR_TEMPLATE.format(value=mode), file=sys.stderr)
        \\            return 2
    );
}

test "self-test probes invalid mode rejection without overlapping other parser cases" {
    try expectOrdered(
        \\"missing_positional_arguments_rejected",
    ,
        \\"invalid_mode_rejected",
    );
    try expectOrdered(
        \\"invalid_mode_rejected",
    ,
        \\"extra_positional_rejected",
    );
    try expectContains(
        \\invalid_mode = run_parser_probe(["--mode", "yaml", str(expected), str(actual)])
    );
    try expectContains(
        \\assert_case(invalid_mode.returncode == 2, "invalid_mode_rejected")
    );
    try expectContains(
        \\covered.append("invalid_mode_rejected")
    );
}
