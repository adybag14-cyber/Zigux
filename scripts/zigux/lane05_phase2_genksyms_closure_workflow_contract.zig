const std = @import("std");

const phase2_artifact_tail_markers = [_][]const u8{
    "      - name: Check current Phase 2 artifact tools manifest packet\n        run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py",
};

const genksyms_bridge_markers = [_][]const u8{
    "      - name: Self-test current Phase 2 genksyms bridge checker\n        run: python3 scripts/zigux/check-genksyms-bridge.py --self-test",
    "      - name: Check current Phase 2 genksyms bridge packet\n        run: python3 scripts/zigux/check-genksyms-bridge.py",
    "      - name: Run current Phase 2 genksyms unit replay\n        run: zig test scripts/zigux/genksyms.zig",
};

const genksyms_guard_markers = [_][]const u8{
    "      - name: Self-test current Phase 2 genksyms alignment checker\n        run: python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py --self-test",
    "      - name: Check current Phase 2 genksyms alignment packet\n        run: python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
    "      - name: Self-test current Phase 2 genksyms survey guard\n        run: python3 scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py --self-test",
    "      - name: Check current Phase 2 genksyms survey packet\n        run: python3 scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py",
};

const phase2_closure_markers = [_][]const u8{
    "      - name: Run current Phase 2 genksyms make route\n        run: make -C zigux phase2-genksyms",
    "      - name: Run current Phase 2 validate make route\n        run: make -C zigux phase2-validate",
    "      - name: Run current Phase 2 aggregate make route\n        run: make -C zigux phase2",
    "      - name: Validate current Phase 2 tool packet\n        run: python3 scripts/zigux/validate-phase2.py",
    "      - name: Self-test current Phase 2 closure validator\n        run: python3 scripts/zigux/validate-phase2-closure.py --self-test",
    "      - name: Check current Phase 2 closure packet\n        run: python3 scripts/zigux/validate-phase2-closure.py",
};

const phase1_entry_markers = [_][]const u8{
    "      - name: Self-test current Phase 1 direct-owner checker\n        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
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

test "phase2 genksyms bridge starts after artifact tools manifest gate" {
    const workflow_source = try readWorkflowSource(std.testing.allocator);
    defer std.testing.allocator.free(workflow_source);

    try expectOrdered(workflow_source, &phase2_artifact_tail_markers);
    try expectOrdered(workflow_source, &genksyms_bridge_markers);

    const artifact_tail = try markerIndex(workflow_source, phase2_artifact_tail_markers[0]);
    const bridge_start = try markerIndex(workflow_source, genksyms_bridge_markers[0]);
    const bridge_check = try markerIndex(workflow_source, genksyms_bridge_markers[1]);
    const unit_replay = try markerIndex(workflow_source, genksyms_bridge_markers[2]);

    try std.testing.expect(artifact_tail < bridge_start);
    try std.testing.expect(bridge_start < bridge_check);
    try std.testing.expect(bridge_check < unit_replay);
}

test "phase2 genksyms alignment and survey guards follow the unit replay" {
    const workflow_source = try readWorkflowSource(std.testing.allocator);
    defer std.testing.allocator.free(workflow_source);

    try expectOrdered(workflow_source, &genksyms_bridge_markers);
    try expectOrdered(workflow_source, &genksyms_guard_markers);

    const unit_replay = try markerIndex(workflow_source, genksyms_bridge_markers[genksyms_bridge_markers.len - 1]);
    const alignment_start = try markerIndex(workflow_source, genksyms_guard_markers[0]);
    const survey_end = try markerIndex(workflow_source, genksyms_guard_markers[genksyms_guard_markers.len - 1]);

    try std.testing.expect(unit_replay < alignment_start);
    try std.testing.expect(alignment_start < survey_end);
}

test "phase2 genksyms routes close through validators before phase1 resumes" {
    const workflow_source = try readWorkflowSource(std.testing.allocator);
    defer std.testing.allocator.free(workflow_source);

    try expectOrdered(workflow_source, &genksyms_guard_markers);
    try expectOrdered(workflow_source, &phase2_closure_markers);
    try expectOrdered(workflow_source, &phase1_entry_markers);

    const survey_end = try markerIndex(workflow_source, genksyms_guard_markers[genksyms_guard_markers.len - 1]);
    const closure_start = try markerIndex(workflow_source, phase2_closure_markers[0]);
    const closure_end = try markerIndex(workflow_source, phase2_closure_markers[phase2_closure_markers.len - 1]);
    const phase1_entry = try markerIndex(workflow_source, phase1_entry_markers[0]);

    try std.testing.expect(survey_end < closure_start);
    try std.testing.expect(closure_start < closure_end);
    try std.testing.expect(closure_end < phase1_entry);
}
