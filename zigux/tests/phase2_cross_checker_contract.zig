const std = @import("std");
const testing = std.testing;

const checker_path = "scripts/zigux/check-phase2-cross.py";

const required_checker_markers = [_][]const u8{
    "Guard the rematerialized Phase 2 direct cross-route packet.",
    "TOOLCHAIN_POLICY = ROOT / \"scripts\" / \"zigux\" / \"zig-toolchain-policy.json\"",
    "MAKEFILE = ROOT / \"zigux\" / \"Makefile\"",
    "FIXTURE = ROOT / \"zigux\" / \"tests\" / \"fixtures\" / \"phase2_cross_targets.json\"",
    "ROUTE = \"make -C zigux phase2-cross\"",
    "EXPECTED_SELF_TEST_CASE_COUNT = 17",
    "PHASE2_DIRECT_CROSS_ROUTE=pass",
    "PHASE2_DIRECT_CROSS_ROUTE=fail",
    "PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST=pass",
    "PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST_CASE_COUNT={checks_run}",
    "PHASE2_DIRECT_CROSS_ROUTE_TARGET_COUNT={len(cross_targets)}",
    "PHASE2_DIRECT_CROSS_ROUTE_ARCHIVE_SCOPE_COUNT={len(load_archive_target_scope(args.root.resolve()))}",
};

const required_issue_codes = [_][]const u8{
    "MISSING_MAKEFILE_LINE",
    "DUPLICATE_MAKEFILE_LINE",
    "INVALID_FIXTURE_SHAPE",
    "INVALID_FIXTURE_FIELD",
    "ARCHIVE_SCOPE_MISMATCH",
    "INVALID_CROSS_TARGET_ENTRY",
    "DUPLICATE_CROSS_TARGET",
    "INVALID_CROSS_TARGET_ROUTE",
    "INVALID_CROSS_TARGET_MODE",
    "ARCHIVE_REQUIRED_TARGET_SET_MISMATCH",
};

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(testing.io, path, allocator, .limited(512 * 1024));
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, index, needle)) |found| {
        count += 1;
        index = found + needle.len;
    }
    return count;
}

fn expectContains(text: []const u8, marker: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, text, marker) != null);
}

fn expectOnce(text: []const u8, marker: []const u8) !void {
    try testing.expectEqual(@as(usize, 1), countOccurrences(text, marker));
}

fn expectOrdered(text: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, text, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, text, after) orelse return error.MissingAfterMarker;
    try testing.expect(before_index < after_index);
}

test "phase2 direct cross checker keeps route, files, and output markers explicit" {
    const checker = try readRepoFile(testing.allocator, checker_path);
    defer testing.allocator.free(checker);

    for (required_checker_markers) |marker| {
        try expectContains(checker, marker);
    }

    try expectOnce(checker, "phase2-cross:");
    try expectOnce(checker, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py");
    try expectOnce(checker, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py");
    try expectOrdered(checker, "phase2-cross:", "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py");
    try expectOrdered(
        checker,
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
    );
}

test "phase2 direct cross checker fail-closes known issue envelope" {
    const checker = try readRepoFile(testing.allocator, checker_path);
    defer testing.allocator.free(checker);

    for (required_issue_codes) |code| {
        try expectContains(checker, code);
    }

    try expectContains(checker, "print(f\"{code}_START\")");
    try expectContains(checker, "print(f\"{code}_END\")");

    try expectContains(checker, "duplicate archive_target_scope entry");
    try expectContains(checker, "required file missing");
    try expectContains(checker, "invalid archive_target_scope");
}

test "phase2 direct cross checker models the current two-target archive-scope packet" {
    const checker = try readRepoFile(testing.allocator, checker_path);
    defer testing.allocator.free(checker);

    try expectContains(checker, "archive_required");
    try expectContains(checker, "route_contract_only");
    try expectContains(checker, "pinned bootstrap archive");
    try expectContains(checker, "route contract only");
    try expectContains(checker, "x86_64-linux");
    try expectContains(checker, "aarch64-linux");
    try expectOrdered(checker, "x86_64-linux", "aarch64-linux");
}
