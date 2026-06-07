const std = @import("std");

const artifact_diff_path = "scripts/zigux/artifact_diff.py";

fn readArtifactDiff(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, artifact_diff_path, allocator, .limited(512 * 1024));
}

fn requireCurrentNormalizeSurface(source: []const u8) !void {
    if (!std.mem.containsAtLeast(u8, source, 1, "LEGACY_MODE_ALIASES = {\"sha256\": \"bytes\"}") or
        !std.mem.containsAtLeast(u8, source, 1, "def normalize_mode(mode: str) -> str:"))
    {
        return error.SkipZigTest;
    }
}

fn countOf(source: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOfPos(u8, source, index, needle)) |found| {
        count += 1;
        index = found + needle.len;
    }
    return count;
}

fn requireInOrder(source: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, source, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, source, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "artifact diff has one small normalize_mode alias boundary" {
    const allocator = std.testing.allocator;
    const source = try readArtifactDiff(allocator);
    defer allocator.free(source);

    try requireCurrentNormalizeSurface(source);

    try std.testing.expectEqual(@as(usize, 1), countOf(source, "LEGACY_MODE_ALIASES = {\"sha256\": \"bytes\"}"));
    try std.testing.expectEqual(@as(usize, 1), countOf(source, "def normalize_mode(mode: str) -> str:"));
    try std.testing.expect(std.mem.containsAtLeast(
        u8,
        source,
        1,
        "    return LEGACY_MODE_ALIASES.get(mode, mode)",
    ));
}

test "compare normalizes legacy mode before path and mode dispatch" {
    const allocator = std.testing.allocator;
    const source = try readArtifactDiff(allocator);
    defer allocator.free(source);

    try requireCurrentNormalizeSurface(source);

    const compare_marker =
        \\def compare(mode: str, expected: Path, actual: Path) -> ComparisonResult:
        \\    mode = normalize_mode(mode)
        \\    problem = path_problem_lines(expected, actual)
    ;
    try std.testing.expect(std.mem.containsAtLeast(u8, source, 1, compare_marker));
    try requireInOrder(source, "    mode = normalize_mode(mode)", "    if mode == \"text\":");
    try requireInOrder(source, "    mode = normalize_mode(mode)", "    if mode == \"bytes\":");
}

test "parser accepts legacy aliases only through normalize-equivalent table" {
    const allocator = std.testing.allocator;
    const source = try readArtifactDiff(allocator);
    defer allocator.free(source);

    try requireCurrentNormalizeSurface(source);

    const parser_alias_marker =
        \\    if mode is not None and mode not in MODE_CHOICES:
        \\        if mode in LEGACY_MODE_ALIASES:
        \\            mode = LEGACY_MODE_ALIASES[mode]
        \\        else:
    ;
    try std.testing.expect(std.mem.containsAtLeast(u8, source, 1, parser_alias_marker));
    try requireInOrder(
        source,
        "        if mode in LEGACY_MODE_ALIASES:",
        "            print(INVALID_MODE_ERROR_TEMPLATE.format(value=mode), file=sys.stderr)",
    );
    try requireInOrder(source, "def normalize_mode(mode: str) -> str:", "def compare(mode: str, expected: Path, actual: Path) -> ComparisonResult:");
}
