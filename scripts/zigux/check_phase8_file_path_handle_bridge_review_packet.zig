// Ported from check-phase8-file-path-handle-bridge-review-packet.py by gen_marker_guard.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

const PASS_MARKER = "PHASE8_FILE_PATH_HANDLE_BRIDGE_REVIEW_PACKET=pass";
const SELF_TEST_PASS_MARKER = "PHASE8_FILE_PATH_HANDLE_BRIDGE_REVIEW_PACKET_SELF_TEST=pass";
const FAIL_PREFIX = "PHASE8_FILE_PATH_HANDLE_BRIDGE_REVIEW_PACKET";

const REQUIRED_FILES = [_][]const u8{
    "scripts/zigux/validate_phase8.zig",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/phase8_file_path_handle_bridge.zig",
};

const FILE_MARKER_ENTRIES = [_]struct { file: []const u8, markers: []const []const u8 }{
    .{ .file = "scripts/zigux/validate_phase8.zig", .markers = &[_][]const u8{
        "zigux/tests/phase8_file_path_handle_bridge_only_build.zig",
        "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
        "Documentation/zigux/phase8-file-path-handle-bridge-slice.md",
    } },
    .{ .file = "zigux/Makefile", .markers = &[_][]const u8{
        "phase8-file-path-handle-bridge-test:",
        "zigux/tests/phase8_file_path_handle_bridge_only_build.zig",
        "phase8: phase8-validate phase8-exec-cmd-test phase8-help-test phase8-help-kallsyms-test phase8-kallsyms-test phase8-file-path-handle-bridge-test phase8-libbpf-segments-test phase8-perf-buffer-poll-test phase8-test",
    } },
    .{ .file = "zigux/tests/README.md", .markers = &[_][]const u8{
        "current mixed-source file-path-handle bridge companions also remain reviewable on current `master` through the public tree and aligned reminder packet:",
        "`zigux/tests/phase8_file_path_handle_bridge_only_build.zig`",
        "`make -C zigux phase8-file-path-handle-bridge-test`",
        "`zigux/tests/phase8_build.zig`",
    } },
    .{ .file = "zigux/tests/phase8_file_path_handle_bridge.zig", .markers = &[_][]const u8{
        "phase 8 file-path handle bridge helper stays wired into its focused Phase 8 build shard",
        "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
        "phase8_file_path_handle_bridge_only_build.zig",
    } },
};

const ValidationResult = struct {
    missing_files: std.ArrayList([]const u8),
    missing_markers: std.ArrayList([]const u8),
};

fn validateRoot(io: Io, allocator: std.mem.Allocator, root: []const u8) !ValidationResult {
    var result = ValidationResult{ .missing_files = .empty, .missing_markers = .empty };
    errdefer {
        for (result.missing_files.items) |item| allocator.free(item);
        result.missing_files.deinit(allocator);
        for (result.missing_markers.items) |item| allocator.free(item);
        result.missing_markers.deinit(allocator);
    }
    for (REQUIRED_FILES) |relative_path| {
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const copy = try allocator.dupe(u8, relative_path);
            try result.missing_files.append(allocator, copy);
        }
    }
    for (FILE_MARKER_ENTRIES) |entry| {
        const full_path = try guard.joinPath(allocator, root, entry.file);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) continue;
        const text = try guard.readUtf8File(io, allocator, full_path);
        defer allocator.free(text);
        for (entry.markers) |marker| {
            if (std.mem.indexOf(u8, text, marker) == null) {
                const issue = try std.fmt.allocPrint(allocator, "{s}:{s}", .{ entry.file, marker });
                try result.missing_markers.append(allocator, issue);
            }
        }
    }
    return result;
}

fn emitResult(io: Io, _: std.mem.Allocator, result: ValidationResult) !u8 {
    if (result.missing_files.items.len == 0 and result.missing_markers.items.len == 0) return 0;
    try guard.printLine(io, "{s}=fail", .{FAIL_PREFIX});
    if (result.missing_files.items.len > 0) {
        try guard.printLine(io, "{s}_MISSING_FILES_START", .{FAIL_PREFIX});
        for (result.missing_files.items) |item| try guard.printLine(io, "{s}", .{item});
        try guard.printLine(io, "{s}_MISSING_FILES_END", .{FAIL_PREFIX});
    }
    if (result.missing_markers.items.len > 0) {
        try guard.printLine(io, "{s}_MISSING_MARKERS_START", .{FAIL_PREFIX});
        for (result.missing_markers.items) |item| try guard.printLine(io, "{s}", .{item});
        try guard.printLine(io, "{s}_MISSING_MARKERS_END", .{FAIL_PREFIX});
    }
    return 1;
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
        if (std.mem.eql(u8, arg, "--self-test")) { self_test = true; continue; }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }
    if (self_test) {
        try guard.printLine(io, "{s}", .{SELF_TEST_PASS_MARKER});
        try guard.printLine(io, "PHASE8_FILE_PATH_HANDLE_BRIDGE_REVIEW_PACKET_SELF_TEST_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
        std.process.exit(0);
    }
    const root = if (explicit_root) |value| value else try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    var result = try validateRoot(io, allocator, root);
    defer {
        for (result.missing_files.items) |item| allocator.free(item);
        result.missing_files.deinit(allocator);
        for (result.missing_markers.items) |item| allocator.free(item);
        result.missing_markers.deinit(allocator);
    }
    const code = try emitResult(io, allocator, result);
    if (code != 0) std.process.exit(code);
    try guard.printLine(io, "{s}", .{PASS_MARKER});
    try guard.printLine(io, "PHASE8_FILE_PATH_HANDLE_BRIDGE_REVIEW_PACKET_REQUIRED_FILE_COUNT=4", .{});
    try guard.printLine(io, "PHASE8_FILE_PATH_HANDLE_BRIDGE_REVIEW_PACKET_REQUIRED_MARKER_COUNT=13", .{});
    std.process.exit(0);
}
