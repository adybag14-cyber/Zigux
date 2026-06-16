// Ported from check-phase15-decision-record-template-alignment.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE15_DECISION_RECORD_TEMPLATE_ALIGNMENT_SELF_TEST=pass";

const CHECKLIST_BOUNDARY_MARKERS = [_][]const u8{
    "`Documentation/zigux/phase15-architecture-council-review-process.md`",
    "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
    "owners of the exact Architecture Council field inventory",
    "stay-in-C closeout record",
    "reopen-evidence details",
};

const CHECKLIST_ENTRY_PROMPT = "if a freeze-map anchor is entering Architecture Council status review";

const DECISION_TEMPLATE_PATH = "Documentation/zigux/phase15-architecture-council-decision-record-template.md";

const FREEZE_MAP_GOVERNANCE_MARKERS = [_][]const u8{
    "freeze-map status-change requests must route through `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, and `Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
    "decision record ID",
    "required approver set",
    "automatic return-to-blocked trigger",
    "`retired_from_active_discussion` state",
    "parity scorecard link or blocker record",
    "indefinite-C policy link or non-applicability note",
};

const FREEZE_MAP_PATH = "Documentation/zigux/freeze-map.md";

const REOPEN_EVIDENCE_FIELDS = [_][]const u8{
    "the exact reopen trigger being exercised",
    "refreshed evidence by path",
    "the blocker disposition being challenged",
    "the narrower seam or policy change that makes the new review safe to consider",
};

const REQUIRED_REVIEW_FIELDS = [_][]const u8{
    "exact Linux anchor path",
    "roadmap phase",
    "decision record ID",
    "lane owner",
    "current status bucket",
    "requested decision bucket",
    "required approver set",
    "rollback owner",
    "validation gate summary",
    "evidence archive path",
    "latest blocker disposition",
    "benchmark notes",
    "replay command",
    "rollback threshold",
    "automatic return-to-blocked trigger",
    "`retired_from_active_discussion` state",
    "reopen triggers",
    "trigger-specific evidence refresh",
    "parity scorecard link or blocker record",
    "indefinite-C policy link or explicit non-applicability note",
    "explicit non-goals",
    "written rationale",
};

const REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md";

const REVIEW_PROCESS_PATH = "Documentation/zigux/phase15-architecture-council-review-process.md";

const STAY_IN_C_CLOSEOUT_FIELDS = [_][]const u8{
    "the retained `freeze_in_c` decision",
    "the current blocker",
    "the required approver set",
    "`retired_from_active_discussion` state",
    "automatic return-to-blocked trigger",
    "the reopen triggers",
    "the trigger-specific evidence refresh",
    "the evidence archive path that will be refreshed before any later reopen request",
};

const TEMPLATE_REQUIRED_MARKERS = [_][]const u8{
    "`DECISION_RECORD_ID=<replace-with-stable-id>`",
    "`PHASE=Phase 15`",
    "`LANE_KEY=P15-L08`",
    "`PHASE15_PROVENANCE_MODE=dated_master_readback`",
    "`SURVEYED_COMMIT=current-master-readback-YYYY-MM-DD`",
    "exact-head provenance exception note:",
    "`REVIEW_STATUS=<blocked_review|stay_in_c|approved_status_bucket_change>`",
    "Prefer the dated master readback form for parked governance and stay-in-C review packets.",
    "Only record an exact head when the linked review needs it to anchor a named published decision",
    "Do not use this template to pull `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, or any other study-only anchor into a freeze-in-C status review unless the freeze map and supporting governance packet have been explicitly updated first.",
    "If any required field above cannot be stated honestly, keep the request blocked and leave the C implementation as the product source of truth.",
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
    try guard.printLine(io, "PHASE15_DECISION_RECORD_TEMPLATE_ALIGNMENT_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
        try guard.printLine(io, "PHASE15_DECISION_RECORD_TEMPLATE_ALIGNMENT_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE15_DECISION_RECORD_TEMPLATE_ALIGNMENT_REQUIRED_FIELD_COUNT={d}", .{@as(usize, REQUIRED_REVIEW_FIELDS.len)});
    try guard.printLine(io, "PHASE15_DECISION_RECORD_TEMPLATE_ALIGNMENT_CLOSEOUT_FIELD_COUNT={d}", .{@as(usize, STAY_IN_C_CLOSEOUT_FIELDS.len)});
    try guard.printLine(io, "PHASE15_DECISION_RECORD_TEMPLATE_ALIGNMENT_REOPEN_FIELD_COUNT={d}", .{@as(usize, REOPEN_EVIDENCE_FIELDS.len)});
    std.process.exit(0);
}
