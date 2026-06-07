const std = @import("std");

const source_path = "scripts/zigux/artifact_diff.py";

fn readSource(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, source_path, allocator, .limited(256 * 1024));
}

fn requireContains(source: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, source, needle) != null);
}

fn requireOrdered(source: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, source, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, source, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "artifact diff self-test main path exits through run_self_test" {
    const allocator = std.testing.allocator;
    const source = try readSource(allocator);
    defer allocator.free(source);

    try requireContains(source, "def run_self_test() -> int:");
    try requireContains(source, "def main() -> int:");
    try requireContains(source, "if self_test:\n        return run_self_test()");
    try requireContains(source, "if __name__ == \"__main__\":\n    raise SystemExit(main())");
    try requireOrdered(source, "if self_test:\n        return run_self_test()", "if mode is None or expected_text is None or actual_text is None:");
}

test "artifact diff self-test emits stable success envelope before returning zero" {
    const allocator = std.testing.allocator;
    const source = try readSource(allocator);
    defer allocator.free(source);

    try requireContains(source, "print(\"ARTIFACT_DIFF_SELF_TEST=pass\")");
    try requireContains(source, "print(f\"ARTIFACT_DIFF_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}\")");
    try requireContains(source, "print(\"ARTIFACT_DIFF_SELF_TEST_CASES=\" + \",\".join(SELF_TEST_CASES))");
    try requireContains(source, "return 0\n\n\ndef parse_args");
    try requireOrdered(source, "assert_case(covered == SELF_TEST_CASES, \"self_test_case_order\")", "print(\"ARTIFACT_DIFF_SELF_TEST=pass\")");
    try requireOrdered(source, "print(\"ARTIFACT_DIFF_SELF_TEST_CASES=\" + \",\".join(SELF_TEST_CASES))", "return 0\n\n\ndef parse_args");
}

test "artifact diff self-test stays parser-independent after self-test flag" {
    const allocator = std.testing.allocator;
    const source = try readSource(allocator);
    defer allocator.free(source);

    try requireContains(source, "if arg == \"--self-test\":\n            self_test = True\n            index += 1\n            continue");
    try requireOrdered(source, "if self_test:\n        return run_self_test()", "if mode is None or expected_text is None or actual_text is None:");
    try requireOrdered(source, "if self_test:\n        return run_self_test()", "expected = Path(expected_text)");
    try requireOrdered(source, "if self_test:\n        return run_self_test()", "result = compare(mode, expected, actual)");
}
