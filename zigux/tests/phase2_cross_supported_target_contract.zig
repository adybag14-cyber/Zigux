const std = @import("std");
const testing = std.testing;

const fixture_path = "zigux/tests/fixtures/phase2_cross_targets.json";
const direct_checker_path = "scripts/zigux/check-phase2-cross.py";
const alignment_checker_path = "scripts/zigux/check-phase2-cross-selftest-alignment.py";

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectMissing(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn count(haystack: []const u8, needle: []const u8) usize {
    var total: usize = 0;
    var rest = haystack;
    while (std.mem.indexOf(u8, rest, needle)) |index| {
        total += 1;
        rest = rest[index + needle.len ..];
    }
    return total;
}

test "phase2 cross fixture keeps the supported target boundary explicit" {
    const fixture = try readRepoFile(testing.allocator, fixture_path);
    defer testing.allocator.free(fixture);

    try expectContains(fixture, "\"phase\": \"Phase 2\"");
    try expectContains(fixture, "\"status\": \"active\"");
    try expectContains(fixture, "\"route\": \"make -C zigux phase2-cross\"");
    try expectContains(fixture, "\"archive_target_scope\"");
    try expectContains(fixture, "\"x86_64-linux\"");
    try expectContains(fixture, "\"target\": \"x86_64-linux\"");
    try expectContains(fixture, "\"review_status\": \"pinned bootstrap archive\"");
    try expectContains(fixture, "\"validation_mode\": \"archive_required\"");
    try expectContains(fixture, "\"target\": \"aarch64-linux\"");
    try expectContains(fixture, "\"review_status\": \"route contract only\"");
    try expectContains(fixture, "\"validation_mode\": \"route_contract_only\"");
    try expectMissing(fixture, "\"target\": \"riscv64-linux\"");
    try testing.expectEqual(@as(usize, 2), count(fixture, "\"target\":"));
}

test "direct checker reports the matrix and archive scope counts" {
    const checker = try readRepoFile(testing.allocator, direct_checker_path);
    defer testing.allocator.free(checker);

    try expectContains(checker, "ALLOWED_VALIDATION_MODES = (\"archive_required\", \"route_contract_only\")");
    try expectContains(checker, "EXPECTED_SELF_TEST_CASE_COUNT = 17");
    try expectContains(checker, "PHASE2_DIRECT_CROSS_ROUTE=pass");
    try expectContains(checker, "PHASE2_DIRECT_CROSS_ROUTE_TARGET_COUNT");
    try expectContains(checker, "PHASE2_DIRECT_CROSS_ROUTE_ARCHIVE_SCOPE_COUNT");
    try expectContains(checker, "(\"ARCHIVE_SCOPE_MISMATCH\", \",\".join(archive_target_scope))");
    try expectContains(checker, "(\"ARCHIVE_REQUIRED_TARGET_SET_MISMATCH\", \",\".join(sorted(archive_required_targets)))");
}

test "alignment checker limits the live cross matrix to two supported targets" {
    const checker = try readRepoFile(testing.allocator, alignment_checker_path);
    defer testing.allocator.free(checker);

    try expectContains(checker, "SUPPORTED_CROSS_TARGETS = (\"x86_64-linux\", \"aarch64-linux\")");
    try expectContains(checker, "\"phase2-cross\",");
    try expectContains(checker, "\"archive_target_scope\": [\"x86_64-linux\"]");
    try expectContains(checker, "payload[\"upgrade_policy\"][\"archive_target_scope\"] = [\"aarch64-linux\"]");
    try expectContains(checker, "payload[\"upgrade_policy\"][\"archive_target_scope\"] = [\"riscv64-linux\"]");
    try expectContains(checker, "unsupported archive_target_scope targets");
    try expectContains(checker, "PHASE2_CROSS_ALIGNMENT_FIXTURE_TARGET_COUNT");
    try expectContains(checker, "PHASE2_CROSS_ALIGNMENT_ARCHIVE_SCOPE_COUNT");
}
