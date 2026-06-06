const std = @import("std");

const source = @embedFile("artifact_diff.py");

fn contains(needle: []const u8) bool {
    return std.mem.indexOf(u8, source, needle) != null;
}

fn indexOf(needle: []const u8) usize {
    return std.mem.indexOf(u8, source, needle) orelse std.debug.panic("missing marker: {s}", .{needle});
}

fn count(needle: []const u8) usize {
    var total: usize = 0;
    var start: usize = 0;
    while (std.mem.indexOfPos(u8, source, start, needle)) |pos| {
        total += 1;
        start = pos + needle.len;
    }
    return total;
}

test "comparison result schema stays frozen and typed" {
    if (!contains("@dataclass(frozen=True)")) return error.SkipZigTest;

    try std.testing.expectEqual(@as(usize, 1), count("@dataclass(frozen=True)\nclass ComparisonResult:"));
    try std.testing.expect(contains("class ComparisonResult:\n    ok: bool\n    extra_lines: list[str]\n"));
    try std.testing.expect(indexOf("class ComparisonResult:") < indexOf("def compare_text(expected: Path, actual: Path) -> ComparisonResult:"));
    try std.testing.expect(indexOf("class ComparisonResult:") < indexOf("def compare_json(expected: Path, actual: Path) -> ComparisonResult:"));
    try std.testing.expect(indexOf("class ComparisonResult:") < indexOf("def compare_bytes(expected: Path, actual: Path) -> ComparisonResult:"));
    try std.testing.expect(indexOf("class ComparisonResult:") < indexOf("def compare(mode: str, expected: Path, actual: Path) -> ComparisonResult:"));
}

test "mode helpers return comparison result envelopes directly" {
    if (!contains("def compare_text(expected: Path, actual: Path) -> ComparisonResult:")) return error.SkipZigTest;

    try std.testing.expect(contains(
        "def compare_text(expected: Path, actual: Path) -> ComparisonResult:\n" ++
            "    if read_bytes(expected) == read_bytes(actual):\n" ++
            "        return ComparisonResult(ok=True, extra_lines=[])\n" ++
            "    return ComparisonResult(ok=False, extra_lines=[])\n",
    ));
    try std.testing.expect(contains(
        "if expected_error is not None:\n" ++
            "        return ComparisonResult(ok=False, extra_lines=[expected_error])\n" ++
            "    actual_bytes, actual_error = canonical_json_bytes(actual, side=\"ACTUAL\")\n" ++
            "    if actual_error is not None:\n" ++
            "        return ComparisonResult(ok=False, extra_lines=[actual_error])\n",
    ));
    try std.testing.expect(contains(
        "if expected_bytes == actual_bytes:\n" ++
            "        return ComparisonResult(ok=True, extra_lines=[])\n" ++
            "    return ComparisonResult(ok=False, extra_lines=[])\n",
    ));
    try std.testing.expect(contains(
        "if expected_digest == actual_digest:\n" ++
            "        return ComparisonResult(ok=True, extra_lines=[f\"SHA256={expected_digest}\"])\n" ++
            "    return ComparisonResult(\n" ++
            "        ok=False,\n" ++
            "        extra_lines=[\n" ++
            "            f\"EXPECTED_SHA256={expected_digest}\",\n" ++
            "            f\"ACTUAL_SHA256={actual_digest}\",\n" ++
            "        ],\n" ++
            "    )\n",
    ));
}

test "dispatcher preserves comparison result before emit_result" {
    if (!contains("def compare(mode: str, expected: Path, actual: Path) -> ComparisonResult:")) return error.SkipZigTest;

    try std.testing.expect(contains(
        "problem = path_problem_lines(expected, actual)\n" ++
            "    if problem is not None:\n" ++
            "        return ComparisonResult(ok=False, extra_lines=problem)\n",
    ));
    try std.testing.expect(indexOf("mode = normalize_mode(mode)") < indexOf("problem = path_problem_lines(expected, actual)"));
    try std.testing.expect(indexOf("if mode == \"text\":\n        return compare_text(expected, actual)") < indexOf("if mode == \"json\":\n        return compare_json(expected, actual)"));
    try std.testing.expect(indexOf("if mode == \"json\":\n        return compare_json(expected, actual)") < indexOf("if mode == \"bytes\":\n        return compare_bytes(expected, actual)"));
    try std.testing.expect(contains("raise ValueError(f\"unsupported mode: {mode}\")"));
    try std.testing.expect(contains(
        "result = compare(mode, expected, actual)\n" ++
            "    return emit_result(\"pass\" if result.ok else \"fail\", mode, expected, actual, result.extra_lines)\n",
    ));
}
