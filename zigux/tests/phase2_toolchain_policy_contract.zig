const std = @import("std");
const testing = std.testing;

fn expectContains(policy_json: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, policy_json, needle) != null);
}

fn expectJsonString(policy_json: []const u8, value: []const u8) !void {
    var token: [160]u8 = undefined;
    const quoted = try std.fmt.bufPrint(&token, "\"{s}\"", .{value});
    try expectContains(policy_json, quoted);
}

test "phase2 toolchain policy keeps pinned archive and action routes explicit" {
    const policy_json = try std.Io.Dir.cwd().readFileAlloc(
        testing.io,
        "scripts/zigux/zig-toolchain-policy.json",
        testing.allocator,
        .limited(16 * 1024),
    );
    defer testing.allocator.free(policy_json);

    try expectContains(policy_json, "\"phase\": \"Phase 2\"");
    try expectContains(policy_json, "\"channel\": \"0.17.0-dev.87+9b177a7d2\"");
    try expectContains(policy_json, "\"minimum_version\": \"0.17.0-dev.87+9b177a7d2\"");
    try expectContains(policy_json, "\"x86_64-linux\": \"313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77\"");
    try expectContains(policy_json, "\"channel_minimum_lockstep\": true");

    try expectJsonString(policy_json, "x86_64-linux");

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
        try expectJsonString(policy_json, route);
    }
}
