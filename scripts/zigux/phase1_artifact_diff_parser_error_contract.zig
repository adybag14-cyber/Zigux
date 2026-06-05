const std = @import("std");

const max_source_bytes = 128 * 1024;

fn readArtifactDiff(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, "scripts/zigux/artifact_diff.py", allocator, .limited(max_source_bytes)) catch |first_err| {
        if (first_err != error.FileNotFound) return first_err;
        return std.Io.Dir.cwd().readFileAlloc(std.testing.io, "artifact_diff.py", allocator, .limited(max_source_bytes));
    };
}

fn contains(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(contains(haystack, needle));
}

fn expectOnce(haystack: []const u8, needle: []const u8) !void {
    var count: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOf(u8, haystack[index..], needle)) |offset| {
        count += 1;
        index += offset + needle.len;
    }
    try std.testing.expectEqual(@as(usize, 1), count);
}

fn expectOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "artifact diff parser errors keep stable diagnostic constants" {
    const source = try readArtifactDiff(std.testing.allocator);
    defer std.testing.allocator.free(source);

    if (!contains(source, "MISSING_ARGUMENT_ERROR")) return error.SkipZigTest;

    try expectContains(source, "MISSING_ARGUMENT_ERROR = (");
    try expectContains(source, "\"are required unless --self-test is set\"");
    try expectContains(source, "INVALID_MODE_ERROR_TEMPLATE = (");
    try expectContains(source, "\"invalid choice: {value!r} (choose from text, json, bytes)\"");
    try expectContains(source, "TOO_MANY_ARGUMENTS_ERROR = (");
    try expectContains(source, "\"expected exactly two positional arguments\"");
    try expectOnce(source, "MODE_CHOICES = (\"text\", \"json\", \"bytes\")");
}

test "artifact diff parser rejects incomplete and extra argv before comparing files" {
    const source = try readArtifactDiff(std.testing.allocator);
    defer std.testing.allocator.free(source);

    if (!contains(source, "def parse_args(argv: list[str])")) return error.SkipZigTest;

    try expectOrdered(
        source,
        "if arg == \"--mode\":" ,
        "expected = positionals[0] if len(positionals) >= 1 else None",
    );
    try expectOrdered(
        source,
        "if index + 1 >= len(argv):",
        "mode = argv[index + 1]",
    );
    try expectOrdered(
        source,
        "if len(positionals) > 2:",
        "if mode is None or expected_text is None or actual_text is None:",
    );
    try expectContains(source, "print(MISSING_ARGUMENT_ERROR, file=sys.stderr)");
    try expectContains(source, "print(TOO_MANY_ARGUMENTS_ERROR, file=sys.stderr)");
    try expectContains(source, "return 2");
}

test "artifact diff parser keeps invalid-mode checks and legacy sha256 alias separate" {
    const source = try readArtifactDiff(std.testing.allocator);
    defer std.testing.allocator.free(source);

    if (!contains(source, "LEGACY_MODE_ALIASES")) return error.SkipZigTest;

    try expectOnce(source, "LEGACY_MODE_ALIASES = {\"sha256\": \"bytes\"}");
    try expectContains(source, "def normalize_mode(mode: str) -> str:");
    try expectContains(source, "return LEGACY_MODE_ALIASES.get(mode, mode)");
    try expectOrdered(
        source,
        "if mode is not None and mode not in MODE_CHOICES:",
        "if mode in LEGACY_MODE_ALIASES:",
    );
    try expectOrdered(
        source,
        "if mode in LEGACY_MODE_ALIASES:",
        "print(INVALID_MODE_ERROR_TEMPLATE.format(value=mode), file=sys.stderr)",
    );
}

test "artifact diff self-test catalog covers parser error cases in order" {
    const source = try readArtifactDiff(std.testing.allocator);
    defer std.testing.allocator.free(source);

    if (!contains(source, "\"missing_mode_value_rejected\",")) return error.SkipZigTest;

    try expectOrdered(source, "\"legacy_sha256_alias\",", "\"missing_mode_value_rejected\",");
    try expectOrdered(source, "\"missing_mode_value_rejected\",", "\"missing_positional_arguments_rejected\",");
    try expectOrdered(source, "\"missing_positional_arguments_rejected\",", "\"invalid_mode_rejected\",");
    try expectOrdered(source, "\"invalid_mode_rejected\",", "\"extra_positional_rejected\",");
    try expectContains(source, "covered.append(\"missing_mode_value_rejected\")");
    try expectContains(source, "covered.append(\"missing_positional_arguments_rejected\")");
    try expectContains(source, "covered.append(\"invalid_mode_rejected\")");
    try expectContains(source, "covered.append(\"extra_positional_rejected\")");
    try expectContains(source, "assert_case(covered == SELF_TEST_CASES, \"self_test_case_order\")");
}
