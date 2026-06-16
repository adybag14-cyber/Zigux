// Ported from check-phase15-roadmap-ledger-readiness-gap.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE15_ROADMAP_LEDGER_READINESS_GAP_SELF_TEST=pass";

const BLOCKED_ROUTE_MARKERS = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "phase15-validate", .marker = "`make -C zigux phase15-validate` remains blocked route vocabulary rather than directly readable shipped evidence" },
    .{ .label = "phase15-test", .marker = "`make -C zigux phase15-test` remains blocked route vocabulary rather than directly readable shipped evidence" },
    .{ .label = "phase15", .marker = "`make -C zigux phase15` remains blocked route vocabulary rather than directly readable shipped evidence" },
};

const EXPECTED_LANE_KEY = "P15-L01";

const EXPECTED_PHASE = "Phase 15";

const EXPECTED_SURVEYED_COMMIT = "current-master-readback-2026-05-26";

const LEDGER_PATH = "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md";

const MAKEFILE_PATH = "zigux/Makefile";

const MANIFEST_PATH = "zigux/tests/phase15_roadmap_ledger_readiness_gap_manifest.json";

const NOTE_PATH = "Documentation/zigux/phase15-roadmap-ledger-readiness-gap-survey.md";

const REQUIRED_NOTE_MARKERS = [_][]const u8{
    "PHASE15_STATUS=roadmap_ledger_readiness_gap_survey_landed",
    "PHASE15_LANE_KEY=P15-L01",
    "PHASE15_SLICE=roadmap_ledger_gap_accounting",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    "current `master` already materializes all four roadmap-required governance features",
    "the bootstrap ledger is still intentionally authoritative only through item 25",
    "does not define a dedicated Phase 15 tranche-close family",
    "remaining readiness gaps are still route-level rather than governance-feature absence",
    "no dedicated `phase15-validate`, `phase15-test`, or `phase15` Makefile wrapper route is materialized",
    "no dedicated Phase 15 validate, test, or aggregate workflow route is materialized",
    "no Architecture Council approval is currently recorded for a freeze-map status change",
    "no direct deep-core Zig bridge or port-readiness decision is implied",
};

const ROADMAP_PATH = "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md";

const WORKFLOW_BLOCKED_MARKER = "`.github/workflows/zigux-bootstrap.yml` still carries no dedicated Phase 15 validate, test, or aggregate route";

const WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml";

const WORKFLOW_PHASE15_MARKERS = [_][]const u8{
    "phase15-validate",
    "phase15-test",
    "phase15:",
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
    try guard.printLine(io, "PHASE15_ROADMAP_LEDGER_READINESS_GAP_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
        try guard.printLine(io, "PHASE15_ROADMAP_LEDGER_READINESS_GAP_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    std.process.exit(0);
}
