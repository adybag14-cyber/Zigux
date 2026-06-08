const std = @import("std");

const artifact_diff_path = "scripts/zigux/artifact_diff.py";

fn readArtifactDiff(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        artifact_diff_path,
        allocator,
        .limited(1024 * 1024),
    );
}

fn hasNeedle(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

fn expectCurrentArtifactDiffOrSkip(source: []const u8) !void {
    if (!hasNeedle(source, "class ComparisonResult:")) {
        return error.SkipZigTest;
    }
}

fn expectContainsInOrder(source: []const u8, markers: []const []const u8) !void {
    var offset: usize = 0;
    for (markers) |marker| {
        const found = std.mem.indexOfPos(u8, source, offset, marker) orelse {
            std.debug.print("missing ordered marker: {s}\n", .{marker});
            return error.TestExpectedEqual;
        };
        offset = found + marker.len;
    }
}

test "comparison result envelope stays frozen and minimal" {
    const allocator = std.testing.allocator;
    const source = try readArtifactDiff(allocator);
    defer allocator.free(source);
    try expectCurrentArtifactDiffOrSkip(source);

    try std.testing.expect(hasNeedle(source, "@dataclass(frozen=True)\nclass ComparisonResult:\n"));
    try expectContainsInOrder(source, &.{
        "class ComparisonResult:\n",
        "    ok: bool\n",
        "    extra_lines: list[str]\n",
        "\n\ndef read_bytes(path: Path) -> bytes:\n",
    });
}

test "comparison helpers return ComparisonResult with explicit extra lines" {
    const allocator = std.testing.allocator;
    const source = try readArtifactDiff(allocator);
    defer allocator.free(source);
    try expectCurrentArtifactDiffOrSkip(source);

    try expectContainsInOrder(source, &.{
        "def compare_text(expected: Path, actual: Path) -> ComparisonResult:\n",
        "        return ComparisonResult(ok=True, extra_lines=[])\n",
        "    return ComparisonResult(ok=False, extra_lines=[])\n",
    });
    try expectContainsInOrder(source, &.{
        "def compare_json(expected: Path, actual: Path) -> ComparisonResult:\n",
        "        return ComparisonResult(ok=False, extra_lines=[expected_error])\n",
        "        return ComparisonResult(ok=False, extra_lines=[actual_error])\n",
        "        return ComparisonResult(ok=True, extra_lines=[])\n",
        "    return ComparisonResult(ok=False, extra_lines=[])\n",
    });
    try expectContainsInOrder(source, &.{
        "def compare_bytes(expected: Path, actual: Path) -> ComparisonResult:\n",
        "        return ComparisonResult(ok=True, extra_lines=[f\"SHA256={expected_digest}\"])\n",
        "    return ComparisonResult(\n",
        "        ok=False,\n",
        "            f\"EXPECTED_SHA256={expected_digest}\",\n",
        "            f\"ACTUAL_SHA256={actual_digest}\",\n",
    });
}

test "compare dispatch normalizes before path checks and fail-closes unsupported modes" {
    const allocator = std.testing.allocator;
    const source = try readArtifactDiff(allocator);
    defer allocator.free(source);
    try expectCurrentArtifactDiffOrSkip(source);

    try expectContainsInOrder(source, &.{
        "def compare(mode: str, expected: Path, actual: Path) -> ComparisonResult:\n",
        "    mode = normalize_mode(mode)\n",
        "    problem = path_problem_lines(expected, actual)\n",
        "    if problem is not None:\n",
        "        return ComparisonResult(ok=False, extra_lines=problem)\n",
        "    if mode == \"text\":\n",
        "        return compare_text(expected, actual)\n",
        "    if mode == \"json\":\n",
        "        return compare_json(expected, actual)\n",
        "    if mode == \"bytes\":\n",
        "        return compare_bytes(expected, actual)\n",
        "    raise ValueError(f\"unsupported mode: {mode}\")\n",
    });
}
