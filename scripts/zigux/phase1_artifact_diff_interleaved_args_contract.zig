const std = @import("std");

const artifact_diff_path = "scripts/zigux/artifact_diff.py";

fn readArtifactDiff(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        artifact_diff_path,
        allocator,
        .limited(256 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

fn requireCurrentParser(source: []const u8) !void {
    if (std.mem.indexOf(u8, source, "LEGACY_MODE_ALIASES") == null or
        std.mem.indexOf(u8, source, "positionals: list[str] = []") == null)
    {
        return error.SkipZigTest;
    }
}

test "artifact diff parser preserves interleaved positionals around mode option" {
    const allocator = std.testing.allocator;
    const source = try readArtifactDiff(allocator);
    defer allocator.free(source);
    try requireCurrentParser(source);

    try expectContains(source, "while index < len(argv):");
    try expectContains(source, "if arg == \"--mode\":");
    try expectContains(source, "mode = argv[index + 1]");
    try expectContains(source, "positionals.append(arg)");
    try expectContains(source, "expected = positionals[0] if len(positionals) >= 1 else None");
    try expectContains(source, "actual = positionals[1] if len(positionals) >= 2 else None");
    try expectContains(source, "if len(positionals) > 2:");

    try expectBefore(source, "positionals: list[str] = []", "while index < len(argv):");
    try expectBefore(source, "if arg == \"--mode\":", "positionals.append(arg)");
    try expectBefore(source, "positionals.append(arg)", "expected = positionals[0] if len(positionals) >= 1 else None");
    try expectBefore(source, "expected = positionals[0] if len(positionals) >= 1 else None", "if len(positionals) > 2:");
}

test "artifact diff main keeps parsed expected and actual paths paired with parsed mode" {
    const allocator = std.testing.allocator;
    const source = try readArtifactDiff(allocator);
    defer allocator.free(source);
    try requireCurrentParser(source);

    try expectContains(source, "self_test, mode, expected_text, actual_text = parsed");
    try expectContains(source, "if mode is None or expected_text is None or actual_text is None:");
    try expectContains(source, "expected = Path(expected_text)");
    try expectContains(source, "actual = Path(actual_text)");
    try expectContains(source, "result = compare(mode, expected, actual)");
    try expectContains(source, "return emit_result(\"pass\" if result.ok else \"fail\", mode, expected, actual, result.extra_lines)");

    try expectBefore(source, "self_test, mode, expected_text, actual_text = parsed", "expected = Path(expected_text)");
    try expectBefore(source, "expected = Path(expected_text)", "result = compare(mode, expected, actual)");
    try expectBefore(source, "result = compare(mode, expected, actual)", "return emit_result(\"pass\" if result.ok else \"fail\", mode, expected, actual, result.extra_lines)");
}

test "artifact diff self-test catalog keeps parser edge cases separate from interleaving" {
    const allocator = std.testing.allocator;
    const source = try readArtifactDiff(allocator);
    defer allocator.free(source);
    try requireCurrentParser(source);

    try expectContains(source, "\"missing_mode_value_rejected\",");
    try expectContains(source, "\"missing_positional_arguments_rejected\",");
    try expectContains(source, "\"invalid_mode_rejected\",");
    try expectContains(source, "\"extra_positional_rejected\",");
    try expectContains(source, "missing_positionals = run_parser_probe([\"--mode\", \"text\"])");
    try expectContains(source, "[\"--mode\", \"text\", str(expected), str(actual), str(missing)]");

    try expectBefore(source, "\"missing_mode_value_rejected\",", "\"missing_positional_arguments_rejected\",");
    try expectBefore(source, "\"missing_positional_arguments_rejected\",", "\"invalid_mode_rejected\",");
    try expectBefore(source, "\"invalid_mode_rejected\",", "\"extra_positional_rejected\",");
}
