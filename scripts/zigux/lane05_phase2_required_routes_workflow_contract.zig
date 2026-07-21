const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const phase2_make_route_markers = [_][]const u8{
    "      - name: Run current Phase 2 toolchain make route\n        run: make -C zigux phase2-toolchain",
    "      - name: Run current Phase 2 tools make route\n        run: make -C zigux phase2-tools",
    "      - name: Run current Phase 2 kconfig make route\n        run: make -C zigux phase2-kconfig",
    "      - name: Run current Phase 2 fixdep make route\n        run: make -C zigux phase2-fixdep",
    "      - name: Run current Phase 2 cross make route\n        run: make -C zigux phase2-cross",
};

const required_route_checker_markers = [_][]const u8{
    "      - name: Self-test current Phase 2 required-make-routes checker\n        run: zig run scripts/zigux/check_phase2_required_make_routes.zig -- --self-test",
    "      - name: Check current Phase 2 required-make-routes packet\n        run: zig run scripts/zigux/check_phase2_required_make_routes.zig",
};

const phase2_manifest_checker_markers = [_][]const u8{
    "      - name: Self-test current Phase 2 shared reminder checker\n        run: zig run scripts/zigux/check_phase2_docs_shared_reminder.zig -- --self-test",
    "      - name: Check current Phase 2 shared reminder packet\n        run: zig run scripts/zigux/check_phase2_docs_shared_reminder.zig",
    "      - name: Self-test current Phase 2 tool manifest checker\n        run: zig run scripts/zigux/check_phase2_tool_manifest.zig -- --self-test",
    "      - name: Check current Phase 2 tool manifest packet\n        run: zig run scripts/zigux/check_phase2_tool_manifest.zig",
    "      - name: Self-test current Phase 2 artifact tools manifest checker\n        run: zig run scripts/zigux/check_phase2_artifact_tools_manifest.zig -- --self-test",
    "      - name: Check current Phase 2 artifact tools manifest packet\n        run: zig run scripts/zigux/check_phase2_artifact_tools_manifest.zig",
};

const phase2_genksyms_validate_markers = [_][]const u8{
    "      - name: Self-test current Phase 2 genksyms bridge checker\n        run: zig run scripts/zigux/check_genksyms_bridge.zig -- --self-test",
    "      - name: Check current Phase 2 genksyms bridge packet\n        run: zig run scripts/zigux/check_genksyms_bridge.zig",
    "      - name: Run current Phase 2 genksyms unit replay\n        run: zig test scripts/zigux/genksyms.zig",
    "      - name: Self-test current Phase 2 genksyms alignment checker\n        run: zig run scripts/zigux/check_phase2_genksyms_selftest_alignment.zig -- --self-test",
    "      - name: Check current Phase 2 genksyms alignment packet\n        run: zig run scripts/zigux/check_phase2_genksyms_selftest_alignment.zig",
    "      - name: Self-test current Phase 2 genksyms survey guard\n        run: zig run scripts/zigux/check_phase2_genksyms_dual_implementation_survey.zig -- --self-test",
    "      - name: Check current Phase 2 genksyms survey packet\n        run: zig run scripts/zigux/check_phase2_genksyms_dual_implementation_survey.zig",
    "      - name: Run current Phase 2 genksyms make route\n        run: make -C zigux phase2-genksyms",
    "      - name: Run current Phase 2 validate make route\n        run: make -C zigux phase2-validate",
    "      - name: Run current Phase 2 aggregate make route\n        run: make -C zigux phase2",
};

const phase2_closure_marker =
    "      - name: Self-test current Phase 2 closure validator\n        run: zig run scripts/zigux/validate_phase2_closure.zig -- --self-test";

fn readWorkflowSource(allocator: std.mem.Allocator) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        workflow_path,
        allocator,
        .limited(1024 * 1024),
    );
}

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

test "phase2 required make routes stay in bootstrap order" {
    const workflow_source = try readWorkflowSource(std.testing.allocator);
    defer std.testing.allocator.free(workflow_source);

    try expectOrdered(workflow_source, &phase2_make_route_markers);

    const toolchain_route = try markerIndex(workflow_source, phase2_make_route_markers[0]);
    const tools_route = try markerIndex(workflow_source, phase2_make_route_markers[1]);
    const kconfig_route = try markerIndex(workflow_source, phase2_make_route_markers[2]);
    const fixdep_route = try markerIndex(workflow_source, phase2_make_route_markers[3]);
    const cross_route = try markerIndex(workflow_source, phase2_make_route_markers[4]);

    try std.testing.expect(toolchain_route < tools_route);
    try std.testing.expect(tools_route < kconfig_route);
    try std.testing.expect(kconfig_route < fixdep_route);
    try std.testing.expect(fixdep_route < cross_route);
}

test "required-route checker follows the direct make-route cluster" {
    const workflow_source = try readWorkflowSource(std.testing.allocator);
    defer std.testing.allocator.free(workflow_source);

    try expectOrdered(workflow_source, &required_route_checker_markers);
    try expectOrdered(workflow_source, &phase2_manifest_checker_markers);

    const cross_route = try markerIndex(workflow_source, phase2_make_route_markers[phase2_make_route_markers.len - 1]);
    const required_selftest = try markerIndex(workflow_source, required_route_checker_markers[0]);
    const required_check = try markerIndex(workflow_source, required_route_checker_markers[required_route_checker_markers.len - 1]);
    const shared_reminder = try markerIndex(workflow_source, phase2_manifest_checker_markers[0]);

    try std.testing.expect(cross_route < required_selftest);
    try std.testing.expect(required_selftest < required_check);
    try std.testing.expect(required_check < shared_reminder);
}

test "genksyms and aggregate phase2 routes stay ahead of closure validation" {
    const workflow_source = try readWorkflowSource(std.testing.allocator);
    defer std.testing.allocator.free(workflow_source);

    try expectOrdered(workflow_source, &phase2_manifest_checker_markers);
    try expectOrdered(workflow_source, &phase2_genksyms_validate_markers);

    const manifest_tail = try markerIndex(workflow_source, phase2_manifest_checker_markers[phase2_manifest_checker_markers.len - 1]);
    const genksyms_start = try markerIndex(workflow_source, phase2_genksyms_validate_markers[0]);
    const aggregate_route = try markerIndex(workflow_source, phase2_genksyms_validate_markers[phase2_genksyms_validate_markers.len - 1]);
    const closure_start = try markerIndex(workflow_source, phase2_closure_marker);

    try std.testing.expect(manifest_tail < genksyms_start);
    try std.testing.expect(genksyms_start < aggregate_route);
    try std.testing.expect(aggregate_route < closure_start);
}
