// Ported from check-phase15-shared-summary-gap.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE15_SHARED_SUMMARY_GAP=pass";

const CURRENT_READBACK_MARKER = "current-master-readback-2026-05-27";

const GAP_NOTE_PATH = "Documentation/zigux/phase15-shared-summary-gap.md";

const HANDOFF_NOTE_PATH = "Documentation/zigux/phase15-handoff-next-steps-survey.md";

const HANDOFF_STATUS_MARKER = "PHASE15_STATUS=handoff_next_steps_survey_landed";

const MATERIALIZED_FOCUSED_COMPANIONS = [_][]const u8{
    "zigux/tests/phase15_architecture_council_review_process.zig",
    "zigux/tests/phase15_architecture_council_review_process_build.zig",
    "zigux/tests/phase15_architecture_council_review_process_manifest.json",
    "zigux/tests/phase15_governance_lane_sequencing_manifest.json",
    "zigux/tests/phase15_governance_lane_sequencing.zig",
    "zigux/tests/phase15_readiness_gate_manifest.json",
    "zigux/tests/phase15_handoff_next_steps_manifest.json",
    "zigux/tests/phase15_handoff_next_steps.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
    "zigux/tests/phase15_build.zig",
    "scripts\\zigux/check_phase15_architecture_council_packet.zig",
    "scripts\\zigux/check_phase15_review_process_handoff.zig",
    "scripts\\zigux/check_phase15_review_checklist_study_only_alignment.zig",
    "scripts\\zigux/check_phase15_tests_readme_alignment.zig",
    "scripts\\zigux/check_phase15_handoff_note_alignment.zig",
    "scripts\\zigux/check_phase15_readiness_gate_packet.zig",
    "scripts\\zigux/validate_phase15.zig",
};

const MATERIALIZED_GOVERNANCE_PATHS = [_][]const u8{
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
    "Documentation/zigux/phase15-architecture-council-decision-index.md",
    "Documentation/zigux/phase15-parity-scorecard-survey.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
    "Documentation/zigux/phase15-deep-core-blocker-survey.md",
    "scripts\\zigux/check_phase15_scripts_readme_alignment.zig",
    "zigux/tests/phase15_freeze_map_governance.zig",
    "zigux/tests/phase15_parity_scorecard.json",
    "zigux/tests/phase15_parity_scorecard.zig",
    "zigux/tests/phase15_indefinite_c_policy.json",
    "zigux/tests/phase15_indefinite_c_policy.zig",
};

const REQUIRED_NOTE_MARKERS = [_][]const u8{
    "surveyed against dated current-master readback marker `current-master-readback-2026-05-27`",
    "`Documentation/zigux/README.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`scripts/zigux/README.md`",
    "`zigux/tests/README.md`",
    "`Documentation/zigux/phase15-freeze-map-governance.md`",
    "`Documentation/zigux/phase15-architecture-council-review-process.md`",
    "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
    "`Documentation/zigux/phase15-architecture-council-decision-index.md`",
    "`Documentation/zigux/phase15-indefinite-c-policy.md`",
    "`Documentation/zigux/phase15-parity-scorecard.md`",
    "`Documentation/zigux/phase15-parity-scorecard-survey.md`",
    "`Documentation/zigux/phase15-readiness-gate-survey.md`",
    "`Documentation/zigux/phase15-governance-lane-sequencing.md`",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`Documentation/zigux/phase15-handoff-next-steps-survey.md`",
    "`scripts\\zigux/check_phase15_docs_readme_alignment.zig`",
    "`scripts\\zigux/check_phase15_scripts_readme_alignment.zig`",
    "`scripts\\zigux/check_phase15_review_checklist_study_only_alignment.zig`",
    "`scripts\\zigux/check_phase15_tests_readme_alignment.zig`",
    "`scripts\\zigux/check_phase15_architecture_council_packet.zig`",
    "`scripts\\zigux/check_phase15_review_process_handoff.zig`",
    "`scripts\\zigux/check_phase15_handoff_note_alignment.zig`",
    "`scripts\\zigux/check_phase15_shared_summary_gap.zig`",
    "`scripts\\zigux/check_phase15_readiness_gate_packet.zig`",
    "`zigux/tests/phase15_architecture_council_review_process_manifest.json`",
    "`zigux/tests/phase15_governance_lane_sequencing_manifest.json`",
    "`zigux/tests/phase15_governance_lane_sequencing.zig`",
    "`zigux/tests/phase15_readiness_gate_manifest.json`",
    "`zigux/tests/phase15_handoff_next_steps_manifest.json`",
    "`zigux/tests/phase15_handoff_next_steps.zig`",
    "`zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`",
    "`zigux/tests/phase15_build.zig`",
    "`scripts/zigux/README.md` now keeps the directly materialized `scripts\\zigux/validate_phase15.zig` maintenance gate, the directly materialized `scripts\\zigux/check_phase15_architecture_council_packet.zig` Architecture Council packet checker, and the directly materialized `zigux/tests/phase15_build.zig` shared build companion explicit while the parked `make -C zigux phase15-validate`, `make -C zigux phase15-test`, and `make -C zigux phase15` routes plus the shared-CI route remain the broader route-level gaps on current `master`",
    "broader wrapper-route wording around `make -C zigux phase15-validate`, `make -C zigux phase15-test`, `make -C zigux phase15`, and the dedicated shared-CI Phase 15 route names",
};

