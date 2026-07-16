const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE1_SHARED_REMINDER_PACKET=pass";
pub const self_test_pass_marker = "PHASE1_SHARED_REMINDER_PACKET_SELF_TEST=pass";

const FileContract = struct {
    rel: []const u8,
    markers: []const []const u8,
};

const markers_0 = [_][]const u8{
    "PHASE1_CURRENT_REMINDER_PACKET=",
    "PHASE1_CLOSURE_VALIDATOR=zig run validate_phase1_closure.zig",
    "PHASE1_ROUTE_SUMMARY_GUARD=zig run check_phase1_route_summary_counts.zig",
    "PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
};

const markers_1 = [_][]const u8{
    "PHASE1_DIRECT_ANCHOR_FOLLOWUP_HELPERS=tools/lib/bitmap.zig,tools/lib/find_bit.zig,tools/lib/rbtree.zig,tools/lib/string.zig",
};

const markers_2 = [_][]const u8{
    "zig run check_phase1_shared_reminder_packet.zig --self-test",
    "phase1-host-tools-smoke --build-file zigux/tests/build.zig",
};

const markers_3 = [_][]const u8{
    "phase1-host-tools-smoke --build-file zigux/tests/build.zig",
};

const markers_4 = [_][]const u8{
    "phase1-route-summary:",
};

const markers_5 = [_][]const u8{
    "run: zig run check_phase1_shared_reminder_packet.zig --self-test",
    "run: zig run check_phase1_shared_reminder_packet.zig",
    "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
};

const markers_6 = [_][]const u8{
    "PHASE1_DIRECT_OWNER_MARKERS_SELF_TEST=pass",
};

const markers_7 = [_][]const u8{
    "PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_SELF_TEST=pass",
};

const markers_8 = [_][]const u8{
    "PHASE1_FIND_BIT_REVIEW_PACKET_SELF_TEST=pass",
};

const markers_9 = [_][]const u8{
    "PHASE1_ROUTE_SUMMARY_COUNTS_SELF_TEST=pass",
};

const markers_10 = [_][]const u8{
    "PHASE1_BENCH_CHECK_SELF_TEST=pass",
};

const markers_11 = [_][]const u8{
    "PHASE1_CLOSURE_VALIDATION=pass",
    "PHASE1_CLOSURE_SELF_TEST=pass",
};

const contracts = [_]FileContract{
    .{ .rel = "Documentation/zigux/phase1-closure.md", .markers = &markers_0 },
    .{ .rel = "Documentation/zigux/phase1-host-helper-lane-sequencing.md", .markers = &markers_1 },
    .{ .rel = "scripts/zigux/README.md", .markers = &markers_2 },
    .{ .rel = "zigux/tests/README.md", .markers = &markers_3 },
    .{ .rel = "zigux/Makefile", .markers = &markers_4 },
    .{ .rel = ".github/workflows/zigux-bootstrap.yml", .markers = &markers_5 },
    .{ .rel = "scripts/zigux/check_phase1_direct_owner_markers.zig", .markers = &markers_6 },
    .{ .rel = "scripts/zigux/check_phase1_direct_anchor_manifest_gate.zig", .markers = &markers_7 },
    .{ .rel = "scripts/zigux/check_phase1_find_bit_review_packet.zig", .markers = &markers_8 },
    .{ .rel = "scripts/zigux/check_phase1_route_summary_counts.zig", .markers = &markers_9 },
    .{ .rel = "scripts/zigux/check_phase1_bench.zig", .markers = &markers_10 },
    .{ .rel = "scripts/zigux/validate_phase1_closure.zig", .markers = &markers_11 },
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (contracts) |contract| {
        const path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(path);
        const text = try guard.readUtf8File(io, allocator, path);
        defer allocator.free(text);
        for (contract.markers) |marker| try guard.requireMarker(text, marker);
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
            index += 1;
            explicit_root = args[index];
            continue;
        }
        std.process.exit(2);
    }
    if (self_test) std.process.exit(try runSelfTest(io, allocator));
    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    checkRepo(io, allocator, root) catch std.process.exit(1);
    try guard.printLine(io, "{s}", .{live_pass_marker});
}
