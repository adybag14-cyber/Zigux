const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE1_CLOSURE_VALIDATION=pass";
pub const self_test_pass_marker = "PHASE1_CLOSURE_SELF_TEST=pass";

const FileContract = struct { rel: []const u8, markers: []const []const u8 };

const markers_0 = [_][]const u8{
    "tools/lib/argv_split.zig",
    "tools/lib/bitmap.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/string.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
};

const markers_1 = [_][]const u8{
    "tools/lib/argv_split.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
    "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local follow-up anchors on current master.",
    "Do not reopen Phase 1 by batching helpers across those two sets in one lane; shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers reopen only for their existing helper-local anchors or already-committed shared fixture keys.",
};

const markers_2 = [_][]const u8{
    "phase2-toolchain:",
    "phase2-tools:",
    "phase2-kconfig:",
    "phase2-cross:",
    "phase2-genksyms:",
    "phase3-validate:",
    "phase3:",
    "phase4-validate:",
    "phase6-validate:",
    "phase8-validate:",
    "phase12-validate:",
    "phase12-smoke:",
    "phase12-test:",
    "phase12: phase12-validate phase12-smoke phase12-test",
    "phase14-validate:",
};

const markers_3 = [_][]const u8{
    "check_phase1_string_review_packet.zig",
    "check_phase1_find_bit_review_packet.zig",
    "check_phase1_rbtree_review_packet.zig",
    "check_phase1_direct_owner_markers.zig",
    "check_phase1_direct_anchor_manifest_gate.zig",
    "check_phase1_route_summary_counts.zig",
    "check_phase1_find_bit_bench_anchors.zig",
    "check_phase1_bitmap_direct_anchors.zig",
    "check_phase1_shared_reminder_packet.zig",
};

const markers_4 = [_][]const u8{
    "PHASE1_CURRENT_REMINDER_PACKET=",
    "PHASE1_CLOSURE_VALIDATOR=zig run scripts/zigux/validate_phase1_closure.zig",
    "PHASE1_ROUTE_SUMMARY_GUARD=zig run scripts/zigux/check_phase1_route_summary_counts.zig",
};

const forbidden_makefile_markers = [_][]const u8{
    "phase1-validate:",
    "phase1-test:",
    "phase1-bench:",
    "phase1:",
};

const contracts = [_]FileContract{
    .{ .rel = "zigux/tests/fixtures/phase1_helper_manifest.json", .markers = &markers_0 },
    .{ .rel = "Documentation/zigux/phase1-host-helper-lane-sequencing.md", .markers = &markers_1 },
    .{ .rel = "zigux/Makefile", .markers = &markers_2 },
    .{ .rel = ".github/workflows/zigux-bootstrap.yml", .markers = &markers_3 },
    .{ .rel = "Documentation/zigux/phase1-closure.md", .markers = &markers_4 },
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (contracts) |contract| {
        const path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(path);
        const text = try guard.readUtf8File(io, allocator, path);
        defer allocator.free(text);
        for (contract.markers) |marker| try guard.requireMarker(text, marker);
    }
    const make_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(make_path);
    const make_text = try guard.readUtf8File(io, allocator, make_path);
    defer allocator.free(make_text);
    for (forbidden_makefile_markers) |marker| {
        if (std.mem.indexOf(u8, make_text, marker) != null) return guard.GuardError.ValidationFailed;
    }
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());
    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) { self_test = true; continue; }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1; explicit_root = args[index]; continue;
        }
        std.process.exit(2);
    }
    if (self_test) std.process.exit(try runSelfTest(io, allocator));
    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    checkRepo(io, allocator, root) catch std.process.exit(1);
    try guard.printLine(io, "{s}", .{live_pass_marker});
}
