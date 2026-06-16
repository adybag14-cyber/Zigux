const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE8_FILE_PATH_HANDLE_BRIDGE_SCOPE=pass";
pub const self_test_pass_marker = "PHASE8_FILE_PATH_HANDLE_BRIDGE_SCOPE_SELF_TEST=pass";

const FDINFO_REQUIRED_HELPERS = [_][]const u8{
    "pub fn buildProcFdinfoPath",
    "pub fn parseFdinfoLine",
    "pub fn applyFdinfoMapInfoLine",
    "pub fn parseFdinfoMapInfo",
    "pub fn summarizeFdinfoMapInfo",
};

const FDINFO_REQUIRED_TEST_MARKERS = [_][]const u8{
    "buildProcFdinfoPath",
    "parseFdinfoMapInfo",
    "applyFdinfoMapInfoLine",
};

const MAP_REUSE_REQUIRED_HELPERS = [_][]const u8{
    "pub fn resolveReusedMapName",
    "pub fn summarizeMapReuseCompatibility",
    "pub fn isMapReuseCompatible",
};

const MAP_REUSE_REQUIRED_TEST_MARKERS = [_][]const u8{
    "resolveReusedMapName",
    "summarizeMapReuseCompatibility",
    "isMapReuseCompatible",
};

const PASSING_HELPER = [_][]const u8{
    "\npub fn buildProcFdinfoPath() void {}\npub fn parseFdinfoLine() void {}\npub fn applyFdinfoMapInfoLine() void {}\npub fn parseFdinfoMapInfo() void {}\npub fn summarizeFdinfoMapInfo() void {}\n",
};

const PASSING_TEST = [_][]const u8{
    "\ntest \"fdinfo\" {\n    _ = buildProcFdinfoPath;\n    _ = parseFdinfoMapInfo;\n    _ = applyFdinfoMapInfoLine;\n}\n",
};

const FAILING_HELPER = [_][]const u8{
    "\npub fn buildProcFdinfoPath() void {}\npub fn parseFdinfoLine() void {}\npub fn applyFdinfoMapInfoLine() void {}\npub fn parseFdinfoMapInfo() void {}\npub fn summarizeFdinfoMapInfo() void {}\n",
};

const FAILING_TEST = [_][]const u8{
    "\ntest \"fdinfo\" {\n    _ = buildProcFdinfoPath;\n    _ = parseFdinfoMapInfo;\n    _ = applyFdinfoMapInfoLine;\n}\n",
};

const FAILING_FDINFO_HELPER = [_][]const u8{
    "\npub fn buildProcFdinfoPath() void {}\npub fn applyFdinfoMapInfoLine() void {}\npub fn parseFdinfoMapInfo() void {}\npub fn summarizeFdinfoMapInfo() void {}\n",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_fdinfo_required_helpers_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig");
    defer allocator.free(text_fdinfo_required_helpers_path);
    const text_fdinfo_required_helpers = try guard.readUtf8File(io, allocator, text_fdinfo_required_helpers_path);
    defer allocator.free(text_fdinfo_required_helpers);
    for (FDINFO_REQUIRED_HELPERS) |marker| try guard.requireMarker(text_fdinfo_required_helpers, marker);
    const text_fdinfo_required_test_markers_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig");
    defer allocator.free(text_fdinfo_required_test_markers_path);
    const text_fdinfo_required_test_markers = try guard.readUtf8File(io, allocator, text_fdinfo_required_test_markers_path);
    defer allocator.free(text_fdinfo_required_test_markers);
    for (FDINFO_REQUIRED_TEST_MARKERS) |marker| try guard.requireMarker(text_fdinfo_required_test_markers, marker);
    const text_map_reuse_required_helpers_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig");
    defer allocator.free(text_map_reuse_required_helpers_path);
    const text_map_reuse_required_helpers = try guard.readUtf8File(io, allocator, text_map_reuse_required_helpers_path);
    defer allocator.free(text_map_reuse_required_helpers);
    for (MAP_REUSE_REQUIRED_HELPERS) |marker| try guard.requireMarker(text_map_reuse_required_helpers, marker);
    const text_map_reuse_required_test_markers_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig");
    defer allocator.free(text_map_reuse_required_test_markers_path);
    const text_map_reuse_required_test_markers = try guard.readUtf8File(io, allocator, text_map_reuse_required_test_markers_path);
    defer allocator.free(text_map_reuse_required_test_markers);
    for (MAP_REUSE_REQUIRED_TEST_MARKERS) |marker| try guard.requireMarker(text_map_reuse_required_test_markers, marker);
    const text_passing_helper_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig");
    defer allocator.free(text_passing_helper_path);
    const text_passing_helper = try guard.readUtf8File(io, allocator, text_passing_helper_path);
    defer allocator.free(text_passing_helper);
    for (PASSING_HELPER) |marker| try guard.requireMarker(text_passing_helper, marker);
    const text_passing_test_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig");
    defer allocator.free(text_passing_test_path);
    const text_passing_test = try guard.readUtf8File(io, allocator, text_passing_test_path);
    defer allocator.free(text_passing_test);
    for (PASSING_TEST) |marker| try guard.requireMarker(text_passing_test, marker);
    const text_failing_helper_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig");
    defer allocator.free(text_failing_helper_path);
    const text_failing_helper = try guard.readUtf8File(io, allocator, text_failing_helper_path);
    defer allocator.free(text_failing_helper);
    for (FAILING_HELPER) |marker| try guard.requireMarker(text_failing_helper, marker);
    const text_failing_test_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig");
    defer allocator.free(text_failing_test_path);
    const text_failing_test = try guard.readUtf8File(io, allocator, text_failing_test_path);
    defer allocator.free(text_failing_test);
    for (FAILING_TEST) |marker| try guard.requireMarker(text_failing_test, marker);
    const text_failing_fdinfo_helper_path = try guard.joinPath(allocator, root, "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig");
    defer allocator.free(text_failing_fdinfo_helper_path);
    const text_failing_fdinfo_helper = try guard.readUtf8File(io, allocator, text_failing_fdinfo_helper_path);
    defer allocator.free(text_failing_fdinfo_helper);
    for (FAILING_FDINFO_HELPER) |marker| try guard.requireMarker(text_failing_fdinfo_helper, marker);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    try checkRepo(io, allocator, try guard.defaultRepoRoot(allocator));
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    checkRepo(io, allocator, root) catch {
        std.process.exit(1);
    };
    try guard.printLine(io, "{s}", .{live_pass_marker});
}
