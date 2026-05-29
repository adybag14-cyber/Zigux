const std = @import("std");

const readme_phase1_packet =
    \\  * current direct-readback Phase 1 reminder packet:
    \\- `scripts/zigux/check-phase1-bench.py`
    \\- `scripts/zigux/check-phase1-shared-reminder-packet.py`
    \\- `scripts/zigux/validate-phase1-closure.py`
    \\- `zigux/tests/build.zig`
    \\- `zigux/tests/phase1_helpers.zig`
    \\- `zigux/tests/phase1_helpers_build.zig`
    \\- `zigux/tests/phase1_host_tools_smoke.zig`
    \\- `.github/workflows/zigux-bootstrap.yml`
    \\- `zigux/tests/README.md`
    \\  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`
    \\  * current focused Phase 1 helper replay route: `zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig`
    \\  * keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`
;

const workflow_phase1_gates =
    \\      - name: Self-test current Phase 1 direct-owner checker
    \\        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test
    \\      - name: Check current Phase 1 direct-owner markers
    \\        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py
    \\      - name: Self-test current Phase 1 direct-anchor manifest gate
    \\        run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test
    \\      - name: Check current Phase 1 direct-anchor manifest gate
    \\        run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py
    \\      - name: Self-test current Phase 1 string review checker
    \\        run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test
    \\      - name: Check current Phase 1 string review packet
    \\        run: python3 scripts/zigux/check-phase1-string-review-packet.py
    \\      - name: Self-test current Phase 1 find-bit review checker
    \\        run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py --self-test
    \\      - name: Check current Phase 1 find-bit review packet
    \\        run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py
    \\      - name: Self-test current Phase 1 bitmap direct-anchor checker
    \\        run: python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py --self-test
    \\      - name: Check current Phase 1 bitmap direct-anchor packet
    \\        run: python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py
    \\      - name: Self-test current Phase 1 rbtree review checker
    \\        run: python3 scripts/zigux/check-phase1-rbtree-review-packet.py --self-test
    \\      - name: Check current Phase 1 rbtree review packet
    \\        run: python3 scripts/zigux/check-phase1-rbtree-review-packet.py
    \\      - name: Self-test current Phase 1 route summary checker
    \\        run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test
    \\      - name: Check current Phase 1 route summary packet
    \\        run: python3 scripts/zigux/check-phase1-route-summary-counts.py
    \\      - name: Self-test current Phase 1 bench checker
    \\        run: python3 scripts/zigux/check-phase1-bench.py --self-test
    \\      - name: Self-test current Phase 1 find-bit bench anchor checker
    \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test
    \\      - name: Check current Phase 1 find-bit bench anchor packet
    \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py
    \\      - name: Self-test current Phase 1 shared reminder checker
    \\        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test
    \\      - name: Check current Phase 1 shared reminder packet
    \\        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py
    \\      - name: Self-test current Phase 1 closure validator
    \\        run: python3 scripts/zigux/validate-phase1-closure.py --self-test
    \\      - name: Check current Phase 1 closure packet
    \\        run: python3 scripts/zigux/validate-phase1-closure.py
    \\      - name: Run current Phase 1 shared tests-root smoke
    \\        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig
;

const expected_workflow_runs = [_][]const u8{
    "python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
    "python3 scripts/zigux/check-phase1-direct-owner-markers.py",
    "python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test",
    "python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
    "python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
    "python3 scripts/zigux/check-phase1-string-review-packet.py",
    "python3 scripts/zigux/check-phase1-find-bit-review-packet.py --self-test",
    "python3 scripts/zigux/check-phase1-find-bit-review-packet.py",
    "python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py --self-test",
    "python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py",
    "python3 scripts/zigux/check-phase1-rbtree-review-packet.py --self-test",
    "python3 scripts/zigux/check-phase1-rbtree-review-packet.py",
    "python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    "python3 scripts/zigux/check-phase1-route-summary-counts.py",
    "python3 scripts/zigux/check-phase1-bench.py --self-test",
    "python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test",
    "python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py",
    "python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    "python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
    "python3 scripts/zigux/validate-phase1-closure.py --self-test",
    "python3 scripts/zigux/validate-phase1-closure.py",
    "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
};

const readme_gate_markers = [_][]const u8{
    "`scripts/zigux/check-phase1-bench.py`",
    "`scripts/zigux/check-phase1-shared-reminder-packet.py`",
    "`scripts/zigux/validate-phase1-closure.py`",
    "`zigux/tests/build.zig`",
    "`zigux/tests/phase1_helpers.zig`",
    "`zigux/tests/phase1_helpers_build.zig`",
    "`zigux/tests/phase1_host_tools_smoke.zig`",
    "`.github/workflows/zigux-bootstrap.yml`",
    "`zigux/tests/README.md`",
};

test "Phase 1 README packet names the workflow-facing tests-root gates in order" {
    try expectInOrder(readme_phase1_packet, &readme_gate_markers);
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(readme_phase1_packet, "current shared Phase 1 smoke route"));
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(readme_phase1_packet, "current focused Phase 1 helper replay route"));
    try std.testing.expect(std.mem.indexOf(u8, readme_phase1_packet, "thirteen helper ports remain closed") != null);
    try std.testing.expect(std.mem.indexOf(u8, readme_phase1_packet, "only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers") != null);
}

test "Phase 1 workflow keeps self-tests before matching packet checks" {
    try expectInOrder(workflow_phase1_gates, &expected_workflow_runs);

    const self_test_count = countOccurrences(workflow_phase1_gates, " --self-test");
    try std.testing.expectEqual(@as(usize, 11), self_test_count);
    try std.testing.expectEqual(@as(usize, expected_workflow_runs.len), countOccurrences(workflow_phase1_gates, "        run: "));
}

test "README and workflow agree on the shared reminder and smoke gate names" {
    const shared_reminder = "scripts/zigux/check-phase1-shared-reminder-packet.py";
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(readme_phase1_packet, shared_reminder));
    try std.testing.expectEqual(@as(usize, 2), countOccurrences(workflow_phase1_gates, shared_reminder));

    const smoke_route = "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig";
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(readme_phase1_packet, smoke_route));
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(workflow_phase1_gates, smoke_route));
}

fn expectInOrder(haystack: []const u8, needles: []const []const u8) !void {
    var cursor: usize = 0;
    for (needles) |needle| {
        const relative = std.mem.indexOf(u8, haystack[cursor..], needle) orelse return error.ExpectedMarkerMissing;
        cursor += relative + needle.len;
    }
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOf(u8, haystack[cursor..], needle)) |relative| {
        count += 1;
        cursor += relative + needle.len;
    }
    return count;
}
