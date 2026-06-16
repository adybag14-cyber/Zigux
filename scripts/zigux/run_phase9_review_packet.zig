const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const self_test_pass_marker = "PHASE9_REVIEW_PACKET_SELF_TEST=pass";

const CHECKER_SCRIPTS = [_][]const u8{
    "scripts/zigux/check_phase9_review_checklist_phase_boundaries.zig",
    "scripts/zigux/check_phase9_freeze_map_study_boundaries.zig",
    "scripts/zigux/check_phase9_trace_events_runtime_packet.zig",
};

const ZIG_TESTS = [_][]const u8{
    "samples/zigux/runtime_trace_events.zig",
    "samples/zigux/runtime_trace_events_unregistered_gate.zig",
    "samples/zigux/runtime_trace_events_exit_rollback_guard.zig",
    "samples/zigux/runtime_trace_events_registration_reentry_gate.zig",
    "zigux/tests/runtime_trace_events_survey.zig",
};

fn pathsEqual(left: []const u8, right: []const u8) bool {
    if (std.mem.eql(u8, left, right)) return true;
    var left_norm: [512]u8 = undefined;
    var right_norm: [512]u8 = undefined;
    const left_len = normalizePath(&left_norm, left);
    const right_len = normalizePath(&right_norm, right);
    return left_len == right_len and std.mem.eql(u8, left_norm[0..left_len], right_norm[0..right_len]);
}

fn normalizePath(buffer: []u8, path: []const u8) usize {
    var out: usize = 0;
    for (path) |ch| {
        const normalized: u8 = if (ch == '\\') '/' else ch;
        buffer[out] = normalized;
        out += 1;
    }
    return out;
}

fn inferRepoRoot(io: Io, allocator: std.mem.Allocator) ![]const u8 {
    const root = try guard.repoRootFromScript(allocator);
    const marker_path = try guard.joinPath(allocator, root, "Documentation/zigux/review-checklist.md");
    defer allocator.free(marker_path);
    if (guard.pathExists(io, marker_path)) return root;
    allocator.free(root);
    return try guard.defaultRepoRoot(allocator);
}

fn buildCommandPlan(
    allocator: std.mem.Allocator,
    repo_root: []const u8,
    zig_bin: []const u8,
    checks_only: bool,
    commands: *std.ArrayList([]const []const u8),
) !void {
    for (CHECKER_SCRIPTS) |rel_path| {
        const script_path = try guard.joinPath(allocator, repo_root, rel_path);
        const argv = try allocator.alloc([]const u8, 3);
        argv[0] = "zig";
        argv[1] = "run";
        argv[2] = script_path;
        try commands.append(allocator, argv);
    }

    if (!checks_only) {
        for (ZIG_TESTS) |rel_path| {
            const test_path = try guard.joinPath(allocator, repo_root, rel_path);
            const argv = try allocator.alloc([]const u8, 3);
            argv[0] = zig_bin;
            argv[1] = "test";
            argv[2] = test_path;
            try commands.append(allocator, argv);
        }
    }
}

fn formatCommand(allocator: std.mem.Allocator, argv: []const []const u8) ![]const u8 {
    var parts: std.ArrayList([]const u8) = .empty;
    defer parts.deinit(allocator);
    for (argv) |arg| try parts.append(allocator, arg);
    return try std.mem.join(allocator, " ", parts.items);
}

