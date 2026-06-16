const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_RBTREE_ANCHOR_GAP=pass";
pub const self_test_pass_marker = "PHASE3_RBTREE_ANCHOR_GAP_SELF_TEST=pass";

const REQUIRED_NOTE_MARKERS = [_][]const u8{
    "Phase 3 Rbtree Anchor Gap",
    "the Phase 3 roadmap names `lib/rbtree.c` as one of the permanent C/Zigux boundary anchors",
    "`include/zigux/abi.h` already exposes `zigux_rbtree_root_view`",
    "`zigux/bindings/abi.zig` already mirrors that shared ABI surface through `RbtreeRootView`",
    "`zigux/kernel/export_shim.zig` already keeps the runtime status relay explicit through `validateRbtreeRootView()`",
    "`zigux/tests/phase3_abi.zig` already replays the shared `RbtreeRootView` layout and validation path",
    "`Documentation/zigux/phase3-bitmap-cpumask-slice.md`, `zigux/helpers/bitmap_view.zig`, and `zigux/helpers/cpumask_view.zig` already provide a dedicated bounded packet",
    "`Documentation/zigux/phase3-list-hlist-slice.md`, `zigux/helpers/list_view.zig`, and `zigux/helpers/hlist_view.zig` already provide a dedicated adjacent boundary packet",
    "Current `master` carries shared `RbtreeRootView` ABI and validation evidence, but it does not yet carry a dedicated manifest-backed `lib/rbtree.c` boundary packet",
    "add a dedicated `phase3-rbtree` survey packet that reuses the existing `RbtreeRootView` ABI surface",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_note_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-rbtree-anchor-gap.md");
    defer allocator.free(text_required_note_markers_path);
    const text_required_note_markers = try guard.readUtf8File(io, allocator, text_required_note_markers_path);
    defer allocator.free(text_required_note_markers);
    for (REQUIRED_NOTE_MARKERS) |marker| try guard.requireMarker(text_required_note_markers, marker);
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
