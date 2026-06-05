const std = @import("std");
const testing = std.testing;

const max_file_size = 256 * 1024;

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(testing.io, path, allocator, .limited(max_file_size));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectAbsent(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try testing.expect(before_index < after_index);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, cursor, needle)) |index| {
        count += 1;
        cursor = index + needle.len;
    }
    return count;
}

test "direct checker keeps success output behind clean issue collection" {
    const checker_source = try readRepoFile(testing.allocator, "scripts/zigux/check-phase2-cross.py");
    defer testing.allocator.free(checker_source);

    try expectContains(checker_source, "issues = collect_issues(args.root.resolve())");
    try expectContains(checker_source, "if issues:");
    try expectContains(checker_source, "return emit_issues(issues)");
    try expectContains(checker_source, "PHASE2_DIRECT_CROSS_ROUTE=pass");
    try expectContains(checker_source, "PHASE2_DIRECT_CROSS_ROUTE_TARGET_COUNT={len(cross_targets)}");
    try expectContains(checker_source, "PHASE2_DIRECT_CROSS_ROUTE_ARCHIVE_SCOPE_COUNT={len(load_archive_target_scope(args.root.resolve()))}");
    try expectOrdered(checker_source, "issues = collect_issues(args.root.resolve())", "PHASE2_DIRECT_CROSS_ROUTE=pass");
    try expectOrdered(checker_source, "return emit_issues(issues)", "PHASE2_DIRECT_CROSS_ROUTE=pass");
}

test "success counts are sourced from the live fixture and policy scope" {
    const checker_source = try readRepoFile(testing.allocator, "scripts/zigux/check-phase2-cross.py");
    defer testing.allocator.free(checker_source);

    try expectContains(checker_source, "fixture = read_json(resolve_path(args.root.resolve(), FIXTURE))");
    try expectContains(checker_source, "cross_targets = fixture.get(\"cross_targets\")");
    try expectContains(checker_source, "assert isinstance(cross_targets, list)");
    try expectContains(checker_source, "load_archive_target_scope(args.root.resolve())");
    try expectContains(checker_source, "archive_target_scope = upgrade_policy.get(\"archive_target_scope\")");
    try expectContains(checker_source, "duplicate archive_target_scope entry");
}

test "fixture remains the current two-target success boundary" {
    const fixture_source = try readRepoFile(testing.allocator, "zigux/tests/fixtures/phase2_cross_targets.json");
    defer testing.allocator.free(fixture_source);

    try expectContains(fixture_source, "\"phase\": \"Phase 2\"");
    try expectContains(fixture_source, "\"status\": \"active\"");
    try expectContains(fixture_source, "\"route\": \"make -C zigux phase2-cross\"");
    try expectContains(fixture_source, "\"archive_target_scope\"");
    try expectContains(fixture_source, "\"target\": \"x86_64-linux\"");
    try expectContains(fixture_source, "\"review_status\": \"pinned bootstrap archive\"");
    try expectContains(fixture_source, "\"validation_mode\": \"archive_required\"");
    try expectContains(fixture_source, "\"target\": \"aarch64-linux\"");
    try expectContains(fixture_source, "\"review_status\": \"route contract only\"");
    try expectContains(fixture_source, "\"validation_mode\": \"route_contract_only\"");
    try expectAbsent(fixture_source, "riscv64");

    try testing.expectEqual(@as(usize, 3), countOccurrences(fixture_source, "make -C zigux phase2-cross"));
    try testing.expectEqual(@as(usize, 2), countOccurrences(fixture_source, "\"target\""));
}

test "policy and Makefile expose the success-count route inputs once" {
    const policy_source = try readRepoFile(testing.allocator, "scripts/zigux/zig-toolchain-policy.json");
    defer testing.allocator.free(policy_source);
    const makefile_source = try readRepoFile(testing.allocator, "zigux/Makefile");
    defer testing.allocator.free(makefile_source);

    try expectContains(policy_source, "\"archive_target_scope\"");
    try expectContains(policy_source, "\"x86_64-linux\"");
    try expectContains(policy_source, "\"phase2-cross\"");
    try expectContains(makefile_source, "phase2-cross:");
    try expectContains(makefile_source, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py --self-test");
    try expectContains(makefile_source, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py");

    try testing.expectEqual(@as(usize, 1), countOccurrences(policy_source, "\"phase2-cross\""));
    try testing.expectEqual(@as(usize, 1), countOccurrences(makefile_source, "phase2-cross:"));
    try testing.expectEqual(@as(usize, 1), countOccurrences(makefile_source, "check-phase2-cross.py --self-test"));
    try testing.expectEqual(@as(usize, 1), countOccurrences(makefile_source, "check-phase2-cross.py\n"));
}
