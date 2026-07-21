const std = @import("std");

fn readRepoFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(1024 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "Phase 15 validator covers replay and approval boundaries" {
    const validator = try readRepoFile("scripts/zigux/validate_phase15.zig");
    defer std.testing.allocator.free(validator);
    for ([_][]const u8{
        "Documentation/zigux/phase15-route-recovery.md",
        "zigux/Makefile",
        ".github/workflows/zigux-bootstrap.yml",
        "zigux/tests/phase15_build.zig",
        "PHASE15_ROUTE_RECOVERY_NO_APPROVAL_CLAIM=true",
        "PHASE15_FREEZE_MAP_STATUS_CHANGE=false",
    }) |marker| try expectContains(validator, marker);
}

test "Phase 15 Makefile validates route recovery before aggregate validation" {
    const makefile = try readRepoFile("zigux/Makefile");
    defer std.testing.allocator.free(makefile);
    const recovery = std.mem.indexOf(u8, makefile, "check_phase15_blocked_route_recovery.zig") orelse return error.MissingRecoveryChecker;
    const validator = std.mem.indexOf(u8, makefile, "validate_phase15.zig -- --self-test") orelse return error.MissingValidator;
    try std.testing.expect(recovery < validator);
}
