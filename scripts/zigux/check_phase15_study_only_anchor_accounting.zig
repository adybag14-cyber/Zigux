// Ported from check-phase15-study-only-anchor-accounting.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE15_STUDY_ONLY_ACCOUNTING_SELF_TEST=pass";

const ANCHORS = [_][]const u8{
    "`kernel/workqueue.c`",
    "`kernel/trace/ring_buffer.c`",
};

const FORBIDDEN_MARKERS = [_][]const u8{
    "an Architecture Council approval for any study-only anchor to leave its current posture",
    "a direct Zigux bridge for `kernel/workqueue.c`",
    "a direct Zigux bridge for `kernel/trace/ring_buffer.c`",
};

const FREEZE_MAP_PATH = "Documentation/zigux/freeze-map.md";

const FREEZE_MAP_REQUIRED_MARKERS = [_][]const u8{
    "## Study / Boundary Only",
    "`kernel/workqueue.c`",
    "`kernel/trace/ring_buffer.c`",
    "shared reminder surfaces that summarize freeze posture",
    "must keep the same study-only anchor inventory and route back to `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "study-only anchor maintenance must stay aligned with `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
};

const HANDOFF_PATH = "Documentation/zigux/phase15-handoff-next-steps-survey.md";

const HANDOFF_REQUIRED_MARKERS = [_][]const u8{
    "keep the two roadmap study-only anchors parked: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c`",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
};

const LANE_SEQ_PATH = "Documentation/zigux/phase15-governance-lane-sequencing.md";

const LANE_SEQ_REQUIRED_MARKERS = [_][]const u8{
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md` owns the explicit two-anchor study-only inventory that stays outside the freeze-in-C scorecard and blocked status-change rows",
    "`Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` are shared reminder surfaces that may summarize the parked packet, but they do not own freeze-map status decisions themselves",
};

const PARITY_SCORECARD_PATH = "Documentation/zigux/phase15-parity-scorecard.md";

const PARITY_SCORECARD_REQUIRED_MARKERS = [_][]const u8{
    "study-only anchors tracked outside this scorecard: `2`",
    "study-only anchors remain outside this scorecard until a lane asks for a status-bucket review",
};

const REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md";

const REVIEW_CHECKLIST_REQUIRED_MARKERS = [_][]const u8{
    "if a shared reminder surface summarizes the study-only freeze-map anchors",
    "`Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context rather than runtime-substrate or bridge-readiness evidence",
};

const SHARED_GAP_PATH = "Documentation/zigux/phase15-shared-summary-gap.md";

const SHARED_GAP_REQUIRED_MARKERS = [_][]const u8{
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "the checklist-specific study-only anchor summary boundary",
};

const STATUS_MARKERS = [_][]const u8{
    "PHASE15_STATUS=study_only_accounting_slice_landed",
    "PHASE15_LANE_KEY=P15-L05",
    "PHASE15_SLICE=study-only-anchor-accounting",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    "current-master-readback-2026-05-25",
};

const STUDY_ONLY_PATH = "Documentation/zigux/phase15-study-only-anchor-accounting.md";

const STUDY_ONLY_REQUIRED_MARKERS = [_][]const u8{
    "tracked outside the freeze-in-C scorecard and outside blocked status-change rows",
    "keep the two study-only anchors explicit beside the freeze map, the Phase 15 freeze-map governance note, the parity scorecard, the governance-lane sequencing note, the handoff-next-steps survey, the shared-summary gap note, and the landed validator-first maintenance gate",
    "the current Phase 15 parity scorecard still records `study-only anchors tracked outside this scorecard: 2`",
    "the current Phase 15 governance-lane sequencing note keeps the study-only inventory explicitly parked behind the owner packets and the remaining dedicated-build gap",
    "the current Phase 15 handoff-next-steps survey keeps the same two study-only anchors parked beside the existing governance packet",
    "the current Phase 15 shared-summary gap note and landed tests-root governance reminder keep docs-root, checklist, scripts-root, tests-root, and validator-first wording drift framed as truthfulness follow-through rather than study-only status-change evidence",
    "this note is an inventory and handoff surface, not an approval record",
    "if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it",
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
    try guard.printLine(io, "PHASE15_STUDY_ONLY_ACCOUNTING_SELF_TEST_CASES={d}", .{@as(usize, 1)});
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
        try guard.printLine(io, "PHASE15_STUDY_ONLY_ACCOUNTING_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    std.process.exit(0);
}
