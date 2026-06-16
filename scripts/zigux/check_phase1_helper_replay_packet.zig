// Ported from check-phase1-helper-replay-packet.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_HELPER_REPLAY_PACKET_SELF_TEST=pass";

const MARKERS_ENTRIES = [_]struct { file: []const u8, marker: []const u8 }{
    .{ .file = "Documentation/zigux/phase1-closure.md", .marker = "- `zigux/tests/phase1_helpers.zig`" },
    .{ .file = "Documentation/zigux/phase1-closure.md", .marker = "- `zigux/tests/phase1_helpers_build.zig`" },
    .{ .file = "Documentation/zigux/phase1-closure.md", .marker = "- `zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig`" },
    .{ .file = "scripts/zigux/README.md", .marker = "- `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `zigux/tests/build.zig`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_helpers_build.zig`, and `zigux/tests/phase1_host_tools_smoke.zig` remain the current reminder-surface companions for that packet" },
    .{ .file = "scripts/zigux/README.md", .marker = "- `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_helpers_build.zig`, and `zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig` restore a focused fixture-backed helper replay anchor on current `master` without widening back into the older validator-first or bench-route stack" },
    .{ .file = "zigux/tests/README.md", .marker = "- `zigux/tests/phase1_helpers.zig`" },
    .{ .file = "zigux/tests/README.md", .marker = "- `zigux/tests/phase1_helpers_build.zig`" },
    .{ .file = "zigux/tests/README.md", .marker = "* current focused Phase 1 helper replay route: `zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig`" },
    .{ .file = "zigux/tests/phase1_helpers_build.zig", .marker = ".root_source_file = b.path(\"phase1_helpers.zig\")," },
    .{ .file = "zigux/tests/phase1_helpers_build.zig", .marker = ".name = \"phase1-helpers\"," },
    .{ .file = "zigux/tests/phase1_helpers_build.zig", .marker = "root_module.addImport(\"bitmap\", bitmap_module);" },
    .{ .file = "zigux/tests/phase1_helpers_build.zig", .marker = "root_module.addImport(\"find_bit\", find_bit_module);" },
    .{ .file = "zigux/tests/phase1_helpers_build.zig", .marker = "root_module.addImport(\"rbtree\", rbtree_module);" },
    .{ .file = "zigux/tests/phase1_helpers_build.zig", .marker = "root_module.addImport(\"string\", string_module);" },
    .{ .file = "zigux/tests/phase1_helpers.zig", .marker = "const fixture_bytes = @embedFile(\"fixtures/phase1_helpers.json\");" },
    .{ .file = "zigux/tests/phase1_helpers.zig", .marker = "const bitmap = @import(\"bitmap\");" },
    .{ .file = "zigux/tests/phase1_helpers.zig", .marker = "const find_bit = @import(\"find_bit\");" },
    .{ .file = "zigux/tests/phase1_helpers.zig", .marker = "const rbtree = @import(\"rbtree\");" },
    .{ .file = "zigux/tests/phase1_helpers.zig", .marker = "const string = @import(\"string\");" },
    .{ .file = "zigux/tests/phase1_helpers.zig", .marker = "test \"phase 1 helper ports match committed parity fixture\" {" },
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

    for (REQUIRED_FILES) |relative_path| {
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            try guard.appendMissingFileIssue(allocator, &failures, relative_path);
        }
    }
    if (failures.items.len > 0) return failures;

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
    try guard.printLine(io, "PHASE1_GUARD_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
        try guard.printLine(io, "PHASE1_HELPER_REPLAY_PACKET_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    std.process.exit(0);
}

