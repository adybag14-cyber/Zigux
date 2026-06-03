const std = @import("std");

const closure_note =
    \\# Phase 1 Closure
    \\
    \\## Current Reminder Packet
    \\
    \\- `PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,scripts/zigux/README.md,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-direct-anchor-manifest-gate.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py,scripts/zigux/validate-phase1-closure.py,zigux/tests/README.md,zigux/tests/build.zig,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_helpers_build.zig,zigux/tests/phase1_host_tools_smoke.zig,.github/workflows/zigux-bootstrap.yml,zigux/tests/fixtures/phase1_helper_manifest.json`
    \\
    \\## Broader Closure Companions
    \\
    \\The older validator-first and replay-side closure companions remain broader closure-stack references rather than active current reminder-packet proof.
    \\
    \\- `scripts/zigux/validate-phase1.py`
    \\- `scripts/zigux/check-phase1-parity.py`
    \\- `zigux/tests/phase1_bench.zig`
    \\- `zigux/tests/fixtures/phase1_bench_expectations.json`
    \\- `zigux/tests/fixtures/phase1_helpers_c_harness.c`
    \\
    \\- `PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`
    \\
    \\This note keeps those broader companions parked as historical closure-stack vocabulary until direct current-master rereads restore them.
;

const expected_reminder_packet = [_][]const u8{
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase1-string-review-packet.py",
    "scripts/zigux/check-phase1-direct-owner-markers.py",
    "scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
    "scripts/zigux/check-phase1-bench.py",
    "scripts/zigux/check-phase1-shared-reminder-packet.py",
    "scripts/zigux/validate-phase1-closure.py",
    "zigux/tests/README.md",
    "zigux/tests/build.zig",
    "zigux/tests/phase1_helpers.zig",
    "zigux/tests/phase1_helpers_build.zig",
    "zigux/tests/phase1_host_tools_smoke.zig",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
};

const expected_gap_packet = [_][]const u8{
    "scripts/zigux/validate-phase1.py",
    "scripts/zigux/check-phase1-parity.py",
    "zigux/tests/phase1_bench.zig",
    "zigux/tests/fixtures/phase1_bench_expectations.json",
    "zigux/tests/fixtures/phase1_helpers_c_harness.c",
};

fn extractPacket(marker: []const u8) []const u8 {
    const marker_start = std.mem.indexOf(u8, closure_note, marker) orelse return "";
    const packet_start = marker_start + marker.len;
    const packet_tail = closure_note[packet_start..];
    const packet_end = std.mem.indexOfScalar(u8, packet_tail, '`') orelse return "";
    return packet_tail[0..packet_end];
}

fn expectCsvEquals(packet: []const u8, expected: []const []const u8) !void {
    var fields = std.mem.splitScalar(u8, packet, ',');
    for (expected) |entry| {
        const actual = fields.next() orelse return error.MissingPacketEntry;
        try std.testing.expectEqualStrings(entry, actual);
    }
    try std.testing.expect(fields.next() == null);
}

fn containsEntry(packet: []const u8, needle: []const u8) bool {
    var fields = std.mem.splitScalar(u8, packet, ',');
    while (fields.next()) |entry| {
        if (std.mem.eql(u8, entry, needle)) return true;
    }
    return false;
}

test "phase1 closure gap packet stays parked outside current reminder packet" {
    const reminder_packet = extractPacket("PHASE1_CURRENT_REMINDER_PACKET=");
    const gap_packet = extractPacket("PHASE1_CURRENT_GAP_PACKET=");

    try expectCsvEquals(reminder_packet, &expected_reminder_packet);
    try expectCsvEquals(gap_packet, &expected_gap_packet);

    for (expected_gap_packet) |gap_entry| {
        try std.testing.expect(!containsEntry(reminder_packet, gap_entry));
        try std.testing.expect(containsEntry(gap_packet, gap_entry));
    }
}

test "phase1 closure note states validator-first companions are historical proof only" {
    try std.testing.expect(std.mem.indexOf(
        u8,
        closure_note,
        "broader closure-stack references rather than active current reminder-packet proof",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        closure_note,
        "parked as historical closure-stack vocabulary until direct current-master rereads restore them",
    ) != null);
}
