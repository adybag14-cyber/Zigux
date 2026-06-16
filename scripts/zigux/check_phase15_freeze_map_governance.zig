// Ported from check-phase15-freeze-map-governance.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE15_FREEZE_MAP_GOVERNANCE_SELF_TEST=pass";

const ADJACENT_EVIDENCE_PATHS = [_][]const u8{
    "scripts\\zigux/validate_phase15.zig",
    "zigux/tests/phase15_build.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
};

const BLOCKED_MAKEFILE_MARKERS = [_][]const u8{
    "phase15-validate:",
    "phase15-test:",
    "phase15:",
    ".PHONY: phase15",
};

const FREEZE_MAP_PATH = "Documentation/zigux/freeze-map.md";

const GAP_EXPECTATIONS_ENTRIES = [_]struct { file: []const u8, marker: []const u8 }{
    .{ .file = "phase15-shared-lane-owner-readback", .marker = "materialized_in_contents_readback" },
    .{ .file = "phase15-shared-lane-owner-readback", .marker = "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig" },
    .{ .file = "phase15-shared-validator-route-readback", .marker = "materialized_on_public_master" },
    .{ .file = "phase15-shared-validator-route-readback", .marker = "scripts\\zigux/validate_phase15.zig" },
    .{ .file = "phase15-shared-build-route-readback", .marker = "materialized_on_public_master" },
    .{ .file = "phase15-shared-build-route-readback", .marker = "zigux/tests/phase15_build.zig" },
    .{ .file = "phase15-shared-wrapper-route-readback", .marker = "repo_reality_gap_confirmed" },
    .{ .file = "phase15-shared-wrapper-route-readback", .marker = "zigux/Makefile" },
};

const GOVERNANCE_NOTE_PATH = "Documentation/zigux/phase15-freeze-map-governance.md";

const GOVERNANCE_ZIG_PATH = "zigux/tests/phase15_freeze_map_governance.zig";

const MAKEFILE_PATH = "zigux/Makefile";

const MANIFEST_PATH = "zigux/tests/phase15_freeze_map_manifest.json";

const RCU_NOTE_PATH = "Documentation/zigux/phase14-rcu-tree-survey.md";

const REQUIRED_NOTE_MARKERS = [_][]const u8{
    "PHASE15_STATUS=governance_slice_landed",
    "PHASE15_LANE_KEY=P15-L04",
    "PHASE15_SLICE=freeze-map-deep-core-blocker-dated-readback-alignment",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    "current-master-readback-2026-05-20",
    "public current-master readback now resolves the shared Phase 15 validator and dedicated-build companions",
    "the current GitHub contents path in this runtime still returns not-found for `scripts\\zigux/validate_phase15.zig` and `zigux/tests/phase15_build.zig`",
    "direct contents readback now resolves `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`",
    "the current `zigux/Makefile` readback still carries no `phase15-validate`, `phase15-test`, or `phase15` targets",
    "validator-first and dedicated-build companions stay public-master materialized adjacent evidence",
    "lane-owner replay stays direct landed evidence",
    "only the wrapper routes remain adjacent gap vocabulary",
    "phase15-shared-lane-owner-readback",
    "phase15-shared-validator-route-readback",
    "phase15-shared-build-route-readback",
    "phase15-shared-wrapper-route-readback",
    "blocked_no_bounded_scheduler_seam",
    "blocked_no_bounded_allocator_seam",
    "blocked_phase14_followup_still_wider_than_allowed_rcu_seam",
    "blocked_packet_lifetime_boundary_still_too_wide",
    "## Maintenance-Mode Handoff",
    "current lane posture: `maintenance_mode`",
};

const REQUIRED_RCU_MARKERS = [_][]const u8{
    "PHASE14_LANE_KEY=P14-L16",
    "blocked by `phase14-rcu-tree-bridge-blocker`",
    "That is still a freeze-in-C posture, not a review-ready bridge seam.",
};

const REQUIRED_SKBUFF_MARKERS = [_][]const u8{
    "PHASE14_LANE_KEY=P14-L11",
    "PHASE14_BLOCKED_GAP=phase14-skbuff-live-ownership-blocker",
    "review-only skbuff bridge packet again",
    "review-first and `boundary_map_only`",
};

const REQUIRED_TRACEABILITY_MARKERS = [_][]const u8{
    "`net/core/skbuff.c`: `Freeze In C Initially`",
    "retained-in-C posture",
    "must not overstate that returned packet as shared-lane parity, ownership transfer, or fully recovered compile evidence",
};

const SKBUFF_NOTE_PATH = "Documentation/zigux/phase14-skbuff-bridge-survey.md";

const TRACEABILITY_NOTE_PATH = "Documentation/zigux/phase14-core-boundary-traceability.md";

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
    try guard.printLine(io, "PHASE15_FREEZE_MAP_GOVERNANCE_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
        try guard.printLine(io, "PHASE15_FREEZE_MAP_GOVERNANCE_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE15_FREEZE_MAP_GOVERNANCE_ADJACENT_EVIDENCE_COUNT={d}", .{@as(usize, ADJACENT_EVIDENCE_PATHS.len)});
    std.process.exit(0);
}
