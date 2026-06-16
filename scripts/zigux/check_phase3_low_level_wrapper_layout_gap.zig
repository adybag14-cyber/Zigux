const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_LOW_LEVEL_WRAPPER_LAYOUT_GAP=pass";
pub const self_test_pass_marker = "PHASE3_LOW_LEVEL_WRAPPER_LAYOUT_GAP_SELF_TEST=pass";

const REQUIRED_LAYOUT_TEST_MARKERS = [_][]const u8{
    "const layout_assert = @import(\"layout_assert\");",
    "test \"phase3 low-level wrappers keep helper-local MMIO layout assertions explicit\" {",
    "try layout_assert.assertMmioRangeLayout();",
};

const REQUIRED_DEDICATED_BUILD_MARKERS = [_][]const u8{
    ".root_source_file = b.path(\"../helpers/layout_assert.zig\"),",
    "layout_assert.addImport(\"abi_bindings\", abi_bindings);",
    "root_module.addImport(\"layout_assert\", layout_assert);",
    "\"phase3-low-level-wrappers-test\"",
};

const REQUIRED_SHARED_SEGMENT_MARKERS = [_][]const u8{
    "fn addPhase3LowLevelWrappers(",
    ".root_source_file = b.path(\"../helpers/atomic.zig\"),",
    ".root_source_file = b.path(\"../helpers/barrier.zig\"),",
    ".root_source_file = b.path(\"../helpers/mmio.zig\"),",
    "root_module.addImport(\"atomic\", atomic);",
    "root_module.addImport(\"barrier\", barrier);",
    "root_module.addImport(\"mmio\", mmio);",
    "root_module.addImport(\"unsafe_policy\", unsafe_policy);",
    "root_module.addImport(\"narrow\", narrow);",
};

const FORBIDDEN_SHARED_SEGMENT_MARKERS = [_][]const u8{
    ".root_source_file = b.path(\"../helpers/layout_assert.zig\"),",
    "layout_assert.addImport(\"abi_bindings\", abi_bindings);",
    "root_module.addImport(\"layout_assert\", layout_assert);",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_layout_test_markers_path = try guard.joinPath(allocator, root, "zigux/tests/phase3_low_level_wrappers.zig");
    defer allocator.free(text_required_layout_test_markers_path);
    const text_required_layout_test_markers = try guard.readUtf8File(io, allocator, text_required_layout_test_markers_path);
    defer allocator.free(text_required_layout_test_markers);
    for (REQUIRED_LAYOUT_TEST_MARKERS) |marker| try guard.requireMarker(text_required_layout_test_markers, marker);
    const text_required_dedicated_build_markers_path = try guard.joinPath(allocator, root, "zigux/tests/phase3_low_level_wrappers.zig");
    defer allocator.free(text_required_dedicated_build_markers_path);
    const text_required_dedicated_build_markers = try guard.readUtf8File(io, allocator, text_required_dedicated_build_markers_path);
    defer allocator.free(text_required_dedicated_build_markers);
    for (REQUIRED_DEDICATED_BUILD_MARKERS) |marker| try guard.requireMarker(text_required_dedicated_build_markers, marker);
    const text_required_shared_segment_markers_path = try guard.joinPath(allocator, root, "zigux/tests/phase3_low_level_wrappers.zig");
    defer allocator.free(text_required_shared_segment_markers_path);
    const text_required_shared_segment_markers = try guard.readUtf8File(io, allocator, text_required_shared_segment_markers_path);
    defer allocator.free(text_required_shared_segment_markers);
    for (REQUIRED_SHARED_SEGMENT_MARKERS) |marker| try guard.requireMarker(text_required_shared_segment_markers, marker);
    const text_forbidden_shared_segment_markers_path = try guard.joinPath(allocator, root, "zigux/tests/phase3_low_level_wrappers.zig");
    defer allocator.free(text_forbidden_shared_segment_markers_path);
    const text_forbidden_shared_segment_markers = try guard.readUtf8File(io, allocator, text_forbidden_shared_segment_markers_path);
    defer allocator.free(text_forbidden_shared_segment_markers);
    for (FORBIDDEN_SHARED_SEGMENT_MARKERS) |marker| {
        if (std.mem.indexOf(u8, text_forbidden_shared_segment_markers, marker) != null) return guard.GuardError.MissingMarker;
    }
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
