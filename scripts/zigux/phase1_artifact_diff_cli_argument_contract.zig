const std = @import("std");

const artifact_diff_source = @embedFile("artifact_diff.py");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, needles: []const []const u8) !void {
    var cursor: usize = 0;
    for (needles) |needle| {
        const found = std.mem.indexOf(u8, haystack[cursor..], needle) orelse return error.MissingExpectedMarker;
        cursor += found + needle.len;
    }
}

fn requireCurrentArtifactDiffSource() !void {
    if (std.mem.indexOf(u8, artifact_diff_source, "MODE_CHOICES = (\"text\", \"json\", \"bytes\")") == null) {
        return error.SkipZigTest;
    }
}

test "artifact diff parser keeps current mode roster and legacy alias normalization" {
    try requireCurrentArtifactDiffSource();

    try expectContains(artifact_diff_source, "MODE_CHOICES = (\"text\", \"json\", \"bytes\")");
    try expectContains(artifact_diff_source, "LEGACY_MODE_ALIASES = {\"sha256\": \"bytes\"}");
    try expectContains(artifact_diff_source, "def normalize_mode(mode: str) -> str:");
    try expectContains(artifact_diff_source, "return LEGACY_MODE_ALIASES.get(mode, mode)");

    try expectOrdered(artifact_diff_source, &.{
        "if mode is not None and mode not in MODE_CHOICES:",
        "if mode in LEGACY_MODE_ALIASES:",
        "mode = LEGACY_MODE_ALIASES[mode]",
        "else:",
        "print(INVALID_MODE_ERROR_TEMPLATE.format(value=mode), file=sys.stderr)",
    });
}

test "artifact diff parser diagnostics remain fail-closed for missing and extra arguments" {
    try requireCurrentArtifactDiffSource();

    try expectContains(artifact_diff_source, "MISSING_ARGUMENT_ERROR = (");
    try expectContains(artifact_diff_source, "--mode, expected, and actual ");
    try expectContains(artifact_diff_source, "are required unless --self-test is set");
    try expectContains(artifact_diff_source, "TOO_MANY_ARGUMENTS_ERROR = (");
    try expectContains(artifact_diff_source, "expected exactly two positional ");
    try expectContains(artifact_diff_source, "arguments");

    try expectOrdered(artifact_diff_source, &.{
        "if arg == \"--mode\":",
        "if index + 1 >= len(argv):",
        "print(MISSING_ARGUMENT_ERROR, file=sys.stderr)",
        "return 2",
    });
    try expectOrdered(artifact_diff_source, &.{
        "if len(positionals) > 2:",
        "print(TOO_MANY_ARGUMENTS_ERROR, file=sys.stderr)",
        "return 2",
    });
    try expectOrdered(artifact_diff_source, &.{
        "if mode is None or expected_text is None or actual_text is None:",
        "print(MISSING_ARGUMENT_ERROR, file=sys.stderr)",
        "return 2",
    });
}

test "artifact diff self-test catalog covers CLI argument boundaries" {
    try requireCurrentArtifactDiffSource();

    try expectOrdered(artifact_diff_source, &.{
        "\"legacy_sha256_alias\"",
        "\"missing_mode_value_rejected\"",
        "\"missing_positional_arguments_rejected\"",
        "\"invalid_mode_rejected\"",
        "\"extra_positional_rejected\"",
    });
    try expectContains(artifact_diff_source, "legacy_alias = run_parser_probe([\"--mode\", \"sha256\", str(blob_a), str(blob_a)])");
    try expectContains(artifact_diff_source, "assert_case(\"ARTIFACT_DIFF=pass\" in legacy_alias.stdout, \"legacy_sha256_alias\")");
    try expectContains(artifact_diff_source, "assert_case(\"MODE=bytes\" in legacy_alias.stdout, \"legacy_sha256_alias\")");
    try expectContains(artifact_diff_source, "missing_mode_value = run_parser_probe([\"--mode\"])");
    try expectContains(artifact_diff_source, "missing_positionals = run_parser_probe([\"--mode\", \"text\"])");
    try expectContains(artifact_diff_source, "extra_positional = run_parser_probe(");
}
