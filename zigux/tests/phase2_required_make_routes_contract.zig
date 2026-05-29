const std = @import("std");
const testing = std.testing;

const required_make_routes = [_][]const u8{
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectJsonString(policy_json: []const u8, value: []const u8) !void {
    var token: [160]u8 = undefined;
    const quoted = try std.fmt.bufPrint(&token, "\"{s}\"", .{value});
    try expectContains(policy_json, quoted);
}

fn expectFormatted(comptime fmt: []const u8, args: anytype, haystack: []const u8) !void {
    var token: [192]u8 = undefined;
    const needle = try std.fmt.bufPrint(&token, fmt, args);
    try expectContains(haystack, needle);
}

fn readRepoFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        testing.io,
        path,
        testing.allocator,
        .limited(256 * 1024),
    );
}

test "phase2 required make routes stay wired through policy workflow and makefile" {
    const policy_json = try readRepoFile("scripts/zigux/zig-toolchain-policy.json");
    defer testing.allocator.free(policy_json);
    const workflow_yaml = try readRepoFile(".github/workflows/zigux-bootstrap.yml");
    defer testing.allocator.free(workflow_yaml);
    const makefile = try readRepoFile("zigux/Makefile");
    defer testing.allocator.free(makefile);

    try expectContains(policy_json, "\"required_make_routes\"");
    try expectContains(workflow_yaml, "run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test");
    try expectContains(workflow_yaml, "run: python3 scripts/zigux/check-phase2-required-make-routes.py");
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py --self-test");
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py");
    try expectContains(makefile, "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep");
    try expectContains(makefile, "phase2: phase2-validate");

    for (required_make_routes) |route| {
        try expectJsonString(policy_json, route);
        try expectFormatted("run: make -C zigux {s}", .{route}, workflow_yaml);
        try expectFormatted("{s}:", .{route}, makefile);
    }
}
