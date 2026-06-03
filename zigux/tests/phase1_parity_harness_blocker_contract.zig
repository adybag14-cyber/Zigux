const std = @import("std");

const harness_path = "zigux/tests/fixtures/phase1_helpers_c_harness.c";
const harness_blocker_id = "phase1_helpers_c_harness_missing_c_sources";

const expected_helpers = [_][]const u8{
    "tools/lib/argv_split.zig",
    "tools/lib/bitmap.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/string.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectExactCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    try std.testing.expectEqual(expected, std.mem.count(u8, haystack, needle));
}

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, std.testing.allocator, .limited(limit));
}

test "phase1 parity checker keeps the parked c harness path explicit" {
    const checker_source = try readRepoFile("scripts/zigux/check-phase1-parity.py", 128 * 1024);
    defer std.testing.allocator.free(checker_source);

    try expectExactCount(checker_source, "HARNESS_REL = Path(\"zigux/tests/fixtures/phase1_helpers_c_harness.c\")", 1);
    try expectExactCount(checker_source, "def harness_path(root: Path) -> Path:", 1);
    try expectContains(checker_source, "return root / HARNESS_REL");
    try expectContains(checker_source, "required_paths = [FIXTURE_REL, HARNESS_REL, ARTIFACT_DIFF_REL]");
    try expectContains(checker_source, "missing_harness = collect_input_issues(tmp_root)");
    try expectContains(checker_source, "assert f\"missing:{HARNESS_REL.as_posix()}\" in missing_harness");
    try expectContains(checker_source, "phase1_helpers_c_harness");
}

test "phase1 replay blocker fixture records the c harness as parked and blocked" {
    const blockers_json = try readRepoFile("zigux/tests/fixtures/phase1_replay_blockers.json", 16 * 1024);
    defer std.testing.allocator.free(blockers_json);

    try expectContains(blockers_json, "\"status\": \"parked\"");
    try expectExactCount(blockers_json, "\"c_harness\": {", 1);
    try expectContains(blockers_json, "\"path\": \"zigux/tests/fixtures/phase1_helpers_c_harness.c\"");
    try expectContains(blockers_json, "\"state\": \"blocked\"");
    try expectContains(blockers_json, "\"helper_count\": 13");
    try expectContains(blockers_json, "\"blocker_id\": \"phase1_helpers_c_harness_missing_c_sources\"");
    try expectContains(blockers_json, "The old host-side parity route still depends on helper `tools/lib/*.c` inputs");
}

test "phase1 c harness blocker keeps the full helper roster in fixture order" {
    const blockers_json = try readRepoFile("zigux/tests/fixtures/phase1_replay_blockers.json", 16 * 1024);
    defer std.testing.allocator.free(blockers_json);

    var cursor: usize = std.mem.indexOf(u8, blockers_json, "\"c_harness\": {").?;
    for (expected_helpers) |helper| {
        const remaining = blockers_json[cursor..];
        const next = std.mem.indexOf(u8, remaining, helper) orelse return error.HelperOutOfOrder;
        cursor += next + helper.len;
    }

    try std.testing.expectEqual(@as(usize, 13), expected_helpers.len);
    try expectExactCount(blockers_json, harness_blocker_id, 1);
    try expectExactCount(blockers_json, harness_path, 1);
}
