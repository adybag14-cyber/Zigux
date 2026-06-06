const std = @import("std");
const Io = std.Io;

const artifact_diff_path = "scripts/zigux/artifact_diff.py";

fn artifactDiffSource() ![]u8 {
    return Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        artifact_diff_path,
        std.testing.allocator,
        .limited(256 * 1024),
    );
}

fn contains(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

fn requireLiveLegacyAliasSurface(source: []const u8) !void {
    if (!contains(source, "LEGACY_MODE_ALIASES = {\"sha256\": \"bytes\"}")) {
        return error.SkipZigTest;
    }
}

fn expectContains(source: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, source, needle) != null);
}

fn expectBefore(source: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, source, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, source, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

test "artifact diff keeps sha256 as a legacy alias outside advertised modes" {
    const source = try artifactDiffSource();
    defer std.testing.allocator.free(source);
    try requireLiveLegacyAliasSurface(source);

    try expectContains(source, "MODE_CHOICES = (\"text\", \"json\", \"bytes\")");
    try expectContains(source, "LEGACY_MODE_ALIASES = {\"sha256\": \"bytes\"}");
    try expectContains(source, "def normalize_mode(mode: str) -> str:");
    try expectContains(source, "return LEGACY_MODE_ALIASES.get(mode, mode)");
    try expectBefore(
        source,
        "LEGACY_MODE_ALIASES = {\"sha256\": \"bytes\"}",
        "HELP_LINES = [",
    );
}

test "artifact diff parser normalizes legacy alias before invalid-mode rejection" {
    const source = try artifactDiffSource();
    defer std.testing.allocator.free(source);
    try requireLiveLegacyAliasSurface(source);

    try expectBefore(
        source,
        "if mode is not None and mode not in MODE_CHOICES:",
        "expected = positionals[0] if len(positionals) >= 1 else None",
    );
    try expectContains(
        source,
        "if mode in LEGACY_MODE_ALIASES:\n            mode = LEGACY_MODE_ALIASES[mode]\n        else:",
    );
    try expectBefore(
        source,
        "mode = LEGACY_MODE_ALIASES[mode]",
        "print(INVALID_MODE_ERROR_TEMPLATE.format(value=mode), file=sys.stderr)",
    );
    try expectBefore(
        source,
        "result = compare(mode, expected, actual)",
        "return emit_result(\"pass\" if result.ok else \"fail\", mode, expected, actual, result.extra_lines)",
    );
}

test "artifact diff self-test proves sha256 alias emits bytes mode" {
    const source = try artifactDiffSource();
    defer std.testing.allocator.free(source);
    try requireLiveLegacyAliasSurface(source);

    try expectContains(source, "\"legacy_sha256_alias\",");
    try expectContains(source, "legacy_alias = run_parser_probe([\"--mode\", \"sha256\", str(blob_a), str(blob_a)])");
    try expectContains(source, "assert_case(legacy_alias.returncode == 0, \"legacy_sha256_alias\")");
    try expectContains(source, "assert_case(\"ARTIFACT_DIFF=pass\" in legacy_alias.stdout, \"legacy_sha256_alias\")");
    try expectContains(source, "assert_case(\"MODE=bytes\" in legacy_alias.stdout, \"legacy_sha256_alias\")");
    try expectBefore(
        source,
        "\"legacy_sha256_alias\",",
        "\"missing_mode_value_rejected\",",
    );
    try expectBefore(
        source,
        "assert_case(\"MODE=bytes\" in legacy_alias.stdout, \"legacy_sha256_alias\")",
        "covered.append(\"legacy_sha256_alias\")",
    );
}
