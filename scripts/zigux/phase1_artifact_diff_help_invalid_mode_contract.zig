const std = @import("std");

const source = @embedFile("artifact_diff.py");

fn has(needle: []const u8) bool {
    return std.mem.indexOf(u8, source, needle) != null;
}

fn indexOf(needle: []const u8) !usize {
    return std.mem.indexOf(u8, source, needle) orelse error.MissingMarker;
}

fn count(needle: []const u8) usize {
    return std.mem.count(u8, source, needle);
}

fn requireCurrentArtifactDiff() !void {
    if (!has("MODE_CHOICES = (\"text\", \"json\", \"bytes\")") or
        !has("HELP_LINES = [") or
        !has("INVALID_MODE_ERROR_TEMPLATE = ("))
    {
        return error.SkipZigTest;
    }
}

test "artifact diff help surface advertises only current public modes" {
    try requireCurrentArtifactDiff();

    try std.testing.expectEqual(@as(usize, 1), count("HELP_LINES = ["));
    try std.testing.expect(has("usage: artifact_diff.py [-h] [--mode {text,json,bytes}] [--self-test]"));
    try std.testing.expect(has(" [expected] [actual]"));
    try std.testing.expect(has("Compare two artifacts in a stable mode."));
    try std.testing.expect(has(" --mode {text,json,bytes}"));
    try std.testing.expect(has(" --self-test Run built-in deterministic comparison checks."));
    try std.testing.expect(has("MODE_CHOICES = (\"text\", \"json\", \"bytes\")"));
    try std.testing.expect(has("LEGACY_MODE_ALIASES = {\"sha256\": \"bytes\"}"));

    const help_start = try indexOf("HELP_LINES = [");
    const alias_start = try indexOf("LEGACY_MODE_ALIASES = {\"sha256\": \"bytes\"}");
    try std.testing.expect(alias_start < help_start);
    try std.testing.expect(std.mem.indexOf(u8, source[help_start..], "sha256") == null);
}

test "artifact diff invalid-mode template keeps argparse-compatible public wording" {
    try requireCurrentArtifactDiff();

    try std.testing.expectEqual(@as(usize, 1), count("INVALID_MODE_ERROR_TEMPLATE = ("));
    try std.testing.expect(has("artifact_diff.py: error: argument --mode: invalid "));
    try std.testing.expect(has("choice: {value!r} (choose from text, json, bytes)"));
    try std.testing.expect(!has("choose from text, json, bytes, sha256"));

    const invalid_template = try indexOf("INVALID_MODE_ERROR_TEMPLATE = (");
    const too_many_template = try indexOf("TOO_MANY_ARGUMENTS_ERROR = (");
    const parser_branch = try indexOf("print(INVALID_MODE_ERROR_TEMPLATE.format(value=mode), file=sys.stderr)");
    try std.testing.expect(invalid_template < too_many_template);
    try std.testing.expect(too_many_template < parser_branch);
}

test "artifact diff parser validates help, aliases, then invalid modes in source order" {
    try requireCurrentArtifactDiff();

    const parse_start = try indexOf("def parse_args(argv: list[str])");
    const help_branch = try indexOf("if argv == [\"--help\"] or argv == [\"-h\"]:");
    const loop_start = try indexOf("while index < len(argv):");
    const mode_value_guard = try indexOf("if index + 1 >= len(argv):");
    const validation_branch = try indexOf("if mode is not None and mode not in MODE_CHOICES:");
    const alias_branch = try indexOf("if mode in LEGACY_MODE_ALIASES:");
    const invalid_print = try indexOf("print(INVALID_MODE_ERROR_TEMPLATE.format(value=mode), file=sys.stderr)");
    const expected_assignment = try indexOf("expected = positionals[0] if len(positionals) >= 1 else None");

    try std.testing.expect(parse_start < help_branch);
    try std.testing.expect(help_branch < loop_start);
    try std.testing.expect(loop_start < mode_value_guard);
    try std.testing.expect(mode_value_guard < validation_branch);
    try std.testing.expect(validation_branch < alias_branch);
    try std.testing.expect(alias_branch < invalid_print);
    try std.testing.expect(invalid_print < expected_assignment);
}
