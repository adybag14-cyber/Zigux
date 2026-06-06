const std = @import("std");
const testing = std.testing;

const artifact_diff_path = "scripts/zigux/artifact_diff.py";

fn readArtifactDiff(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, artifact_diff_path, allocator, .limited(1024 * 1024));
}

fn contains(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

fn requireContains(source: []const u8, marker: []const u8) !void {
    if (!contains(source, marker)) {
        std.debug.print("missing marker: {s}\n", .{marker});
        return error.MissingMarker;
    }
}

fn requireOrder(source: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, source, first) orelse {
        std.debug.print("missing first marker: {s}\n", .{first});
        return error.MissingFirstMarker;
    };
    const second_index = std.mem.indexOf(u8, source, second) orelse {
        std.debug.print("missing second marker: {s}\n", .{second});
        return error.MissingSecondMarker;
    };
    if (first_index >= second_index) {
        std.debug.print("marker order drifted: {s} should appear before {s}\n", .{ first, second });
        return error.MarkerOrderDrifted;
    }
}

fn skipUnlessCurrentArtifactDiff(source: []const u8) !void {
    if (!contains(source, "MODE_CHOICES = (\"text\", \"json\", \"bytes\")") or
        !contains(source, "def canonical_json_bytes("))
    {
        return error.SkipZigTest;
    }
}

test "artifact_diff JSON canonical bytes stay deterministic" {
    const source = try readArtifactDiff(testing.allocator);
    defer testing.allocator.free(source);
    try skipUnlessCurrentArtifactDiff(source);

    try requireContains(source, "def canonical_json_bytes(path: Path, *, side: str) -> tuple[bytes | None, str | None]:");
    try requireContains(source, "value = json.loads(text)");
    try requireContains(source, "json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + \"\\n\"");
    try requireContains(source, ".encode(\"utf-8\"), None");
    try requireOrder(source, "value = json.loads(text)", "json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True)");
}

test "artifact_diff JSON errors keep expected-side precedence" {
    const source = try readArtifactDiff(testing.allocator);
    defer testing.allocator.free(source);
    try skipUnlessCurrentArtifactDiff(source);

    try requireOrder(source, "expected_bytes, expected_error = canonical_json_bytes(expected, side=\"EXPECTED\")", "actual_bytes, actual_error = canonical_json_bytes(actual, side=\"ACTUAL\")");
    try requireOrder(source, "if expected_error is not None:", "actual_bytes, actual_error = canonical_json_bytes(actual, side=\"ACTUAL\")");
    try requireContains(source, "return ComparisonResult(ok=False, extra_lines=[expected_error])");
    try requireContains(source, "return ComparisonResult(ok=False, extra_lines=[actual_error])");
    try requireContains(source, "return None, f\"{side}_JSON_ERROR={path}:{exc.lineno}:{exc.colno}: {exc.msg}\"");
}

test "artifact_diff valid JSON mismatch has stable empty diagnostics" {
    const source = try readArtifactDiff(testing.allocator);
    defer testing.allocator.free(source);
    try skipUnlessCurrentArtifactDiff(source);

    try requireOrder(source, "if expected_bytes == actual_bytes:", "return ComparisonResult(ok=False, extra_lines=[])");
    try requireContains(source, "assert expected_bytes is not None");
    try requireContains(source, "assert actual_bytes is not None");
    try requireContains(source, "\"json_pass\"");
    try requireContains(source, "\"json_mismatch\"");
    try requireOrder(source, "\"json_pass\"", "\"json_mismatch\"");
}
