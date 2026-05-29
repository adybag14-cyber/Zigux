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

const rooted_files = [_][]const u8{
    "scripts/zigux/zig-toolchain-policy.json",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
};

fn readRooted(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.Options.debug_io, path, allocator, .limited(256 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase2 toolchain pin scope keeps policy, checker, workflow, and make routes aligned" {
    const allocator = std.testing.allocator;

    var opened_files: usize = 0;
    inline for (rooted_files) |path| {
        const content = try readRooted(allocator, path);
        defer allocator.free(content);
        try std.testing.expect(content.len > 0);
        opened_files += 1;
    }
    try std.testing.expectEqual(rooted_files.len, opened_files);

    const policy = try readRooted(allocator, "scripts/zigux/zig-toolchain-policy.json");
    defer allocator.free(policy);
    const pin_scope = try readRooted(allocator, "scripts/zigux/check-phase2-toolchain-pin-scope.py");
    defer allocator.free(pin_scope);
    const workflow = try readRooted(allocator, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow);
    const makefile = try readRooted(allocator, "zigux/Makefile");
    defer allocator.free(makefile);

    try expectContains(policy, "\"phase\": \"Phase 2\"");
    try expectContains(policy, "\"channel_minimum_lockstep\": true");
    try expectContains(policy, "\"archive_target_scope\": [\n      \"x86_64-linux\"\n    ]");
    try expectContains(policy, "\"x86_64-linux\": \"313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77\"");

    try expectContains(pin_scope, "EXPECTED_PHASE = \"Phase 2\"");
    try expectContains(pin_scope, "EXPECTED_TARGETS = [\"x86_64-linux\"]");
    try expectContains(pin_scope, "SHA256_RE = re.compile(r\"^[0-9a-f]{64}$\")");
    try expectContains(pin_scope, "ZIG_PINNED_TARGET := $(shell $(PYTHON) -c ");
    try expectContains(pin_scope, "run: make -C zigux phase2-toolchain");

    try expectContains(workflow, "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only");
    try expectContains(workflow, "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing");
    try expectContains(workflow, "run: make -C zigux phase2-toolchain");
    try expectContains(workflow, "run: make -C zigux phase2");

    try expectContains(makefile, "ZIG_PINNED_TARGET := $(shell $(PYTHON) -c ");
    try expectContains(makefile, "ZIG_PINNED_TOOLCHAIN := $(if $(ZIG_PINNED_EXECUTABLE),$(ZIG_PINNED_EXECUTABLE),$(ZIG_LOCAL_TOOLCHAIN))");
    try expectContains(makefile, "ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)");

    inline for (required_routes) |route| {
        try expectContains(policy, route);
        try expectContains(pin_scope, route);
        try expectContains(workflow, route);
        try expectContains(makefile, route);
    }
}
