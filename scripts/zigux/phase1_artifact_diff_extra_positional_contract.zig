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

test "extra positional diagnostic keeps public argparse-compatible wording" {
    try expectContains(
        \\TOO_MANY_ARGUMENTS_ERROR = (
    );
    try expectContains(
        \\\"usage: artifact_diff.py [-h] [--mode {text,json,bytes}] [--self-test] "
    );
    try expectContains(
        \\\"[expected] [actual] artifact_diff.py: error: expected exactly two positional "
    );
    try expectContains(
        \\\"arguments"
    );
}

test "parser rejects more than two positionals before returning parsed paths" {
    try expectOrdered(
        \\expected = positionals[0] if len(positionals) >= 1 else None
    ,
        \\if len(positionals) > 2:
    );
    try expectOrdered(
        \\actual = positionals[1] if len(positionals) >= 2 else None
    ,
        \\if len(positionals) > 2:
    );
    try expectContains(
        \\if len(positionals) > 2:
        \\        print(TOO_MANY_ARGUMENTS_ERROR, file=sys.stderr)
        \\        return 2
    );
}

test "self-test probes the extra positional rejection route" {
    try expectContains(
        \\\"extra_positional_rejected",
    );
    try expectContains(
        \\extra_positional = run_parser_probe(
    );
    try expectContains(
        \\["--mode", "text", str(expected), str(actual), str(missing)]
    );
    try expectContains(
        \\)
    );
    try expectContains(
        \\assert_case(extra_positional.returncode == 2, "extra_positional_rejected")
    );
    try expectContains(
        \\\" ".join(extra_positional.stderr.split()) == TOO_MANY_ARGUMENTS_ERROR,
    );
    try expectContains(
        \\covered.append("extra_positional_rejected")
    );
}
