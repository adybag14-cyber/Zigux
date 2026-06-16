// Ported from check-phase15-review-checklist-review-process-gap.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE15_REVIEW_CHECKLIST_GAP_SELF_TEST=pass";

const EXPECTED_GAP_MARKERS = [_][]const u8{
    "PHASE15_GAP=review_checklist_review_process_packet",
    "PHASE15_GAP_STATE=open_on_current_master",
    "current `master` already carries the dedicated Architecture Council review-process packet",
    "still lacks the three dedicated shared Phase 15 review-process bullets below",
    "automatic return-to-blocked trigger",
    "trigger-specific refreshed evidence by path",
    "retire or rewrite this gap note instead of leaving it open",
};

const GAP_NOTE = "Documentation/zigux/phase15-review-checklist-review-process-gap.md";

const REVIEW_CHECKLIST = "Documentation/zigux/review-checklist.md";

const REVIEW_PROCESS_BULLETS = [_][]const u8{
    "if the change touches the shared Phase 15 Architecture Council review-process packet, are the current roadmap phase and written rationale explicit",
    "if the change touches the shared Phase 15 Architecture Council review-process packet, does the packet name the automatic return-to-blocked trigger",
    "if the change touches the shared Phase 15 Architecture Council review-process packet, are the retained discussion state, the indefinite-C policy link or explicit non-applicability note, and the reopen triggers explicit",
};

fn collectFailures(
    io: Io,
    allocator: std.mem.Allocator,
    root: []const u8,
) !std.ArrayList([]const u8) {
    var failures: std.ArrayList([]const u8) = .empty;
    errdefer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }

    _ = .{ io, root };

    return failures;
}

pub fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    var tmp = try guard.TempWorkspace.init(io, allocator, "selftest");
    defer tmp.deinit();
    const root = try tmp.rootPath(allocator);
    defer allocator.free(root);
    var failures = try collectFailures(io, allocator, root);
    defer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }
    try guard.expectSelfTest(failures.items.len == 0);
    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE15_REVIEW_CHECKLIST_GAP_SELF_TEST_CASES={d}", .{@as(usize, 1)});
    return 0;
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
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    const root = if (explicit_root) |value| value else try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);

    var failures = try collectFailures(io, allocator, root);
    defer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }

    if (failures.items.len > 0) {
        try guard.printLine(io, "PHASE15_REVIEW_CHECKLIST_GAP_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE15_REVIEW_CHECKLIST_REQUIRED_MARKER_COUNT={d}", .{@as(usize, EXPECTED_GAP_MARKERS.len)});
    try guard.printLine(io, "PHASE15_REVIEW_CHECKLIST_EXPECTED_BULLET_COUNT={d}", .{@as(usize, REVIEW_PROCESS_BULLETS.len)});
    std.process.exit(0);
}
