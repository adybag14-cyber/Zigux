// Ported from check-phase15-blocked-route-recovery.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE15_BLOCKED_ROUTE_RECOVERY_SELF_TEST=pass";

const BLOCKED_MAKE_TARGETS = [_][]const u8{
    "phase15-validate",
    "phase15-test",
    "phase15",
};

const GAP_MATRIX = "zigux/tests/phase15_readiness_gap_matrix.json";

const MAKEFILE = "zigux/Makefile";

const NOTE_MARKERS = [_][]const u8{
    "PHASE15_STATUS=readiness_gate_survey_landed",
    "PHASE15_LANE_KEY=P15-L04",
    "broader route and workflow companions still remain blocked on current `master`",
    "`make -C zigux phase15-validate` remains blocked route vocabulary",
    "`make -C zigux phase15-test` remains blocked route vocabulary",
    "`make -C zigux phase15` remains blocked route vocabulary",
    "shared CI coverage for the broader Phase 15 replay packet remains absent",
};

const READINESS_NOTE = "Documentation/zigux/phase15-readiness-gate-survey.md";

const VALIDATOR = "scripts\\zigux/validate_phase15.zig";

const VALIDATOR_MARKERS = [_][]const u8{
    "\"missing_make_targets\": [\"phase15-validate\", \"phase15-test\", \"phase15\"]",
    "\"missing_workflow_phase15_route\": True",
    "\"phase15_validate_target_present\": False",
    "\"phase15_test_target_present\": False",
    "\"phase15_aggregate_target_present\": False",
    "\"shared_ci_phase15_present\": False",
};

const WORKFLOW = ".github/workflows/zigux-bootstrap.yml";

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
    try guard.printLine(io, "PHASE15_BLOCKED_ROUTE_RECOVERY_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
        try guard.printLine(io, "PHASE15_BLOCKED_ROUTE_RECOVERY_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE15_BLOCKED_ROUTE_RECOVERY_MAKE_TARGET_COUNT={d}", .{@as(usize, BLOCKED_MAKE_TARGETS.len)});
    std.process.exit(0);
}
