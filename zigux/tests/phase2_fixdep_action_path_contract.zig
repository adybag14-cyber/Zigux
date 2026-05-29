const std = @import("std");

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1 << 24));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectLineCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, std.mem.trim(u8, line, " \t\r"), needle)) count += 1;
    }
    try std.testing.expectEqual(expected, count);
}

test "phase2 fixdep action path stays wired through bootstrap and make" {
    const allocator = std.testing.allocator;
    const workflow = try readRepoFile(allocator, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow);
    const makefile = try readRepoFile(allocator, "zigux/Makefile");
    defer allocator.free(makefile);

    try expectLineCount(workflow, "run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test", 1);
    try expectLineCount(workflow, "run: python3 scripts/zigux/check-phase2-fixdep-gate.py", 1);
    try expectLineCount(workflow, "run: python3 scripts/zigux/check-fixdep-diff.py --self-test", 1);
    try expectLineCount(workflow, "run: python3 scripts/zigux/check-fixdep-diff.py", 1);
    try expectLineCount(workflow, "run: zig test scripts/zigux/fixdep.zig", 1);
    try expectContains(makefile, "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py --self-test");
    try expectContains(makefile, "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py");
    try expectContains(makefile, "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --self-test");
    try expectContains(makefile, "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py");
}

test "phase2 fixdep action path stays visible in reminder surfaces" {
    const allocator = std.testing.allocator;
    const bootstrap_notes = try readRepoFile(allocator, "Documentation/zigux/phase2-toolchain-bootstrap-notes.md");
    defer allocator.free(bootstrap_notes);
    const scripts_readme = try readRepoFile(allocator, "scripts/zigux/README.md");
    defer allocator.free(scripts_readme);
    const tests_readme = try readRepoFile(allocator, "zigux/tests/README.md");
    defer allocator.free(tests_readme);
    const markers = [_][]const u8{
        "scripts/zigux/check-phase2-fixdep-gate.py",
        "scripts/zigux/check-fixdep-diff.py",
        "scripts/zigux/fixdep.zig",
    };

    inline for (markers) |marker| {
        try expectContains(tests_readme, marker);
    }

    try expectContains(bootstrap_notes, "zig test scripts/zigux/fixdep.zig");
    try expectContains(scripts_readme, "check-phase2-fixdep-gate.py");
    try expectContains(scripts_readme, "check-fixdep-diff.py");
}

test "phase2 aggregate routes still include fixdep before validation" {
    const allocator = std.testing.allocator;
    const makefile = try readRepoFile(allocator, "zigux/Makefile");
    defer allocator.free(makefile);

    try expectContains(makefile, "check-phase2-fixdep-gate.py --self-test");
    try expectContains(makefile, "check-fixdep-diff.py --self-test");
    try expectContains(makefile, "phase2-validate:");
    try expectContains(makefile, "phase2:");
}
