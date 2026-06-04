const std = @import("std");
const workflow_options = @import("workflow_options");

const workflow_text = workflow_options.workflow_text;

const Marker = struct {
    label: []const u8,
    text: []const u8,
};

const route_summary_check = Marker{
    .label = "route_summary_check",
    .text = "      - name: Check current Phase 1 route summary packet\n        run: python3 scripts/zigux/check-phase1-route-summary-counts.py\n",
};

const bench_self_test = Marker{
    .label = "bench_self_test",
    .text = "      - name: Self-test current Phase 1 bench checker\n        run: python3 scripts/zigux/check-phase1-bench.py --self-test\n",
};

const bench_live_check = Marker{
    .label = "bench_live_check",
    .text = "      - name: Check current Phase 1 bench packet\n        run: python3 scripts/zigux/check-phase1-bench.py\n",
};

const find_bit_bench_self_test = Marker{
    .label = "find_bit_bench_self_test",
    .text = "      - name: Self-test current Phase 1 find-bit bench anchor checker\n        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test\n",
};

const find_bit_bench_check = Marker{
    .label = "find_bit_bench_check",
    .text = "      - name: Check current Phase 1 find-bit bench anchor packet\n        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py\n",
};

const shared_reminder_self_test = Marker{
    .label = "shared_reminder_self_test",
    .text = "      - name: Self-test current Phase 1 shared reminder checker\n        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test\n",
};

const shared_reminder_check = Marker{
    .label = "shared_reminder_check",
    .text = "      - name: Check current Phase 1 shared reminder packet\n        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py\n",
};

const closure_self_test = Marker{
    .label = "closure_self_test",
    .text = "      - name: Self-test current Phase 1 closure validator\n        run: python3 scripts/zigux/validate-phase1-closure.py --self-test\n",
};

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var start: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, start, needle)) |index| {
        count += 1;
        start = index + needle.len;
    }
    return count;
}

fn requireOnce(marker: Marker) !usize {
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(workflow_text, marker.text));
    return std.mem.indexOf(u8, workflow_text, marker.text) orelse error.MissingWorkflowMarker;
}

fn optionalIndex(marker: Marker) !?usize {
    const count = countOccurrences(workflow_text, marker.text);
    try std.testing.expect(count <= 1);
    if (count == 0) return null;
    return std.mem.indexOf(u8, workflow_text, marker.text) orelse error.MissingWorkflowMarker;
}

fn requireBefore(left: Marker, right: Marker) !void {
    const left_index = try requireOnce(left);
    const right_index = try requireOnce(right);
    try std.testing.expect(left_index < right_index);
}

test "phase1 bench handoff flows into find-bit bench before shared reminder" {
    try requireBefore(route_summary_check, bench_self_test);
    try requireBefore(bench_self_test, find_bit_bench_self_test);
    try requireBefore(find_bit_bench_self_test, find_bit_bench_check);
    try requireBefore(find_bit_bench_check, shared_reminder_self_test);
    try requireBefore(shared_reminder_self_test, shared_reminder_check);
    try requireBefore(shared_reminder_check, closure_self_test);
}

test "optional live bench packet stays between bench self-test and find-bit anchor" {
    const bench_index = try requireOnce(bench_self_test);
    const find_bit_index = try requireOnce(find_bit_bench_self_test);

    if (try optionalIndex(bench_live_check)) |live_index| {
        try std.testing.expect(bench_index < live_index);
        try std.testing.expect(live_index < find_bit_index);
    }
}

test "shared reminder does not creep into the bench-anchor subcluster" {
    const bench_index = try requireOnce(bench_self_test);
    const shared_index = try requireOnce(shared_reminder_self_test);
    const bench_cluster = workflow_text[bench_index..shared_index];

    try std.testing.expectEqual(@as(usize, 1), countOccurrences(bench_cluster, "check-phase1-bench.py --self-test"));
    try std.testing.expect(countOccurrences(bench_cluster, "check-phase1-bench.py\n") <= 1);
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(bench_cluster, "check-phase1-find-bit-bench-anchors.py --self-test"));
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(bench_cluster, "check-phase1-find-bit-bench-anchors.py\n"));
    try std.testing.expectEqual(@as(usize, 0), countOccurrences(bench_cluster, "check-phase1-shared-reminder-packet.py"));
    try std.testing.expectEqual(@as(usize, 0), countOccurrences(bench_cluster, "phase1-host-tools-smoke"));
}
