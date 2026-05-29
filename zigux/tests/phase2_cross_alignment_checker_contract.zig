const std = @import("std");
const testing = std.testing;

const checker_path = "scripts/zigux/check-phase2-cross-selftest-alignment.py";

fn readChecker(allocator: std.mem.Allocator) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, checker_path, allocator, .limited(1024 * 1024));
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn countContains(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, offset, needle)) |index| {
        count += 1;
        offset = index + needle.len;
    }
    return count;
}

test "phase2 cross alignment checker keeps required live packet files explicit" {
    const source = try readChecker(testing.allocator);
    defer testing.allocator.free(source);

    const required_paths = [_][]const u8{
        "Documentation/zigux/README.md",
        "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
        "Documentation/zigux/review-checklist.md",
        "zigux/tests/README.md",
        "scripts/zigux/README.md",
        "zigux/Makefile",
        "scripts/zigux/zig-toolchain-policy.json",
        "scripts/zigux/check-phase2-toolchain-pinning.py",
        "scripts/zigux/check-phase2-tests-readme-alignment.py",
        "zigux/tests/fixtures/phase2_cross_targets.json",
    };

    for (required_paths) |path| {
        try requireContains(source, path);
    }

    try requireContains(source, "required file missing");
    try requireContains(source, "invalid json in required file");
}

test "phase2 cross alignment checker preserves target and route contract" {
    const source = try readChecker(testing.allocator);
    defer testing.allocator.free(source);

    try requireContains(source, "SUPPORTED_CROSS_TARGETS = (\"x86_64-linux\", \"aarch64-linux\")");
    try requireContains(source, "ROUTE = \"make -C zigux phase2-cross\"");
    try requireContains(source, "archive_required");
    try requireContains(source, "route_contract_only");
    try requireContains(source, "unsupported archive_target_scope targets");
    try requireContains(source, "DUPLICATE_CROSS_TARGET_ENTRY");
    try requireContains(source, "INVALID_CROSS_TARGET_MATRIX");

    const required_make_routes = [_][]const u8{
        "phase2-toolchain",
        "phase2-tools",
        "phase2-kconfig",
        "phase2-cross",
        "phase2-genksyms",
        "phase2-fixdep",
        "phase2-validate",
    };

    for (required_make_routes) |route| {
        try testing.expect(countContains(source, route) >= 1);
    }
}

test "phase2 cross alignment checker keeps result markers and self-test envelope" {
    const source = try readChecker(testing.allocator);
    defer testing.allocator.free(source);

    const result_markers = [_][]const u8{
        "PHASE2_CROSS_ALIGNMENT_SELF_TEST=pass",
        "PHASE2_CROSS_ALIGNMENT_SELF_TEST_CASE_COUNT=",
        "PHASE2_CROSS_ALIGNMENT=pass",
        "PHASE2_CROSS_ALIGNMENT=fail",
        "PHASE2_CROSS_ALIGNMENT_MARKER_COUNT=",
        "PHASE2_CROSS_ALIGNMENT_ARCHIVE_SCOPE_COUNT=",
        "PHASE2_CROSS_ALIGNMENT_FIXTURE_TARGET_COUNT=",
    };

    for (result_markers) |marker| {
        try requireContains(source, marker);
    }

    try requireContains(source, "expected_case_count = (");
    try requireContains(source, "+ 19");
    try requireContains(source, "+ 10");
    try requireContains(source, "assert checks_run == expected_case_count");
}
