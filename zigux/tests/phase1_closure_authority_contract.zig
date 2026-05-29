const std = @import("std");
const testing = std.testing;

const closure_authority_packet =
    \\current authority: the committed helper manifest, this closure note, the narrow closure validator, the direct-anchor manifest gate, the shipped bench checker, the shipped shared reminder checker, the live owner-map reminders, and the shared tests-root smoke route remain the trustworthy current-master sources for the closed helper tranche, while the route-summary checker stays an adjacent workflow and Makefile guard.
    \\
    \\`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`
    \\`PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`
    \\`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`
    \\`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`
    \\`PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py exact-checks the current direct-anchor helper manifest packet for bitmap, find_bit, rbtree, and string and then reruns the dedicated rbtree direct-anchor checker`
;

const validator_required_surface_packet =
    \\PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
    \\PHASE1_LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
    \\DIRECT_OWNER_CHECKER_REL = Path("scripts/zigux/check-phase1-direct-owner-markers.py")
    \\DIRECT_ANCHOR_MANIFEST_GATE_REL = Path("scripts/zigux/check-phase1-direct-anchor-manifest-gate.py")
    \\ROUTE_SUMMARY_CHECKER_REL = Path("scripts/zigux/check-phase1-route-summary-counts.py")
    \\BENCH_CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")
    \\SHARED_REMINDER_CHECKER_REL = Path("scripts/zigux/check-phase1-shared-reminder-packet.py")
    \\TESTS_BUILD_REL = Path("zigux/tests/build.zig")
    \\PHASE1_SMOKE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")
    \\WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
    \\MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
    \\ZIGUX_MAKEFILE_REL = Path("zigux/Makefile")
    \\REQUIRED_FILES = (
    \\    PHASE1_CLOSURE_REL,
    \\    PHASE1_LANE_NOTE_REL,
    \\    DIRECT_OWNER_CHECKER_REL,
    \\    DIRECT_ANCHOR_MANIFEST_GATE_REL,
    \\    ROUTE_SUMMARY_CHECKER_REL,
    \\    BENCH_CHECKER_REL,
    \\    SHARED_REMINDER_CHECKER_REL,
    \\    TESTS_BUILD_REL,
    \\    PHASE1_SMOKE_REL,
    \\    WORKFLOW_REL,
    \\    MANIFEST_REL,
    \\    ZIGUX_MAKEFILE_REL,
    \\)
;

const authority_surfaces = [_]AuthoritySurface{
    .{ .phrase = "committed helper manifest", .validator_symbol = "MANIFEST_REL", .path = "zigux/tests/fixtures/phase1_helper_manifest.json" },
    .{ .phrase = "this closure note", .validator_symbol = "PHASE1_CLOSURE_REL", .path = "Documentation/zigux/phase1-closure.md" },
    .{ .phrase = "narrow closure validator", .marker = "PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py" },
    .{ .phrase = "direct-anchor manifest gate", .validator_symbol = "DIRECT_ANCHOR_MANIFEST_GATE_REL", .path = "scripts/zigux/check-phase1-direct-anchor-manifest-gate.py" },
    .{ .phrase = "shipped bench checker", .validator_symbol = "BENCH_CHECKER_REL", .path = "scripts/zigux/check-phase1-bench.py" },
    .{ .phrase = "shipped shared reminder checker", .validator_symbol = "SHARED_REMINDER_CHECKER_REL", .path = "scripts/zigux/check-phase1-shared-reminder-packet.py" },
    .{ .phrase = "live owner-map reminders", .validator_symbol = "DIRECT_OWNER_CHECKER_REL", .path = "scripts/zigux/check-phase1-direct-owner-markers.py" },
    .{ .phrase = "shared tests-root smoke route", .validator_symbol = "PHASE1_SMOKE_REL", .path = "zigux/tests/phase1_host_tools_smoke.zig" },
};

const adjacent_guard_surfaces = [_]AuthoritySurface{
    .{ .phrase = "route-summary checker", .validator_symbol = "ROUTE_SUMMARY_CHECKER_REL", .path = "scripts/zigux/check-phase1-route-summary-counts.py" },
    .{ .phrase = "workflow", .validator_symbol = "WORKFLOW_REL", .path = ".github/workflows/zigux-bootstrap.yml" },
    .{ .phrase = "Makefile guard", .validator_symbol = "ZIGUX_MAKEFILE_REL", .path = "zigux/Makefile" },
};

const AuthoritySurface = struct {
    phrase: []const u8,
    validator_symbol: ?[]const u8 = null,
    path: ?[]const u8 = null,
    marker: ?[]const u8 = null,
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, left: []const u8, right: []const u8) !void {
    const left_index = std.mem.indexOf(u8, haystack, left) orelse return error.MissingLeftNeedle;
    const right_index = std.mem.indexOf(u8, haystack, right) orelse return error.MissingRightNeedle;
    try testing.expect(left_index < right_index);
}

test "closure note names the current authority surfaces before adjacent route-summary work" {
    try expectContains(closure_authority_packet, "current authority:");
    try expectContains(closure_authority_packet, "trustworthy current-master sources for the closed helper tranche");

    inline for (authority_surfaces) |surface| {
        try expectContains(closure_authority_packet, surface.phrase);
        if (surface.marker) |marker| {
            try expectContains(closure_authority_packet, marker);
        }
    }

    try expectContains(closure_authority_packet, "route-summary checker stays an adjacent workflow and Makefile guard");
    try expectBefore(closure_authority_packet, "shared tests-root smoke route", "route-summary checker stays an adjacent workflow and Makefile guard");
}

test "validator required-files packet backs each named authority surface" {
    inline for (authority_surfaces) |surface| {
        if (surface.validator_symbol) |symbol| {
            try expectContains(validator_required_surface_packet, symbol);
            try expectContains(validator_required_surface_packet, surface.path.?);
        }
    }

    try expectContains(validator_required_surface_packet, "REQUIRED_FILES = (");
    try expectContains(validator_required_surface_packet, "PHASE1_CLOSURE_REL");
    try expectContains(validator_required_surface_packet, "MANIFEST_REL");
    try expectBefore(validator_required_surface_packet, "PHASE1_CLOSURE_REL =", "REQUIRED_FILES = (");
    try expectBefore(validator_required_surface_packet, "MANIFEST_REL =", "REQUIRED_FILES = (");
}

test "adjacent route-summary guard stays required but outside closure authority" {
    try expectContains(closure_authority_packet, "PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py");

    inline for (adjacent_guard_surfaces) |surface| {
        try expectContains(closure_authority_packet, surface.phrase);
        try expectContains(validator_required_surface_packet, surface.validator_symbol.?);
        try expectContains(validator_required_surface_packet, surface.path.?);
    }

    try expectContains(validator_required_surface_packet, "TESTS_BUILD_REL");
    try expectContains(validator_required_surface_packet, "zigux/tests/build.zig");
    try expectBefore(validator_required_surface_packet, "ROUTE_SUMMARY_CHECKER_REL", "WORKFLOW_REL");
    try expectBefore(validator_required_surface_packet, "WORKFLOW_REL", "ZIGUX_MAKEFILE_REL");
}
