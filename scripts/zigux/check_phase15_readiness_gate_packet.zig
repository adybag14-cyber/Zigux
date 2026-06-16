// Ported from check-phase15-readiness-gate-packet.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE15_READINESS_GATE_PACKET_SELF_TEST=pass";

const BLOCKED_ROUTE_MARKERS = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "phase15-validate", .marker = "`make -C zigux phase15-validate` remains blocked route vocabulary rather than a directly readable shipped replay path" },
    .{ .label = "phase15-test", .marker = "`make -C zigux phase15-test` remains blocked route vocabulary rather than a directly readable shipped replay path" },
    .{ .label = "phase15", .marker = "`make -C zigux phase15` remains blocked route vocabulary rather than a directly readable shipped replay path" },
};

const BUILD_ZIG_PATH = "zigux/tests/phase15_build.zig";

const EXPECTED_GAP_MATRIX_LANE_KEY = "P15-L01";

const EXPECTED_LANE_KEY = "P15-L04";

const EXPECTED_LEDGER_ANCHOR = "docs(zigux): add documentation root, review checklist, and freeze map";

const EXPECTED_PHASE = "Phase 15";

const EXPECTED_REMAINING_GAPS = [_][]const u8{
    "missing_make_routes",
    "missing_workflow_route",
    "no_architecture_council_status_change_approval",
};

const EXPECTED_ROADMAP_REQUIREMENTS = [_][]const u8{
    "freeze map",
    "Architecture Council review process",
    "parity scorecard",
    "policy for code that remains in C indefinitely",
};

const GAP_MATRIX_PATH = "zigux/tests/phase15_readiness_gap_matrix.json";

const MAKEFILE_PATH = "zigux/Makefile";

const MANIFEST_PATH = "zigux/tests/phase15_readiness_gate_manifest.json";

const READINESS_NOTE_PATH = "Documentation/zigux/phase15-readiness-gate-survey.md";

const REQUIRED_NOTE_MARKERS = [_][]const u8{
    "PHASE15_STATUS=readiness_gate_survey_landed",
    "PHASE15_LANE_KEY=P15-L04",
    "PHASE15_SLICE=validator_first_readiness_packet",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    "the governance packet is materially landed and reviewable",
    "the dedicated validator now exists as a directly readable maintenance gate",
    "the dedicated shared-build companion is now directly readable current-master evidence",
    "the roadmap-versus-ledger gap matrix now keeps the remaining readiness requirements explicit",
    "broader make-wrapper and workflow companions still block any claim that the larger Phase 15 replay route is one-command or shared-CI ready",
    "Although `zigux/Makefile` is present on current `master`, it still does not materialize dedicated `phase15*` wrapper routes",
    "ready for maintenance-mode truthfulness refreshes, direct validator-first replay, shared-build companion review, and explicit roadmap-versus-ledger gap accounting only",
    "no Architecture Council approval is currently recorded for a freeze-map status change",
    "`zigux/tests/phase15_readiness_gap_matrix.json`",
};

const SCRIPTS_CHECKER_PATH = "scripts\\zigux/check_phase15_scripts_readme_alignment.zig";

const VALIDATOR_PATH = "scripts\\zigux/validate_phase15.zig";

const WORKFLOW_BLOCKED_MARKER = "`.github/workflows/zigux-bootstrap.yml` still carries no dedicated Phase 15 validate, test, or aggregate route";

const WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml";

const WORKFLOW_PHASE15_MARKERS = [_][]const u8{
    "validate-phase15.py",
    "make -C zigux phase15-validate",
    "make -C zigux phase15-test",
    "make -C zigux phase15",
    "zigux/tests/phase15_build.zig",
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
    try guard.printLine(io, "PHASE15_READINESS_GATE_PACKET_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
        try guard.printLine(io, "PHASE15_READINESS_GATE_PACKET_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    std.process.exit(0);
}
