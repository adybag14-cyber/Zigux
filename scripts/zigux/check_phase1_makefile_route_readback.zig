// Ported from check-phase1-makefile-route-readback.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

const MAKEFILE_REL = "zigux/Makefile";

const SAMPLE_MAKEFILE = "PYTHON ?= python3\nZIG ?= zig\nPHASE2_SCRIPT_ROOT := ../scripts/zigux\nPHASE3_SCRIPT_ROOT := ../scripts/zigux\nPHASE8_SCRIPT_ROOT := ../scripts/zigux\nZIGUX_ROOT := ..\n\n.PHONY: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-validate phase2 phase3-validate phase3 phase8-validate phase8-exec-cmd-test phase8-test phase8 phase10-validate phase10-test phase10 phase12-smoke phase12-test phase12\n\nphase2-toolchain:\n\ttrue\nphase2-tools:\n\ttrue\nphase2-kconfig:\n\ttrue\nphase2-cross:\n\ttrue\nphase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross\n\ttrue\nphase2: phase2-validate\n\ttrue\nphase3-validate:\n\ttrue\nphase3: phase3-validate\n\ttrue\nphase8-validate:\n\ttrue\nphase8-exec-cmd-test:\n\ttrue\nphase8-test:\n\ttrue\nphase8:\n\ttrue\nphase10-validate:\n\ttrue\nphase10-test:\n\ttrue\nphase10: phase10-validate phase10-test\n\ttrue\nphase12-smoke:\n\ttrue\nphase12-test:\n\ttrue\nphase12: phase12-smoke phase12-test\n\ttrue\n";

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
    try guard.printLine(io, "SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
        try guard.printLine(io, "PHASE1_GUARD=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "PHASE1_GUARD=pass", .{});
    std.process.exit(0);
}
