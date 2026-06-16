const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "CHECK_PHASE3_BITMAP_CPUMASK_STARTER_PACKET=pass";
pub const self_test_pass_marker = "CHECK_PHASE3_BITMAP_CPUMASK_STARTER_PACKET_SELF_TEST=pass";

const REQUIRED_MARKERS__Documentation_zigux_phase3-bitmap-cpumask-slice_md = [_][]const u8{
    "bounded shared-subsystems helper packet",
    "zigux/helpers/bitmap_view.zig",
    "zigux/helpers/cpumask_view.zig",
    "zig build phase3-bitmap-cpumask-starter-packet --build-file zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig",
};

const REQUIRED_MARKERS__zigux_helpers_bitmap_view_zig = [_][]const u8{
    "pub const word_bits: usize = @bitSizeOf(usize);",
    "pub fn activeWordLen(self: BitmapView) usize {",
    "pub fn countSetBits(self: BitmapView) usize {",
    "pub fn firstSetBit(self: BitmapView) ?usize {",
    "pub fn firstClearBit(self: BitmapView) ?usize {",
};

const REQUIRED_MARKERS__zigux_helpers_cpumask_view_zig = [_][]const u8{
    "const bitmap_view = @import(\"bitmap_view\");",
    "pub fn hasCpu(self: CpuMaskView, cpu: usize) bool {",
    "pub fn countPresentCpus(self: CpuMaskView) usize {",
    "pub fn isSubsetOf(self: CpuMaskView, other: CpuMaskView) bool {",
    "pub fn intersects(self: CpuMaskView, other: CpuMaskView) bool {",
};

const REQUIRED_MARKERS__zigux_tests_phase3_bitmap_cpumask_starter_packet_zig = [_][]const u8{
    "bitmap starter packet keeps set-bit counting bounded to the declared range",
    "bitmap starter packet keeps a sparse shared bitmap reviewable",
    "cpumask starter packet keeps cpu membership and missing-cpu discovery explicit",
    "cpumask starter packet keeps subset and overlap semantics inside the bounded mask",
};

const REQUIRED_MARKERS__zigux_tests_phase3_bitmap_cpumask_starter_packet_build_zig = [_][]const u8{
    ".root_source_file = b.path(\"../helpers/bitmap_view.zig\"),",
    ".root_source_file = b.path(\"../helpers/cpumask_view.zig\"),",
    "cpumask_view.addImport(\"bitmap_view\", bitmap_view);",
    "\"phase3-bitmap-cpumask-starter-packet\"",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_markers__documentation_zigux_phase3-bitmap-cpumask-slice_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-bitmap-cpumask-slice/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase3-bitmap-cpumask-slice_md_path);
    const text_required_markers__documentation_zigux_phase3-bitmap-cpumask-slice_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase3-bitmap-cpumask-slice_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase3-bitmap-cpumask-slice_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase3-bitmap-cpumask-slice_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase3-bitmap-cpumask-slice_md, marker);
    const text_required_markers__zigux_helpers_bitmap_view_zig_path = try guard.joinPath(allocator, root, "zigux/helpers/bitmap/view/zig");
    defer allocator.free(text_required_markers__zigux_helpers_bitmap_view_zig_path);
    const text_required_markers__zigux_helpers_bitmap_view_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_helpers_bitmap_view_zig_path);
    defer allocator.free(text_required_markers__zigux_helpers_bitmap_view_zig);
    for (REQUIRED_MARKERS__zigux_helpers_bitmap_view_zig) |marker| try guard.requireMarker(text_required_markers__zigux_helpers_bitmap_view_zig, marker);
    const text_required_markers__zigux_helpers_cpumask_view_zig_path = try guard.joinPath(allocator, root, "zigux/helpers/cpumask/view/zig");
    defer allocator.free(text_required_markers__zigux_helpers_cpumask_view_zig_path);
    const text_required_markers__zigux_helpers_cpumask_view_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_helpers_cpumask_view_zig_path);
    defer allocator.free(text_required_markers__zigux_helpers_cpumask_view_zig);
    for (REQUIRED_MARKERS__zigux_helpers_cpumask_view_zig) |marker| try guard.requireMarker(text_required_markers__zigux_helpers_cpumask_view_zig, marker);
    const text_required_markers__zigux_tests_phase3_bitmap_cpumask_starter_packet_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/bitmap/cpumask/starter/packet/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_bitmap_cpumask_starter_packet_zig_path);
    const text_required_markers__zigux_tests_phase3_bitmap_cpumask_starter_packet_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_bitmap_cpumask_starter_packet_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_bitmap_cpumask_starter_packet_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_bitmap_cpumask_starter_packet_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_bitmap_cpumask_starter_packet_zig, marker);
    const text_required_markers__zigux_tests_phase3_bitmap_cpumask_starter_packet_build_zig_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/bitmap/cpumask/starter/packet/build/zig");
    defer allocator.free(text_required_markers__zigux_tests_phase3_bitmap_cpumask_starter_packet_build_zig_path);
    const text_required_markers__zigux_tests_phase3_bitmap_cpumask_starter_packet_build_zig = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_bitmap_cpumask_starter_packet_build_zig_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_bitmap_cpumask_starter_packet_build_zig);
    for (REQUIRED_MARKERS__zigux_tests_phase3_bitmap_cpumask_starter_packet_build_zig) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_bitmap_cpumask_starter_packet_build_zig, marker);
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
