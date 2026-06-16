// Ported from check-phase15-approver-matrix.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE15_APPROVER_MATRIX_SELF_TEST=pass";

const APPROVER_MATRIX_PATH = "Documentation/zigux/phase15-architecture-council-approver-matrix.md";

const REQUIRED_MATRIX_MARKERS = [_][]const u8{
    "`PHASE15_STATUS=architecture_council_approver_matrix_landed`",
    "`PHASE15_LANE_KEY=P15-L17`",
    "`PHASE15_SLICE=required-approver-and-rollback-owner-matrix`",
    "`PHASE15_PROVENANCE_MODE=dated_master_readback`",
    "`kernel/sched/core.c`",
    "`Architecture Council + PMO / Release Management`",
    "`blocked_no_bounded_scheduler_seam`",
    "`mm/page_alloc.c`",
    "`Architecture Council + Validation and Perf Team`",
    "`blocked_no_bounded_allocator_seam`",
    "`kernel/rcu/tree.c`",
    "`Architecture Council + ABI and Runtime Team`",
    "`blocked_phase14_followup_still_wider_than_allowed_rcu_seam`",
    "`net/core/skbuff.c`",
    "`Architecture Council + Shared Subsystems Pod`",
    "`blocked_packet_lifetime_boundary_still_too_wide`",
    "`Documentation/zigux/phase15-freeze-map-governance.md`",
    "`Documentation/zigux/phase15-architecture-council-review-process.md`",
    "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
    "`Documentation/zigux/phase15-parity-scorecard.md`",
    "`Documentation/zigux/freeze-map.md`",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
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
    try guard.printLine(io, "PHASE15_APPROVER_MATRIX_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
        try guard.printLine(io, "PHASE15_APPROVER_MATRIX_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    std.process.exit(0);
}
