const std = @import("std");

const kconfig_tail_markers = [_][]const u8{
    "      - name: Check current Phase 2 kconfig allconfig helper packet\n        run: python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    "      - name: Self-test current Phase 2 kbuild routes checker\n        run: python3 scripts/zigux/check-phase2-kbuild-routes.py --self-test",
    "      - name: Check current Phase 2 kbuild packet\n        run: python3 scripts/zigux/check-phase2-kbuild-routes.py",
    "      - name: Self-test current Phase 2 tests README checker\n        run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test",
    "      - name: Check current Phase 2 tests README packet\n        run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py",
};

const cross_checker_markers = [_][]const u8{
    "      - name: Self-test current Phase 2 cross checker\n        run: python3 scripts/zigux/check-phase2-cross.py --self-test",
    "      - name: Check current Phase 2 direct cross-route packet\n        run: python3 scripts/zigux/check-phase2-cross.py",
    "      - name: Self-test current Phase 2 cross selftest alignment checker\n        run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "      - name: Check current Phase 2 cross alignment packet\n        run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
};

const toolchain_checker_markers = [_][]const u8{
    "      - name: Self-test current Phase 2 toolchain pinning checker\n        run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
    "      - name: Check current Phase 2 toolchain pinning packet\n        run: python3 scripts/zigux/check-phase2-toolchain-pinning.py",
    "      - name: Self-test current Phase 2 toolchain pin-scope checker\n        run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "      - name: Check current Phase 2 toolchain pin-scope packet\n        run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
};

const phase2_make_route_markers = [_][]const u8{
    "      - name: Self-test current Phase 2 bootstrap workflow routes checker\n        run: python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py --self-test",
    "      - name: Check current Phase 2 bootstrap workflow routes packet\n        run: python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
    "      - name: Run current Phase 2 toolchain make route\n        run: make -C zigux phase2-toolchain",
    "      - name: Run current Phase 2 tools make route\n        run: make -C zigux phase2-tools",
    "      - name: Run current Phase 2 kconfig make route\n        run: make -C zigux phase2-kconfig",
    "      - name: Run current Phase 2 fixdep make route\n        run: make -C zigux phase2-fixdep",
    "      - name: Run current Phase 2 cross make route\n        run: make -C zigux phase2-cross",
};

const required_make_route_markers = [_][]const u8{
    "      - name: Self-test current Phase 2 required-make-routes checker\n        run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test",
    "      - name: Check current Phase 2 required-make-routes packet\n        run: python3 scripts/zigux/check-phase2-required-make-routes.py",
};

const phase2_tail_markers = [_][]const u8{
    "      - name: Self-test current Phase 2 shared reminder checker\n        run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py --self-test",
    "      - name: Check current Phase 2 shared reminder packet\n        run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py",
    "      - name: Self-test current Phase 2 tool manifest checker\n        run: python3 scripts/zigux/check-phase2-tool-manifest.py --self-test",
    "      - name: Check current Phase 2 tool manifest packet\n        run: python3 scripts/zigux/check-phase2-tool-manifest.py",
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

test "phase2 cross checkers stay after kconfig gates and before toolchain pin gates" {
    const workflow_source = try readWorkflowSource(std.testing.allocator);
    defer std.testing.allocator.free(workflow_source);

    try expectOrdered(workflow_source, &kconfig_tail_markers);
    try expectOrdered(workflow_source, &cross_checker_markers);
    try expectOrdered(workflow_source, &toolchain_checker_markers);

    const kconfig_tail = try markerIndex(workflow_source, kconfig_tail_markers[kconfig_tail_markers.len - 1]);
    const cross_start = try markerIndex(workflow_source, cross_checker_markers[0]);
    const cross_end = try markerIndex(workflow_source, cross_checker_markers[cross_checker_markers.len - 1]);
    const toolchain_start = try markerIndex(workflow_source, toolchain_checker_markers[0]);

    try std.testing.expect(kconfig_tail < cross_start);
    try std.testing.expect(cross_end < toolchain_start);
}

test "phase2 make route cluster keeps cross route after toolchain, tools, kconfig, and fixdep" {
    const workflow_source = try readWorkflowSource(std.testing.allocator);
    defer std.testing.allocator.free(workflow_source);

    try expectOrdered(workflow_source, &phase2_make_route_markers);

    const bootstrap_routes = try markerIndex(workflow_source, phase2_make_route_markers[1]);
    const toolchain = try markerIndex(workflow_source, phase2_make_route_markers[2]);
    const tools = try markerIndex(workflow_source, phase2_make_route_markers[3]);
    const kconfig = try markerIndex(workflow_source, phase2_make_route_markers[4]);
    const fixdep = try markerIndex(workflow_source, phase2_make_route_markers[5]);
    const cross = try markerIndex(workflow_source, phase2_make_route_markers[6]);

    try std.testing.expect(bootstrap_routes < toolchain);
    try std.testing.expect(toolchain < tools);
    try std.testing.expect(tools < kconfig);
    try std.testing.expect(kconfig < fixdep);
    try std.testing.expect(fixdep < cross);
}

test "required make route guard follows cross make and hands off to phase2 tail manifests" {
    const workflow_source = try readWorkflowSource(std.testing.allocator);
    defer std.testing.allocator.free(workflow_source);

    try expectOrdered(workflow_source, &required_make_route_markers);
    try expectOrdered(workflow_source, &phase2_tail_markers);

    const cross_make = try markerIndex(workflow_source, phase2_make_route_markers[phase2_make_route_markers.len - 1]);
    const required_selftest = try markerIndex(workflow_source, required_make_route_markers[0]);
    const required_check = try markerIndex(workflow_source, required_make_route_markers[1]);
    const shared_reminder = try markerIndex(workflow_source, phase2_tail_markers[0]);

    try std.testing.expect(cross_make < required_selftest);
    try std.testing.expect(required_selftest < required_check);
    try std.testing.expect(required_check < shared_reminder);
}