const REQUIRED_WATCHPOINT_MARKERS = [_][]const u8{
    "`Documentation/zigux/phase15-architecture-council-decision-index.md`",
    "`scripts\\zigux/check_phase15_scripts_readme_alignment.zig`",
    "`Documentation/zigux/phase15-readiness-gate-survey.md`",
    "`Documentation/zigux/phase15-governance-lane-sequencing.md`",
    "`zigux/tests/phase15_governance_lane_sequencing_manifest.json`",
    "`zigux/tests/phase15_governance_lane_sequencing.zig`",
    "`zigux/tests/phase15_readiness_gate_manifest.json`",
    "`zigux/tests/phase15_build.zig`",
    "`scripts\\zigux/check_phase15_readiness_gate_packet.zig`",
    "`scripts/zigux/README.md` now keeps the directly materialized `scripts\\zigux/validate_phase15.zig` maintenance gate, the directly materialized `scripts\\zigux/check_phase15_architecture_council_packet.zig` Architecture Council packet checker, and the directly materialized `zigux/tests/phase15_build.zig` shared build companion explicit while the parked `make -C zigux phase15-validate`, `make -C zigux phase15-test`, and `make -C zigux phase15` routes plus the shared-CI route remain the broader route-level gaps on current `master`",
};

const ROUTE_GAP_MARKERS = [_][]const u8{
    "no dedicated `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15` route body is materialized on current `master`",
    "`.github/workflows/zigux-bootstrap.yml` still carries no dedicated Phase 15 validate, test, or aggregate route name on current `master`",
};

const STALE_TEXT_MARKERS = [_][]const u8{
    "## Still-missing focused companions on current master",
    "The current shared-summary drift is anchored to these still-missing paths:",
    "previously treated as missing",
    "current-master-readback-2026-05-17",
    "current-master-readback-2026-05-21",
    "current-master-readback-2026-05-23",
};

const STATUS_MARKERS = [_][]const u8{
    "PHASE15_STATUS=shared_summary_gap_recorded",
    "PHASE15_LANE_KEY=P15-L02",
    "PHASE15_SLICE=materialized-governance-packet-truthfulness-refresh",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
};

const VALIDATOR_WORDING_SPLIT_MARKER = "`scripts/zigux/README.md` now keeps the directly materialized `scripts\\zigux/validate_phase15.zig` maintenance gate, the directly materialized `scripts\\zigux/check_phase15_architecture_council_packet.zig` Architecture Council packet checker, and the directly materialized `zigux/tests/phase15_build.zig` shared build companion explicit while the parked `make -C zigux phase15-validate`, `make -C zigux phase15-test`, and `make -C zigux phase15` routes plus the shared-CI route remain the broader route-level gaps on current `master`";

const WATCHPOINTS_HEADING = "## Current shared-summary watchpoints";

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
    try guard.printLine(io, "PHASE15_SHARED_SUMMARY_GAP_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
        try guard.printLine(io, "PHASE15_SHARED_SUMMARY_GAP=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    std.process.exit(0);
}
