const std = @import("std");

const required_routes = [_][]const u8{
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrderedAfter(haystack: []const u8, needle: []const u8, previous_index: *usize) !void {
    const relative_index = std.mem.indexOfPos(u8, haystack, previous_index.*, needle) orelse return error.MissingMarker;
    previous_index.* = relative_index + needle.len;
}

fn expectExactlyOnce(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), std.mem.count(u8, haystack, needle));
}

fn expectMakeTarget(haystack: []const u8, route: []const u8) !void {
    const start_marker = try std.fmt.allocPrint(std.testing.allocator, "{s}:", .{route});
    defer std.testing.allocator.free(start_marker);
    if (std.mem.startsWith(u8, haystack, start_marker)) return;

    const line_marker = try std.fmt.allocPrint(std.testing.allocator, "\n{s}:", .{route});
    defer std.testing.allocator.free(line_marker);
    try expectContains(haystack, line_marker);
}

fn readFixture(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(2 * 1024 * 1024));
}

test "toolchain policy keeps the pinned channel, target, and trusted digest lockstep" {
    const policy = try readFixture(std.testing.allocator, "scripts/zigux/zig-toolchain-policy.json");
    defer std.testing.allocator.free(policy);

    try expectContains(policy, "\"phase\": \"Phase 2\"");
    try expectContains(policy, "\"channel\": \"0.17.0-dev.758+748e7c5e3\"");
    try expectContains(policy, "\"minimum_version\": \"0.17.0-dev.758+748e7c5e3\"");
    try expectContains(policy, "\"x86_64-linux\": \"0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6\"");
    try expectContains(policy, "\"channel_minimum_lockstep\": true");
    try expectContains(policy, "\"archive_target_scope\": [\n      \"x86_64-linux\"\n    ]");
}

test "toolchain policy required routes stay complete and ordered" {
    const policy = try readFixture(std.testing.allocator, "scripts/zigux/zig-toolchain-policy.json");
    defer std.testing.allocator.free(policy);

    var cursor: usize = 0;
    try expectOrderedAfter(policy, "\"required_make_routes\": [", &cursor);
    for (required_routes) |route| {
        const marker = try std.fmt.allocPrint(std.testing.allocator, "\"{s}\"", .{route});
        defer std.testing.allocator.free(marker);
        try expectOrderedAfter(policy, marker, &cursor);
        try expectExactlyOnce(policy, marker);
    }
}

test "required policy routes have Makefile targets and workflow make gates" {
    const makefile = try readFixture(std.testing.allocator, "zigux/Makefile");
    defer std.testing.allocator.free(makefile);
    const workflow = try readFixture(std.testing.allocator, ".github/workflows/zigux-bootstrap.yml");
    defer std.testing.allocator.free(workflow);

    for (required_routes) |route| {
        try expectMakeTarget(makefile, route);

        const workflow_gate = try std.fmt.allocPrint(std.testing.allocator, "run: make -C zigux {s}", .{route});
        defer std.testing.allocator.free(workflow_gate);
        try expectExactlyOnce(workflow, workflow_gate);
    }

    try expectExactlyOnce(workflow, "run: make -C zigux phase2\n");
}
