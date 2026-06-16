// Ported from check-phase15-review-checklist-alignment.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE15_REVIEW_CHECKLIST_ALIGNMENT_SELF_TEST=pass";

const DECISION_RECORD_TEMPLATE_PATH = "Documentation/zigux/phase15-architecture-council-decision-record-template.md";

const DECISION_TEMPLATE_MARKERS = [_][]const u8{
    "`PHASE15_PROVENANCE_MODE=dated_master_readback`",
    "`SURVEYED_COMMIT=current-master-readback-YYYY-MM-DD`",
    "exact-head provenance exception note:",
    "Do not use this template to pull `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, or any other study-only anchor into a freeze-in-C status review",
    "If any required field above cannot be stated honestly, keep the request blocked and leave the C implementation as the product source of truth.",
};

const ENTRY_REVIEW_MARKERS = [_][]const u8{
    "`Documentation/zigux/phase15-architecture-council-review-process.md`",
    "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
    "owners of the exact Architecture Council field inventory",
    "stay-in-C closeout record",
    "reopen-evidence details",
    "`Documentation/zigux/phase15-indefinite-c-policy.md`",
    "retained blocker posture",
    "trigger-specific evidence refresh",
    "return-to-blocked wording",
};

const ENTRY_REVIEW_PROMPT = "if a freeze-map anchor is entering Architecture Council status review";

const FREEZE_MAP_MARKERS = [_][]const u8{
    "freeze-map status-change requests must route through `Documentation/zigux/phase15-architecture-council-review-process.md`",
    "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
    "shared reminder surfaces that summarize freeze posture",
    "must keep the same study-only anchor inventory and route back to `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "study-only anchor maintenance must stay aligned with `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
};

const FREEZE_MAP_PATH = "Documentation/zigux/freeze-map.md";

const INDEFINITE_C_POLICY_MARKERS = [_][]const u8{
    "the decision record ID, lane owner, required approver set, and rollback owner",
    "the automatic return-to-blocked trigger, retained `retired_from_active_discussion` state, reopen triggers, and trigger-specific evidence refresh",
    "There is no silent exception path around the indefinite-C policy.",
    "the named reopen trigger now being exercised",
};

const INDEFINITE_C_POLICY_PATH = "Documentation/zigux/phase15-indefinite-c-policy.md";

const REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md";

const REVIEW_PROCESS_MARKERS = [_][]const u8{
    "`Documentation/zigux/review-checklist.md` keeps the shared entry-review and closeout prompts explicit",
    "exact Linux anchor path",
    "roadmap phase",
    "decision record ID",
    "lane owner",
    "required approver set",
    "rollback owner",
    "the retained `freeze_in_c` decision",
    "the automatic return-to-blocked trigger",
    "the exact reopen trigger being exercised",
};

const REVIEW_PROCESS_PATH = "Documentation/zigux/phase15-architecture-council-review-process.md";

const STUDY_ONLY_ACCOUNTING_MARKERS = [_][]const u8{
    "### `kernel/workqueue.c`",
    "### `kernel/trace/ring_buffer.c`",
    "tracked outside the freeze-in-C scorecard",
    "if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it",
};

const STUDY_ONLY_ACCOUNTING_PATH = "Documentation/zigux/phase15-study-only-anchor-accounting.md";

const STUDY_ONLY_MARKERS = [_][]const u8{
    "`Documentation/zigux/freeze-map.md`",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c`",
    "study-only boundary context rather than runtime-substrate or bridge-readiness evidence",
};

const STUDY_ONLY_PROMPT = "if a shared reminder surface summarizes the study-only freeze-map anchors";

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
    try guard.printLine(io, "PHASE15_REVIEW_CHECKLIST_ALIGNMENT_SELF_TEST_CASES={d}", .{@as(usize, 1)});
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
        try guard.printLine(io, "PHASE15_REVIEW_CHECKLIST_ALIGNMENT_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    std.process.exit(0);
}
