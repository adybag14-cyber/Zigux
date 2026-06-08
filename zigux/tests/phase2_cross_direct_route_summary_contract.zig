const std = @import("std");

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn requireCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    try std.testing.expectEqual(expected, std.mem.count(u8, haystack, needle));
}

fn readRepoFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        std.Io.Limit.limited(256 * 1024),
    );
}

test "direct checker keeps pass summary markers distinct from failure output" {
    const checker_source = try readRepoFile("scripts/zigux/check-phase2-cross.py");
    defer std.testing.allocator.free(checker_source);

    try requireContains(checker_source, "print(\"PHASE2_DIRECT_CROSS_ROUTE=pass\")");
    try requireContains(checker_source, "PHASE2_DIRECT_CROSS_ROUTE_TARGET_COUNT={len(cross_targets)}");
    try requireContains(
        checker_source,
        "PHASE2_DIRECT_CROSS_ROUTE_ARCHIVE_SCOPE_COUNT={len(load_archive_target_scope(args.root.resolve()))}",
    );
    try requireContains(checker_source, "PHASE2_DIRECT_CROSS_ROUTE=fail");

    const fail_index = std.mem.indexOf(u8, checker_source, "PHASE2_DIRECT_CROSS_ROUTE=fail").?;
    const pass_index = std.mem.indexOf(u8, checker_source, "PHASE2_DIRECT_CROSS_ROUTE=pass").?;
    try std.testing.expect(fail_index < pass_index);
}

test "fixture keeps the current two target and one archive-scope packet" {
    const fixture_json = try readRepoFile("zigux/tests/fixtures/phase2_cross_targets.json");
    defer std.testing.allocator.free(fixture_json);

    try requireContains(fixture_json, "\"phase\": \"Phase 2\"");
    try requireContains(fixture_json, "\"status\": \"active\"");
    try requireCount(fixture_json, "\"target\":", 2);
    try requireCount(fixture_json, "\"validation_mode\": \"archive_required\"", 1);
    try requireCount(fixture_json, "\"validation_mode\": \"route_contract_only\"", 1);
    try requireCount(fixture_json, "\"archive_target_scope\"", 1);
    try requireContains(fixture_json, "\"x86_64-linux\"");
    try requireContains(fixture_json, "\"aarch64-linux\"");
    try requireNotContains(fixture_json, "riscv64-linux");
    try requireNotContains(fixture_json, "-musl");
}

test "pass summary count markers describe the same fixture boundary" {
    const checker_source = try readRepoFile("scripts/zigux/check-phase2-cross.py");
    defer std.testing.allocator.free(checker_source);
    const fixture_json = try readRepoFile("zigux/tests/fixtures/phase2_cross_targets.json");
    defer std.testing.allocator.free(fixture_json);

    try requireContains(fixture_json, "\"route\": \"make -C zigux phase2-cross\"");
    try requireCount(fixture_json, "\"route\": \"make -C zigux phase2-cross\"", 3);
    try requireCount(fixture_json, "\"review_status\": \"pinned bootstrap archive\"", 1);
    try requireCount(fixture_json, "\"review_status\": \"route contract only\"", 1);

    try requireContains(checker_source, "cross_targets = fixture.get(\"cross_targets\")");
    try requireContains(checker_source, "load_archive_target_scope(args.root.resolve())");
    try requireContains(checker_source, "EXPECTED_SELF_TEST_CASE_COUNT = 17");
}
