const std = @import("std");

const phase4_tail_markers = [_][]const u8{
    "      - name: Self-test current Phase 4 artifact-diff determinism checker\n        run: python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test",
    "      - name: Check current Phase 4 artifact-diff determinism packet\n        run: python3 scripts/zigux/check-phase4-artifact-diff-determinism.py",
    "      - name: Self-test current Phase 4 artifact-diff validator replay checker\n        run: python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py --self-test",
    "      - name: Check current Phase 4 artifact-diff validator replay packet\n        run: python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py",
};

const phase6_markers = [_][]const u8{
    "      - name: Validate current Phase 6 helper packet\n        run: make -C zigux phase6-validate",
    "      - name: Run current Phase 6 leaf helper tests\n        run: zig build test --build-file zigux/tests/phase6_build.zig --summary all",
    "      - name: Run current Phase 6 shared perf route\n        run: make -C zigux phase6-perf",
};

const phase8_markers = [_][]const u8{
    "      - name: Validate Phase 8 tooling routes\n        run: make -C zigux phase8-validate",
    "      - name: Run focused Phase 8 exec-cmd tests\n        run: make -C zigux phase8-exec-cmd-test",
    "      - name: Run focused Phase 8 libbpf segment tests\n        run: make -C zigux phase8-libbpf-segments-test",
    "      - name: Run Phase 8 tooling tests\n        run: make -C zigux phase8-test",
};

const phase9_entry_markers = [_][]const u8{
    "      - name: Self-test current Phase 9 review-checklist boundaries checker\n        run: python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py --self-test",
    "      - name: Check current Phase 9 review-checklist boundaries packet\n        run: python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py",
};

fn markerIndex(source: []const u8, marker: []const u8) !usize {
    return std.mem.indexOf(u8, source, marker) orelse error.MissingWorkflowMarker;
}

fn expectOrdered(source: []const u8, markers: []const []const u8) !void {
    var previous: ?usize = null;
    for (markers) |marker| {
        const current = try markerIndex(source, marker);
        if (previous) |prev| {
            try std.testing.expect(current > prev);
        }
        previous = current;
    }
}

fn readWorkflowSource(allocator: std.mem.Allocator) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        ".github/workflows/zigux-bootstrap.yml",
        allocator,
        .limited(1024 * 1024),
    );
}

test "phase4 artifact-diff gates hand off to phase6 helper routes before phase8 tooling" {
    const workflow_source = try readWorkflowSource(std.testing.allocator);
    defer std.testing.allocator.free(workflow_source);

    try expectOrdered(workflow_source, &phase4_tail_markers);
    try expectOrdered(workflow_source, &phase6_markers);
    try expectOrdered(workflow_source, &phase8_markers);

    const phase4_tail_end = try markerIndex(workflow_source, phase4_tail_markers[phase4_tail_markers.len - 1]);
    const phase6_start = try markerIndex(workflow_source, phase6_markers[0]);
    const phase6_end = try markerIndex(workflow_source, phase6_markers[phase6_markers.len - 1]);
    const phase8_start = try markerIndex(workflow_source, phase8_markers[0]);

    try std.testing.expect(phase4_tail_end < phase6_start);
    try std.testing.expect(phase6_end < phase8_start);
}

test "phase6 helper packet keeps validate, tests, and perf in order" {
    const workflow_source = try readWorkflowSource(std.testing.allocator);
    defer std.testing.allocator.free(workflow_source);

    const validate = try markerIndex(workflow_source, phase6_markers[0]);
    const tests = try markerIndex(workflow_source, phase6_markers[1]);
    const perf = try markerIndex(workflow_source, phase6_markers[2]);

    try std.testing.expect(validate < tests);
    try std.testing.expect(tests < perf);
}

test "phase8 tooling routes stay complete and ahead of phase9 entry checks" {
    const workflow_source = try readWorkflowSource(std.testing.allocator);
    defer std.testing.allocator.free(workflow_source);

    try expectOrdered(workflow_source, &phase8_markers);
    try expectOrdered(workflow_source, &phase9_entry_markers);

    const phase8_validate = try markerIndex(workflow_source, phase8_markers[0]);
    const phase8_exec_cmd = try markerIndex(workflow_source, phase8_markers[1]);
    const phase8_libbpf = try markerIndex(workflow_source, phase8_markers[2]);
    const phase8_all = try markerIndex(workflow_source, phase8_markers[3]);
    const phase9_entry = try markerIndex(workflow_source, phase9_entry_markers[0]);

    try std.testing.expect(phase8_validate < phase8_exec_cmd);
    try std.testing.expect(phase8_exec_cmd < phase8_libbpf);
    try std.testing.expect(phase8_libbpf < phase8_all);
    try std.testing.expect(phase8_all < phase9_entry);
}
