const std = @import("std");

const workflow = @embedFile("fixtures/phase1_workflow_bench_live_guard.yml");

const ordered_markers = [_][]const u8{
    "      - name: Self-test current Phase 1 route summary checker\n        run: zig run scripts/zigux/check_phase1_route_summary_counts.zig -- --self-test",
    "      - name: Check current Phase 1 route summary packet\n        run: zig run scripts/zigux/check_phase1_route_summary_counts.zig",
    "      - name: Self-test current Phase 1 bench checker\n        run: zig run scripts/zigux/check_phase1_bench.zig -- --self-test",
    "      - name: Check current Phase 1 bench packet\n        run: zig run scripts/zigux/check_phase1_bench.zig",
    "      - name: Self-test current Phase 1 bench live-check workflow guard\n        run: zig run scripts/zigux/check_phase1_bench_live_check_workflow.zig -- --self-test",
    "      - name: Check current Phase 1 bench live-check workflow guard packet\n        run: zig run scripts/zigux/check_phase1_bench_live_check_workflow.zig",
    "      - name: Self-test current Phase 1 find-bit bench anchor checker\n        run: zig run scripts/zigux/check_phase1_find_bit_bench_anchors.zig -- --self-test",
    "      - name: Check current Phase 1 find-bit bench anchor packet\n        run: zig run scripts/zigux/check_phase1_find_bit_bench_anchors.zig",
    "      - name: Self-test current Phase 1 shared reminder checker\n        run: zig run scripts/zigux/check_phase1_shared_reminder_packet.zig -- --self-test",
    "      - name: Check current Phase 1 shared reminder packet\n        run: zig run scripts/zigux/check_phase1_shared_reminder_packet.zig",
    "      - name: Self-test current Phase 1 closure validator\n        run: zig run scripts/zigux/validate_phase1_closure.zig -- --self-test",
    "      - name: Check current Phase 1 closure packet\n        run: zig run scripts/zigux/validate_phase1_closure.zig",
    "      - name: Run current Phase 1 shared tests-root smoke\n        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
};

const stale_command_markers = [_][]const u8{
    "zig run scripts/zigux/check_phase1_bench_live_check_workflow.zig -- --root",
    "zig run scripts/zigux/check_phase1_bench_live_check_workflow.zig -- --allow-missing",
    "zig run scripts/zigux/check_phase1_find_bit_bench_anchors.zig -- --root",
    "zig run scripts/zigux/check_phase1_find_bit_bench_anchors.zig -- --allow-missing",
};

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOf(u8, haystack[cursor..], needle)) |offset| {
        count += 1;
        cursor += offset + needle.len;
    }
    return count;
}

test "bench live workflow cluster is exact and ordered" {
    var previous: usize = 0;
    for (ordered_markers, 0..) |marker, index| {
        try std.testing.expectEqual(@as(usize, 1), countOccurrences(workflow, marker));
        const position = std.mem.indexOf(u8, workflow, marker) orelse return error.MissingMarker;
        if (index != 0) {
            try std.testing.expect(position > previous);
        }
        previous = position;
    }
}

test "bench live workflow guard keeps live commands argument-free" {
    for (stale_command_markers) |marker| {
        try std.testing.expectEqual(@as(usize, 0), countOccurrences(workflow, marker));
    }
}

test "bench live guard stays between route summary and shared reminder gates" {
    const route_summary = std.mem.indexOf(u8, workflow, "check-phase1-route-summary-counts.py") orelse return error.MissingRouteSummary;
    const bench_live = std.mem.indexOf(u8, workflow, "check-phase1-bench-live-check-workflow.py") orelse return error.MissingBenchLiveGuard;
    const find_bit_bench = std.mem.indexOf(u8, workflow, "check-phase1-find-bit-bench-anchors.py") orelse return error.MissingFindBitBenchGuard;
    const shared_reminder = std.mem.indexOf(u8, workflow, "check-phase1-shared-reminder-packet.py") orelse return error.MissingSharedReminder;

    try std.testing.expect(route_summary < bench_live);
    try std.testing.expect(bench_live < find_bit_bench);
    try std.testing.expect(find_bit_bench < shared_reminder);
}
