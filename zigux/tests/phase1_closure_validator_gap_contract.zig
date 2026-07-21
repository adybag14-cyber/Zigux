const std = @import("std");

const current_reminder_packet =
    "Documentation/zigux/phase1-closure.md,Documentation/zigux/phase1-host-helper-lane-sequencing.md," ++
    "Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,scripts/zigux/README.md," ++
    "scripts\zigux/check_phase1_string_review_packet.zig,scripts\zigux/check_phase1_direct_owner_markers.zig," ++
    "scripts\zigux/check_phase1_direct_anchor_manifest_gate.zig,scripts\zigux/check_phase1_bench.zig," ++
    "scripts\zigux/check_phase1_shared_reminder_packet.zig,scripts\zigux/validate_phase1_closure.zig," ++
    "zigux/tests/README.md,zigux/tests/build.zig,zigux/tests/phase1_helpers.zig," ++
    "zigux/tests/phase1_helpers_build.zig,zigux/tests/phase1_host_tools_smoke.zig," ++
    ".github/workflows/zigux-bootstrap.yml,zigux/tests/fixtures/phase1_helper_manifest.json";

const current_gap_packet =
    "scripts\zigux/validate_phase1.zig,scripts\zigux/check_phase1_parity.zig," ++
    "zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json," ++
    "zigux/tests/fixtures/phase1_helpers_c_harness.c";

const parked_gap_companions = [_][]const u8{
    "scripts\zigux/validate_phase1.zig",
    "scripts\zigux/check_phase1_parity.zig",
    "zigux/tests/phase1_bench.zig",
    "zigux/tests/fixtures/phase1_bench_expectations.json",
    "zigux/tests/fixtures/phase1_helpers_c_harness.c",
};

const active_validator_and_route_markers = [_][]const u8{
    "PHASE1_CLOSURE_VALIDATOR=zig run scripts/zigux/validate_phase1_closure.zig",
    "PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master",
    "PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    "PHASE1_ROUTE_SUMMARY_GUARD=zig run scripts/zigux/check_phase1_route_summary_counts.zig",
};

fn packetContains(packet: []const u8, path: []const u8) bool {
    var fields = std.mem.splitScalar(u8, packet, ',');
    while (fields.next()) |field| {
        if (std.mem.eql(u8, field, path)) return true;
    }
    return false;
}

fn packetCount(packet: []const u8) usize {
    if (packet.len == 0) return 0;

    var count: usize = 1;
    for (packet) |byte| {
        if (byte == ',') count += 1;
    }
    return count;
}

test "broader closure companions stay parked outside the current reminder packet" {
    try std.testing.expectEqual(@as(usize, 18), packetCount(current_reminder_packet));
    try std.testing.expectEqual(@as(usize, parked_gap_companions.len), packetCount(current_gap_packet));

    for (parked_gap_companions) |path| {
        try std.testing.expect(packetContains(current_gap_packet, path));
        try std.testing.expect(!packetContains(current_reminder_packet, path));
    }
}

test "current validator route remains narrow while the broader validator-first stack is parked" {
    try std.testing.expect(packetContains(current_reminder_packet, "scripts\zigux/validate_phase1_closure.zig"));
    try std.testing.expect(packetContains(current_reminder_packet, "scripts\zigux/check_phase1_bench.zig"));
    try std.testing.expect(packetContains(current_reminder_packet, "scripts\zigux/check_phase1_shared_reminder_packet.zig"));
    try std.testing.expect(packetContains(current_reminder_packet, "zigux/tests/build.zig"));
    try std.testing.expect(packetContains(current_reminder_packet, "zigux/tests/phase1_host_tools_smoke.zig"));

    try std.testing.expect(!packetContains(current_gap_packet, "scripts\zigux/validate_phase1_closure.zig"));
    try std.testing.expect(!packetContains(current_gap_packet, "zigux/tests/phase1_host_tools_smoke.zig"));
}

test "closure validator command markers distinguish current proof from historical gap evidence" {
    for (active_validator_and_route_markers) |marker| {
        try std.testing.expect(std.mem.indexOf(u8, marker, "PHASE1_") != null);
    }

    try std.testing.expect(std.mem.indexOf(u8, active_validator_and_route_markers[0], "validate-phase1-closure.py") != null);
    try std.testing.expect(std.mem.indexOf(u8, active_validator_and_route_markers[1], "available_current_master") != null);
    try std.testing.expect(std.mem.indexOf(u8, active_validator_and_route_markers[2], "phase1-host-tools-smoke") != null);
    try std.testing.expect(std.mem.indexOf(u8, active_validator_and_route_markers[3], "check-phase1-route-summary-counts.py") != null);
}
