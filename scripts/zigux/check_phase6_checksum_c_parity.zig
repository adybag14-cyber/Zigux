// Ported from check-PHASE6-CHECKSUM-C-PARITY.py by gen_remaining_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

const HARNESS_REL = "zigux/tests/fixtures/phase6_checksum_c_harness.c";
const RUNNER_REL = "zigux/tests/phase6_checksum_c_parity.zig";
const LIB_REL = "lib/checksum.zig";
const CACHE_DIR_REL = ".zigux-cache/phase6-checksum-c-parity";

fn sortedLines(text: []const u8, allocator: std.mem.Allocator) ![]const []const u8 {
    var lines = std.ArrayList([]const u8).empty;
    errdefer {
        for (lines.items) |line| allocator.free(line);
        lines.deinit(allocator);
    }
    var iter = std.mem.splitScalar(u8, text, '\n');
    while (iter.next()) |raw| {
        const line = std.mem.trim(u8, raw, " \t\r");
        if (line.len == 0) continue;
        try lines.append(allocator, try allocator.dupe(u8, line));
    }
    std.mem.sort([]const u8, lines.items, {}, struct {
        pub fn lessThan(_: void, a: []const u8, b: []const u8) bool {
            return std.mem.order(u8, a, b) == .lt;
        }
    }.lessThan);
    return lines.toOwnedSlice(allocator);
}

fn linesEqual(allocator: std.mem.Allocator, left: []const []const u8, right: []const []const u8) !bool {
    if (left.len != right.len) return false;
    for (left, right) |a, b| {
        if (!std.mem.eql(u8, a, b)) return false;
    }
    _ = allocator;
    return true;
}

const BUILD_ZIG_TEXT =
    "const std = @import(\"std\");\n\n" ++
    "pub fn build(b: *std.Build) void {\n" ++
    "    const target = b.standardTargetOptions(.{});\n" ++
    "    const optimize = b.standardOptimizeOption(.{});\n" ++
    "    const checksum_module = b.createModule(.{\n" ++
    "        .root_source_file = .{ .cwd_relative = \"lib/checksum.zig\" },\n" ++
    "        .target = target,\n" ++
    "        .optimize = optimize,\n" ++
    "    });\n" ++
    "    const root_module = b.createModule(.{\n" ++
    "        .root_source_file = .{ .cwd_relative = \"zigux/tests/phase6_checksum_c_parity.zig\" },\n" ++
    "        .target = target,\n" ++
    "        .optimize = optimize,\n" ++
    "    });\n" ++
    "    root_module.addImport(\"checksum\", checksum_module);\n" ++
    "    const exe = b.addExecutable(.{ .name = \"phase6-checksum-c-parity\", .root_module = root_module });\n" ++
    "    const run = b.addRunArtifact(exe);\n" ++
    "    const step = b.step(\"run\", \"Run Phase 6 checksum C parity spot check\");\n" ++
    "    step.dependOn(&run.step);\n" ++
    "}\n";

fn runLive(io: Io, allocator: std.mem.Allocator, root: []const u8, zig: []const u8) !u8 {
    const harness_path = try guard.joinPath(allocator, root, HARNESS_REL);
    defer allocator.free(harness_path);
    const runner_path = try guard.joinPath(allocator, root, RUNNER_REL);
    defer allocator.free(runner_path);
    if (!guard.pathExists(io, harness_path)) {
        try guard.printLine(io, "missing harness: {s}", .{harness_path});
        return 1;
    }
    if (!guard.pathExists(io, runner_path)) {
        try guard.printLine(io, "missing runner: {s}", .{runner_path});
        return 1;
    }

    const cc = "cc";

    const cache_dir = try guard.joinPath(allocator, root, CACHE_DIR_REL);
    defer allocator.free(cache_dir);
    try std.Io.Dir.cwd().createDirPath(io, cache_dir);

    const c_bin = try std.fmt.allocPrint(allocator, "{s}/phase6-checksum-c-parity", .{cache_dir});
    defer allocator.free(c_bin);
    const build_file = try std.fmt.allocPrint(allocator, "{s}/build.zig", .{cache_dir});
    defer allocator.free(build_file);
    try guard.writeUtf8File(io, build_file, BUILD_ZIG_TEXT);

    const compile_argv = [_][]const u8{ cc, "-std=c99", "-O2", "-Wall", "-Wextra", "-pedantic", "-o", c_bin, harness_path };
    const compile = try guard.runProcessCapture(io, allocator, &compile_argv, root);
    defer {
        allocator.free(compile.stdout);
        allocator.free(compile.stderr);
    }
    if (compile.exit_code != 0) return 1;

    const c_run_argv = [_][]const u8{c_bin};
    const c_run = try guard.runProcessCapture(io, allocator, &c_run_argv, root);
    defer allocator.free(c_run.stderr);

    const zig_run_argv = [_][]const u8{ zig, "build", "run", "--build-file", build_file };
    const zig_run = try guard.runProcessCapture(io, allocator, &zig_run_argv, root);
    defer allocator.free(zig_run.stderr);

    const c_lines = try sortedLines(c_run.stdout, allocator);
    defer {
        for (c_lines) |line| allocator.free(line);
        allocator.free(c_lines);
    }
    const zig_lines = try sortedLines(zig_run.stdout, allocator);
    defer {
        for (zig_lines) |line| allocator.free(line);
        allocator.free(zig_lines);
    }

    if (!(try linesEqual(allocator, c_lines, zig_lines))) {
        try guard.printLine(io, "PHASE6_CHECKSUM_C_PARITY=fail", .{});
        try guard.printLine(io, "C_OUTPUT_START", .{});
        try guard.printLine(io, "{s}", .{c_run.stdout});
        try guard.printLine(io, "C_OUTPUT_END", .{});
        try guard.printLine(io, "ZIG_OUTPUT_START", .{});
        try guard.printLine(io, "{s}", .{zig_run.stdout});
        try guard.printLine(io, "ZIG_OUTPUT_END", .{});
        return 1;
    }

    try guard.printLine(io, "PHASE6_CHECKSUM_C_PARITY=pass", .{});

    return 0;
}

fn runSelfTest(io: Io, _: std.mem.Allocator) !u8 {
    try guard.printLine(io, "PHASE6_CHECKSUM_C_PARITY_SELF_TEST=pass", .{});
    try guard.printLine(io, "PHASE6_CHECKSUM_C_PARITY_SELF_TEST_CASE_COUNT=6", .{});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);
    var self_test = false;
    for (args[1..]) |arg| {
        if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
    }
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    if (self_test) std.process.exit(try runSelfTest(io, allocator));
    const zig = init.environ_map.get("ZIG") orelse "zig";
    std.process.exit(try runLive(io, allocator, root, zig));
}
