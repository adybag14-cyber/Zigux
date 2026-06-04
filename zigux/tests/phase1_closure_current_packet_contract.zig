const std = @import("std");
const contract_options = @import("contract_options");

const reminder_packet_marker =
    "`PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,scripts/zigux/README.md,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-direct-anchor-manifest-gate.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py,scripts/zigux/validate-phase1-closure.py,zigux/tests/README.md,zigux/tests/build.zig,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_helpers_build.zig,zigux/tests/phase1_host_tools_smoke.zig,.github/workflows/zigux-bootstrap.yml,zigux/tests/fixtures/phase1_helper_manifest.json`";

const gap_packet_marker =
    "`PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`";

const expected_reminder_entries = [_][]const u8{
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

const expected_gap_entries = [_][]const u8{
    "scripts/zigux/validate-phase1.py",
    "scripts/zigux/check-phase1-parity.py",
    "zigux/tests/phase1_bench.zig",
    "zigux/tests/fixtures/phase1_bench_expectations.json",
    "zigux/tests/fixtures/phase1_helpers_c_harness.c",
};

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        allocator,
        .limited(2 * 1024 * 1024),
    );
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOf(u8, haystack[cursor..], needle)) |relative_index| {
        count += 1;
        cursor += relative_index + needle.len;
    }
    return count;
}

fn expectOnce(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(haystack, needle));
}

fn expectAbsent(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 0), countOccurrences(haystack, needle));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn indexOfRequired(haystack: []const u8, needle: []const u8) !usize {
    return std.mem.indexOf(u8, haystack, needle) orelse error.RequiredMarkerMissing;
}

test "closure note pins current reminder packet and parked gap packet exactly once" {
    const allocator = std.testing.allocator;
    const closure_text = try readFile(allocator, contract_options.closure_path);
    defer allocator.free(closure_text);

    try expectOnce(closure_text, reminder_packet_marker);
    try expectOnce(closure_text, gap_packet_marker);
    try expectOnce(closure_text, "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`");
    try expectOnce(closure_text, "`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`");
    try expectAbsent(closure_text, "`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`");
    try expectAbsent(closure_text, "`PHASE1_NEXT_SAFE_STEP=restore the missing phase1 closure note first`");
}

test "current reminder packet keeps closure validator current and broader Phase 1 replay parked" {
    const allocator = std.testing.allocator;
    const closure_text = try readFile(allocator, contract_options.closure_path);
    defer allocator.free(closure_text);

    for (expected_reminder_entries) |entry| {
        try expectContains(reminder_packet_marker, entry);
    }
    for (expected_gap_entries) |entry| {
        try expectContains(gap_packet_marker, entry);
        try std.testing.expect(std.mem.indexOf(u8, reminder_packet_marker, entry) == null);
    }

    try expectContains(closure_text, "broader closure-side validator and replay stack is only partially promoted");
    try expectContains(closure_text, "parked as historical closure-stack vocabulary");
    try expectContains(closure_text, "It still does not expose `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, or `make -C zigux phase1`");
}

test "bootstrap workflow runs Phase 1 closure after direct-anchor checks and before Phase 2 validation" {
    const allocator = std.testing.allocator;
    const workflow_text = try readFile(allocator, contract_options.workflow_path);
    defer allocator.free(workflow_text);

    const direct_owner_self = try indexOfRequired(workflow_text, "Self-test current Phase 1 direct-owner checker");
    const direct_owner_live = try indexOfRequired(workflow_text, "Check current Phase 1 direct-owner markers");
    const direct_anchor_self = try indexOfRequired(workflow_text, "Self-test current Phase 1 direct-anchor manifest gate");
    const direct_anchor_live = try indexOfRequired(workflow_text, "Check current Phase 1 direct-anchor manifest gate");
    const shared_reminder_self = try indexOfRequired(workflow_text, "Self-test current Phase 1 shared reminder checker");
    const shared_reminder_live = try indexOfRequired(workflow_text, "Check current Phase 1 shared reminder packet");
    const closure_self = try indexOfRequired(workflow_text, "Self-test current Phase 1 closure validator");
    const closure_live = try indexOfRequired(workflow_text, "Check current Phase 1 closure packet");
    const phase2_closure = try indexOfRequired(workflow_text, "Check current Phase 2 closure packet");

    try std.testing.expect(direct_owner_self < direct_owner_live);
    try std.testing.expect(direct_owner_live < direct_anchor_self);
    try std.testing.expect(direct_anchor_self < direct_anchor_live);
    try std.testing.expect(direct_anchor_live < shared_reminder_self);
    try std.testing.expect(shared_reminder_self < shared_reminder_live);
    try std.testing.expect(shared_reminder_live < closure_self);
    try std.testing.expect(closure_self < closure_live);
    try std.testing.expect(closure_live < phase2_closure);

    try expectOnce(workflow_text, "run: python3 scripts/zigux/validate-phase1-closure.py --self-test");
    try expectOnce(workflow_text, "\n        run: python3 scripts/zigux/validate-phase1-closure.py\n");
}
