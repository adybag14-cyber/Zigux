const std = @import("std");

const rooted_files = [_][]const u8{
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
};

fn readRooted(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.Options.debug_io, path, allocator, .limited(512 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn contains(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

test "phase2 cross selftest alignment keeps direct route and fixture packet wired" {
    const allocator = std.testing.allocator;

    var opened_files: usize = 0;
    inline for (rooted_files) |path| {
        const content = try readRooted(allocator, path);
        defer allocator.free(content);
        try std.testing.expect(content.len > 0);
        opened_files += 1;
    }
    try std.testing.expectEqual(rooted_files.len, opened_files);

    const cross_checker = try readRooted(allocator, "scripts/zigux/check-phase2-cross.py");
    defer allocator.free(cross_checker);
    const alignment_checker = try readRooted(allocator, "scripts/zigux/check-phase2-cross-selftest-alignment.py");
    defer allocator.free(alignment_checker);
    const fixture = try readRooted(allocator, "zigux/tests/fixtures/phase2_cross_targets.json");
    defer allocator.free(fixture);
    const workflow = try readRooted(allocator, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow);
    const makefile = try readRooted(allocator, "zigux/Makefile");
    defer allocator.free(makefile);

    try expectContains(cross_checker, "FIXTURE = ROOT / \"zigux\" / \"tests\" / \"fixtures\" / \"phase2_cross_targets.json\"");
    try expectContains(cross_checker, "--self-test");
    try expectContains(cross_checker, "PHASE2_CROSS");

    try expectContains(alignment_checker, "check-phase2-cross.py");
    try expectContains(alignment_checker, "check-phase2-cross-selftest-alignment.py");
    try expectContains(alignment_checker, "phase2-cross");
    try expectContains(alignment_checker, "PHASE2_CROSS_ALIGNMENT_SELF_TEST_CASE_COUNT");

    try expectContains(fixture, "\"phase\": \"Phase 2\"");
    if (contains(fixture, "\"cross_targets\"")) {
        try expectContains(cross_checker, "ROUTE = \"make -C zigux phase2-cross\"");
        try expectContains(cross_checker, "EXPECTED_SELF_TEST_CASE_COUNT = 17");
        try expectContains(cross_checker, "ALLOWED_VALIDATION_MODES = (\"archive_required\", \"route_contract_only\")");
        try expectContains(alignment_checker, "CROSS_TARGETS = ROOT / \"zigux\" / \"tests\" / \"fixtures\" / \"phase2_cross_targets.json\"");
        try expectContains(fixture, "\"route\": \"make -C zigux phase2-cross\"");
        try expectContains(fixture, "\"archive_target_scope\": [\n    \"x86_64-linux\"\n  ]");
        try expectContains(fixture, "\"target\": \"x86_64-linux\"");
        try expectContains(fixture, "\"validation_mode\": \"archive_required\"");
        try expectContains(fixture, "\"target\": \"aarch64-linux\"");
        try expectContains(fixture, "\"validation_mode\": \"route_contract_only\"");
    } else {
        try expectContains(cross_checker, "EXPECTED_TARGETS = [");
        try expectContains(cross_checker, "EXPECTED_ZIG_TEST_FILES = [");
        try expectContains(alignment_checker, "PHASE2_CROSS_TARGET_HEADER = \"phase2-cross: phase2-toolchain\"");
        try expectContains(fixture, "\"targets\": [");
        try expectContains(fixture, "\"zig_test_files\": [");
    }

    try expectContains(workflow, "run: python3 scripts/zigux/check-phase2-cross.py --self-test");
    try expectContains(workflow, "scripts/zigux/check-phase2-cross.py");
    try expectContains(workflow, "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test");
    try expectContains(workflow, "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py");
    try expectContains(workflow, "phase2-cross");

    try expectContains(makefile, "phase2-cross");
    try expectContains(makefile, "check-phase2-cross.py");
    try expectContains(makefile, "check-phase2-cross-selftest-alignment.py");
}
