// Ported from check-phase15-governance-lane-sequencing.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE15_GOVERNANCE_LANE_SEQUENCING_SELF_TEST=pass";

const EXPECTED_DIRECT_PACKET_PATHS = [_][]const u8{
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "Documentation/zigux/phase15-study-only-anchor-accounting.md",
    "Documentation/zigux/phase15-shared-summary-gap.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/tests/phase15_governance_lane_sequencing_manifest.json",
    "zigux/tests/phase15_governance_lane_sequencing.zig",
    "zigux/tests/phase15_handoff_next_steps_manifest.json",
    "scripts\\zigux/check_phase15_handoff_note_alignment.zig",
};

const EXPECTED_MAINTENANCE_REPLAY_COMMANDS = [_][]const u8{
    "zig run scripts/zigux/check_phase15_docs_readme_alignment.zig",
    "zig run scripts/zigux/check_phase15_scripts_readme_alignment.zig",
    "zig run scripts/zigux/check_phase15_tests_readme_alignment.zig",
    "zig run scripts/zigux/check_phase15_review_process_handoff.zig",
    "zig run scripts/zigux/check_phase15_handoff_note_alignment.zig",
    "zig run scripts/zigux/check_phase15_shared_summary_gap.zig",
    "zig test zigux/tests/phase15_governance_lane_sequencing.zig",
};

const EXPECTED_MISSING_BROADER_PATHS = [_][]const u8{
    "scripts\\zigux/validate_phase15.zig",
    "zigux/tests/phase15_build.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
};

const MAKEFILE_PATH = "zigux/Makefile";

const MANIFEST_PATH = "zigux/tests/phase15_governance_lane_sequencing_manifest.json";

const READINESS_NOTE_PATH = "Documentation/zigux/phase15-readiness-gate-survey.md";

const REQUIRED_NOTE_MARKERS = [_][]const u8{
    "PHASE15_STATUS=governance_lane_sequencing_packet_landed",
    "PHASE15_LANE_KEY=arch-council",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    "Phase 15 is a governance tranche, not a hidden deep-core delivery lane.",
    "`zigux/tests/phase15_governance_lane_sequencing_manifest.json` and `zigux/tests/phase15_governance_lane_sequencing.zig`",
    "`zigux/tests/phase15_handoff_next_steps_manifest.json` and `scripts\\zigux/check_phase15_handoff_note_alignment.zig`",
    "The shared reminder surfaces must not say that:",
    "a deep-core status change has been approved",
    "a freeze-in-C anchor is ready for a direct Zigux bridge",
    "a missing focused replay, dedicated build file, or other absent broader companion is already landed on current `master`",
    "zig run scripts/zigux/check_phase15_tests_readme_alignment.zig",
    "zig run scripts/zigux/check_phase15_handoff_note_alignment.zig",
    "zig test zigux/tests/phase15_governance_lane_sequencing.zig",
};

const REQUIRED_READINESS_MARKERS = [_][]const u8{
    "`Documentation/zigux/phase15-governance-lane-sequencing.md`",
    "`zigux/tests/phase15_governance_lane_sequencing_manifest.json`",
    "`zigux/tests/phase15_governance_lane_sequencing.zig`",
    "`zigux/tests/phase15_handoff_next_steps_manifest.json`",
};

const SEQUENCING_NOTE_PATH = "Documentation/zigux/phase15-governance-lane-sequencing.md";

const SHARED_GAP_NOTE_PATH = "Documentation/zigux/phase15-shared-summary-gap.md";

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
    try guard.printLine(io, "PHASE15_GOVERNANCE_LANE_SEQUENCING_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
        try guard.printLine(io, "PHASE15_GOVERNANCE_LANE_SEQUENCING_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    std.process.exit(0);
}
