const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_RBTREE_ANCHOR_GAP=pass";
pub const self_test_pass_marker = "PHASE3_RBTREE_ANCHOR_GAP_SELF_TEST=pass";

const REQUIRED_DOC_MARKERS = [_][]const u8{
    "- the Phase 3 roadmap names `lib/rbtree.c` as one of the permanent C/Zigux boundary anchors beside `rust/exports.c`, `lib/bitmap.c`, and `lib/cpumask.c`",
    "- `include/zigux/abi.h` already exposes `zigux_rbtree_root_view`, `zigux_rbtree_root_view_is_cached()`, `zigux_rbtree_root_view_has_leftmost()`, `zigux_rbtree_root_view_is_valid()`, and `zigux_rbtree_root_view_canonicalize()`",
    "- `zigux/bindings/abi.zig` already mirrors that shared ABI surface through `RbtreeRootView`, `rbtreeRootViewIsCached()`, `rbtreeRootViewHasLeftmost()`, `rbtreeRootViewIsValid()`, and `canonicalizeRbtreeRootView()`",
    "- `zigux/kernel/export_shim.zig` already keeps the runtime status relay explicit through `validateRbtreeRootView()`",
    "Current `master` carries shared `RbtreeRootView` ABI and validation evidence, but it does not yet carry a dedicated manifest-backed `lib/rbtree.c` boundary packet comparable to the landed bitmap/cpumask and list/hlist survey slices.",
    "- add a dedicated `phase3-rbtree` survey packet that reuses the existing `RbtreeRootView` ABI surface, keeps the scope at boundary and layout validation, and does not widen into broader runtime-core delivery",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_doc_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-rbtree-anchor-gap.md");
    defer allocator.free(text_required_doc_markers_path);
    const text_required_doc_markers = try guard.readUtf8File(io, allocator, text_required_doc_markers_path);
    defer allocator.free(text_required_doc_markers);
    for (REQUIRED_DOC_MARKERS) |marker| try guard.requireMarker(text_required_doc_markers, marker);
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
