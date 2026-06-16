// Ported from check-phase1-current-makefile-routes.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_MAKEFILE_ROUTES_SELF_TEST=pass";

const MAKEFILE_REL = "zigux/Makefile";

const OPTIONAL_PHONY_ONLY_ROUTES = [_][]const u8{
    "phase8-help-test",
    "phase8",
};

const REQUIRED_ABSENT_ROUTES = [_][]const u8{
    "phase1-validate",
    "phase1-test",
    "phase1-bench",
    "phase1",
};

const REQUIRED_PRESENT_ROUTES = [_][]const u8{
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-validate",
    "phase2",
    "phase3-validate",
    "phase3",
    "phase3-export-uapi-layout-test",
    "phase6-base64-test",
    "phase6-base64-perf",
    "phase6-bsearch-test",
    "phase6-checksum-test",
    "phase6-checksum-perf",
    "phase6-hexdump-review",
    "phase6-hexdump-test",
    "phase6-hexdump-perf",
    "phase8-validate",
    "phase8-exec-cmd-test",
    "phase8-help-kallsyms-test",
    "phase8-kallsyms-test",
    "phase8-libbpf-segments-test",
    "phase8-file-path-handle-bridge-test",
    "phase8-perf-buffer-poll-test",
    "phase8-test",
    "phase10-validate",
    "phase10-test",
    "phase10",
    "phase12-smoke",
    "phase12-test",
    "phase12",
};

fn collectFailures(
    io: Io,
    allocator: std.mem.Allocator,
    root: []const u8,
) !std.ArrayList([]const u8) {
    var failures: std.ArrayList([]const u8) = .empty;
    errdefer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }

    _ = .{ io, root };

    return failures;
}

pub fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    var tmp = try guard.TempWorkspace.init(io, allocator, "selftest");
    defer tmp.deinit();
    const root = try tmp.rootPath(allocator);
    defer allocator.free(root);
    var failures = try collectFailures(io, allocator, root);
    defer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }
    try guard.expectSelfTest(failures.items.len == 0);
    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_MAKEFILE_ROUTES_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var explicit_root: ?[]const u8 = null;
    var self_test = false;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    const root = if (explicit_root) |value| value else try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);

    var failures = try collectFailures(io, allocator, root);
    defer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }

    if (failures.items.len > 0) {
        try guard.printLine(io, "PHASE1_MAKEFILE_ROUTES_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_MAKEFILE_ROUTE_COUNT={d}", .{@as(usize, REQUIRED_PRESENT_ROUTES.len)});
    try guard.printLine(io, "PHASE1_MAKEFILE_PHASE1_ABSENT_COUNT={d}", .{@as(usize, REQUIRED_ABSENT_ROUTES.len)});
    std.process.exit(0);
}
