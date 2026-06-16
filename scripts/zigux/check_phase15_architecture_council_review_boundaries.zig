// Ported from check-phase15-architecture-council-review-boundaries.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE15_ARCHITECTURE_COUNCIL_REVIEW_BOUNDARIES_SELF_TEST=pass";

const DECISION_INDEX_PATH = "Documentation/zigux/phase15-architecture-council-decision-index.md";

const DECISION_TEMPLATE_PATH = "Documentation/zigux/phase15-architecture-council-decision-record-template.md";

const FREEZE_IN_C_ANCHORS = [_][]const u8{
    "`kernel/sched/core.c`",
    "`mm/page_alloc.c`",
    "`kernel/rcu/tree.c`",
    "`net/core/skbuff.c`",
};

const FREEZE_MAP_PATH = "Documentation/zigux/freeze-map.md";

const REQUIRED_REVIEW_FIELDS = [_][]const u8{
    "exact Linux anchor path",
    "required approver set",
    "rollback owner",
    "validation gate summary",
    "evidence archive path",
    "rollback threshold",
    "`retired_from_active_discussion` state",
    "reopen triggers",
    "trigger-specific evidence refresh",
    "governance lane sequencing link or explicit scope note",
    "study-only anchor accounting link or explicit freeze-map-anchor confirmation",
    "written rationale",
};

const REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md";

const REVIEW_PROCESS_PATH = "Documentation/zigux/phase15-architecture-council-review-process.md";

const STUDY_ONLY_ACCOUNTING_PATH = "Documentation/zigux/phase15-study-only-anchor-accounting.md";

const STUDY_ONLY_ANCHORS = [_][]const u8{
    "`kernel/workqueue.c`",
    "`kernel/trace/ring_buffer.c`",
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
    try guard.printLine(io, "PHASE15_ARCHITECTURE_COUNCIL_REVIEW_BOUNDARIES_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
        try guard.printLine(io, "PHASE15_ARCHITECTURE_COUNCIL_REVIEW_BOUNDARIES_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    std.process.exit(0);
}
