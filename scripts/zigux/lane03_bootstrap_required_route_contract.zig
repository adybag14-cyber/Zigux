const std = @import("std");

const required_make_routes = [_][]const u8{
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
};

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        std.testing.allocator,
        .limited(limit),
    );
}

fn countSubstring(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var rest = haystack;
    while (std.mem.indexOf(u8, rest, needle)) |index| {
        count += 1;
        rest = rest[index + needle.len ..];
    }
    return count;
}

fn countExactTrimmedLine(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, std.mem.trim(u8, line, " \t\r"), needle)) {
            count += 1;
        }
    }
    return count;
}

test "toolchain policy keeps the current required Phase 2 make-route roster" {
    const policy = try readRepoFile("scripts/zigux/zig-toolchain-policy.json", 16 * 1024);
    defer std.testing.allocator.free(policy);

    try std.testing.expectEqual(@as(usize, 1), countSubstring(policy, "\"channel\": \"0.17.0-dev.758+748e7c5e3\""));
    try std.testing.expectEqual(@as(usize, 1), countSubstring(policy, "\"minimum_version\": \"0.17.0-dev.758+748e7c5e3\""));
    try std.testing.expectEqual(@as(usize, 1), countSubstring(policy, "\"channel_minimum_lockstep\": true"));
    try std.testing.expectEqual(@as(usize, 1), countSubstring(policy, "\"x86_64-linux\": \"0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6\""));

    for (required_make_routes) |route| {
        var route_marker: [64]u8 = undefined;
        const marker = try std.fmt.bufPrint(&route_marker, "\"{s}\"", .{route});
        try std.testing.expectEqual(@as(usize, 1), countSubstring(policy, marker));
    }
}

test "bootstrap workflow carries every policy-required make route exactly once" {
    const workflow = try readRepoFile(".github/workflows/zigux-bootstrap.yml", 256 * 1024);
    defer std.testing.allocator.free(workflow);

    for (required_make_routes) |route| {
        var line_buf: [96]u8 = undefined;
        const line = try std.fmt.bufPrint(&line_buf, "run: make -C zigux {s}", .{route});
        try std.testing.expectEqual(@as(usize, 1), countExactTrimmedLine(workflow, line));
    }
}

test "bootstrap validator remains part of the current workflow packet" {
    const workflow = try readRepoFile(".github/workflows/zigux-bootstrap.yml", 256 * 1024);
    defer std.testing.allocator.free(workflow);

    try std.testing.expectEqual(
        @as(usize, 1),
        countExactTrimmedLine(workflow, "run: python3 scripts/zigux/validate-bootstrap.py --self-test"),
    );
    try std.testing.expectEqual(
        @as(usize, 1),
        countExactTrimmedLine(workflow, "run: python3 scripts/zigux/validate-bootstrap.py"),
    );
}