fn runCommandPlan(io: Io, allocator: std.mem.Allocator, commands: []const []const []const u8, repo_root: []const u8) !u8 {
    for (commands) |argv| {
        const printable = try formatCommand(allocator, argv);
        defer allocator.free(printable);
        try guard.printLine(io, "PHASE9_REVIEW_PACKET_STEP={s}", .{printable});

        const output = try guard.runProcessCapture(io, allocator, argv, repo_root);
        defer allocator.free(output.stdout);
        defer allocator.free(output.stderr);
        if (output.exit_code != 0) {
            if (output.stderr.len != 0) {
                var stderr_buffer: [4096]u8 = undefined;
                var stderr_writer = Io.File.stderr().writer(io, &stderr_buffer);
                try stderr_writer.interface.writeAll(output.stderr);
                try stderr_writer.interface.flush();
            }
            return output.exit_code;
        }
    }
    return 0;
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const repo_root = "/tmp/zigux-phase9-review-packet-fixture";

    var full_commands: std.ArrayList([]const []const u8) = .empty;
    defer {
        for (full_commands.items) |argv| {
            allocator.free(argv[2]);
            allocator.free(argv);
        }
        full_commands.deinit(allocator);
    }
    try buildCommandPlan(allocator, repo_root, "zig-custom", false, &full_commands);

    try guard.expectSelfTest(full_commands.items.len == CHECKER_SCRIPTS.len + ZIG_TESTS.len);
    for (CHECKER_SCRIPTS, 0..) |rel_path, index| {
        const argv = full_commands.items[index];
        try guard.expectSelfTest(std.mem.eql(u8, argv[0], "zig"));
        try guard.expectSelfTest(std.mem.eql(u8, argv[1], "run"));
        const expected = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ repo_root, rel_path });
        defer allocator.free(expected);
        try guard.expectSelfTest(pathsEqual(argv[2], expected));
    }
    for (ZIG_TESTS, 0..) |rel_path, index| {
        const argv = full_commands.items[CHECKER_SCRIPTS.len + index];
        try guard.expectSelfTest(std.mem.eql(u8, argv[0], "zig-custom"));
        try guard.expectSelfTest(std.mem.eql(u8, argv[1], "test"));
        const expected = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ repo_root, rel_path });
        defer allocator.free(expected);
        try guard.expectSelfTest(pathsEqual(argv[2], expected));
    }

    var checks_only_commands: std.ArrayList([]const []const u8) = .empty;
    defer {
        for (checks_only_commands.items) |argv| {
            allocator.free(argv[2]);
            allocator.free(argv);
        }
        checks_only_commands.deinit(allocator);
    }
    try buildCommandPlan(allocator, repo_root, "zig-custom", true, &checks_only_commands);
    try guard.expectSelfTest(checks_only_commands.items.len == CHECKER_SCRIPTS.len);

    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    try guard.printLine(io, "PHASE9_REVIEW_PACKET_CHECKER_COUNT={d}", .{CHECKER_SCRIPTS.len});
    try guard.printLine(io, "PHASE9_REVIEW_PACKET_ZIG_TEST_COUNT={d}", .{ZIG_TESTS.len});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());

    var self_test = false;
    var checks_only = false;
    var dry_run = false;
    var repo_root: ?[]const u8 = null;
    var zig_bin: []const u8 = "zig";

    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--checks-only")) {
            checks_only = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--dry-run")) {
            dry_run = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            repo_root = args[index];
            continue;
        }
        if (std.mem.eql(u8, arg, "--zig")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            zig_bin = args[index];
            continue;
        }
        std.process.exit(2);
    }

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    const root = repo_root orelse try inferRepoRoot(io, allocator);
    defer if (repo_root == null) allocator.free(root);

    var commands: std.ArrayList([]const []const u8) = .empty;
    defer {
        for (commands.items) |argv| {
            allocator.free(argv[2]);
            allocator.free(argv);
        }
        commands.deinit(allocator);
    }
    try buildCommandPlan(allocator, root, zig_bin, checks_only, &commands);

    if (dry_run) {
        for (commands.items) |argv| {
            const printable = try formatCommand(allocator, argv);
            defer allocator.free(printable);
            try guard.printLine(io, "PHASE9_REVIEW_PACKET_PLAN={s}", .{printable});
        }
        return;
    }

    std.process.exit(try runCommandPlan(io, allocator, commands.items, root));
}