const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const phase9_review_markers = [_][]const u8{
    "      - name: Self-test current Phase 9 review-checklist boundaries checker\n        run: zig run scripts/zigux/check_phase9_review_checklist_phase_boundaries.zig -- --self-test",
    "      - name: Check current Phase 9 review-checklist boundaries packet\n        run: zig run scripts/zigux/check_phase9_review_checklist_phase_boundaries.zig",
    "      - name: Self-test current Phase 9 freeze-map study-boundaries checker\n        run: zig run scripts/zigux/check_phase9_freeze_map_study_boundaries.zig -- --self-test",
    "      - name: Check current Phase 9 freeze-map study-boundaries packet\n        run: zig run scripts/zigux/check_phase9_freeze_map_study_boundaries.zig",
    "      - name: Self-test current Phase 9 build-only surface checker\n        run: zig run scripts/zigux/check_phase9_build_only_surface.zig -- --self-test",
    "      - name: Check current Phase 9 build-only surface packet\n        run: zig run scripts/zigux/check_phase9_build_only_surface.zig",
};

const phase9_runtime_markers = [_][]const u8{
    "      - name: Self-test current Phase 9 trace-events runtime packet checker\n        run: zig run scripts/zigux/check_phase9_trace_events_runtime_packet.zig -- --self-test",
    "      - name: Check current Phase 9 trace-events runtime packet\n        run: zig run scripts/zigux/check_phase9_trace_events_runtime_packet.zig",
    "      - name: Run current Phase 9 shared loader command-environment boundary guard tests\n        run: zig build phase9-runtime-loader-command-env-boundary-guard-tests --build-file zigux/tests/phase9_build.zig",
    "      - name: Run current Phase 9 shared loader allocator-init-flow packet\n        run: zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig",
    "      - name: Run current Phase 9 trace-events runtime sample tests\n        run: zig test samples/zigux/runtime_trace_events.zig",
    "      - name: Run current Phase 9 trace-events survey witness\n        run: zig test zigux/tests/runtime_trace_events_survey.zig",
};

const phase7_handoff_markers = [_][]const u8{
    "      - name: Self-test current Phase 7 shared-control gap checker\n        run: zig run scripts/zigux/check_phase7_shared_control_gap.zig -- --self-test",
    "      - name: Check current Phase 7 shared-control gap packet\n        run: zig run scripts/zigux/check_phase7_shared_control_gap.zig",
    "      - name: Self-test current Phase 7 make-wrapper selftest alignment checker\n        run: zig run scripts/zigux/check_phase7_make_wrapper_selftest_alignment.zig -- --self-test",
    "      - name: Check current Phase 7 make-wrapper selftest alignment packet\n        run: zig run scripts/zigux/check_phase7_make_wrapper_selftest_alignment.zig",
};

const phase10_phase11_markers = [_][]const u8{
    "      - name: Self-test current Phase 10 bootstrap route checker\n        run: zig run scripts/zigux/check_phase10_bootstrap_route.zig -- --self-test",
    "      - name: Check current Phase 10 bootstrap route\n        run: zig run scripts/zigux/check_phase10_bootstrap_route.zig",
    "      - name: Validate Phase 10 checker-backed review packet\n        run: make -C zigux phase10-validate",
    "      - name: Run Phase 10 helper tests\n        run: make -C zigux phase10-test",
    "      - name: Self-test current Phase 11 build inventory checker\n        run: zig run scripts/zigux/check_phase11_build_inventory.zig -- --self-test",
    "      - name: Check current Phase 11 build inventory packet\n        run: zig run scripts/zigux/check_phase11_build_inventory.zig",
    "      - name: Validate current Phase 11 support bundle\n        run: make -C zigux phase11-validate",
};

const phase12_entry_marker =
    "      - name: Self-test current Phase 12 build-only surface checker\n        run: zig run scripts/zigux/check_build_only_phase12_surface.zig -- --self-test";

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
        workflow_path,
        allocator,
        .limited(1024 * 1024),
    );
}

test "phase9 review gates precede phase9 runtime sample routes" {
    const workflow_source = try readWorkflowSource(std.testing.allocator);
    defer std.testing.allocator.free(workflow_source);

    try expectOrdered(workflow_source, &phase9_review_markers);
    try expectOrdered(workflow_source, &phase9_runtime_markers);

    const review_end = try markerIndex(workflow_source, phase9_review_markers[phase9_review_markers.len - 1]);
    const runtime_start = try markerIndex(workflow_source, phase9_runtime_markers[0]);
    try std.testing.expect(review_end < runtime_start);
}

test "phase9 runtime packet hands off to phase7 before phase10" {
    const workflow_source = try readWorkflowSource(std.testing.allocator);
    defer std.testing.allocator.free(workflow_source);

    try expectOrdered(workflow_source, &phase9_runtime_markers);
    try expectOrdered(workflow_source, &phase7_handoff_markers);
    try expectOrdered(workflow_source, &phase10_phase11_markers);

    const runtime_end = try markerIndex(workflow_source, phase9_runtime_markers[phase9_runtime_markers.len - 1]);
    const phase7_start = try markerIndex(workflow_source, phase7_handoff_markers[0]);
    const phase7_end = try markerIndex(workflow_source, phase7_handoff_markers[phase7_handoff_markers.len - 1]);
    const phase10_start = try markerIndex(workflow_source, phase10_phase11_markers[0]);

    try std.testing.expect(runtime_end < phase7_start);
    try std.testing.expect(phase7_end < phase10_start);
}

test "phase10 and phase11 checks stay ahead of phase12 entry" {
    const workflow_source = try readWorkflowSource(std.testing.allocator);
    defer std.testing.allocator.free(workflow_source);

    try expectOrdered(workflow_source, &phase10_phase11_markers);

    const phase11_validate = try markerIndex(workflow_source, phase10_phase11_markers[phase10_phase11_markers.len - 1]);
    const phase12_entry = try markerIndex(workflow_source, phase12_entry_marker);
    try std.testing.expect(phase11_validate < phase12_entry);
}
