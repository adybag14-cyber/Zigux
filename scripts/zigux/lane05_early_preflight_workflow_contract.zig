const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const setup_tail_markers = [_][]const u8{
    "      - name: Setup Python\n        uses: actions/setup-python@v6.2.0",
    "      - name: Setup pinned Zig toolchain\n        run: |",
    "      - name: Compile current scripts\n        run: |",
};

const current_toolchain_markers = [_][]const u8{
    "      - name: Self-test current Zig toolchain checker\n        run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "      - name: Check current Zig toolchain policy packet\n        run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "      - name: Check current pinned Zig archive packet\n        run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
};

const lane05_archive_markers = [_][]const u8{
    "      - name: Self-test current Lane 05 local-first archive checker\n        run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
    "      - name: Check current Lane 05 local-first archive packet\n        run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "      - name: Self-test current Lane 05 local archive README checker\n        run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test",
    "      - name: Check current Lane 05 local archive README packet\n        run: python3 scripts/zigux/check-lane05-local-archive-readme.py",
    "      - name: Self-test current Lane 05 install-zig archive verification checker\n        run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",
    "      - name: Check current Lane 05 install-zig archive verification packet\n        run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",
};

const lane05_stage_helper_markers = [_][]const u8{
    "      - name: Self-test current staged pinned Zig archive helper\n        run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
    "      - name: Self-test current Zig installer helper\n        run: python3 scripts/zigux/install-zig.py --self-test",
    "      - name: Self-test current Lane 05 stage helper contract checker\n        run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test",
    "      - name: Check current Lane 05 stage helper contract packet\n        run: python3 scripts/zigux/check-lane05-stage-helper-contract.py",
    "      - name: Self-test current Lane 05 stage helper selftest checker\n        run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test",
    "      - name: Check current Lane 05 stage helper selftest packet\n        run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py",
};

const phase2_fixdep_entry_markers = [_][]const u8{
    "      - name: Self-test current Phase 2 fixdep gate checker\n        run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "      - name: Check current Phase 2 fixdep gate packet\n        run: python3 scripts/zigux/check-phase2-fixdep-gate.py",
};

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

fn markerCount(source: []const u8, marker: []const u8) usize {
    var count: usize = 0;
    var start: usize = 0;
    while (std.mem.indexOfPos(u8, source, start, marker)) |index| {
        count += 1;
        start = index + marker.len;
    }
    return count;
}

fn expectUnique(source: []const u8, markers: []const []const u8) !void {
    for (markers) |marker| {
        try std.testing.expectEqual(@as(usize, 1), markerCount(source, marker));
    }
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

test "early setup reaches Python compile before current toolchain gates" {
    const workflow_source = try readWorkflowSource(std.testing.allocator);
    defer std.testing.allocator.free(workflow_source);

    try expectUnique(workflow_source, &setup_tail_markers);
    try expectUnique(workflow_source, &current_toolchain_markers);
    try expectOrdered(workflow_source, &setup_tail_markers);
    try expectOrdered(workflow_source, &current_toolchain_markers);

    const compile_scripts = try markerIndex(workflow_source, setup_tail_markers[setup_tail_markers.len - 1]);
    const toolchain_selftest = try markerIndex(workflow_source, current_toolchain_markers[0]);

    try std.testing.expect(compile_scripts < toolchain_selftest);
}

test "current toolchain gates hand off to Lane 05 archive packet" {
    const workflow_source = try readWorkflowSource(std.testing.allocator);
    defer std.testing.allocator.free(workflow_source);

    try expectUnique(workflow_source, &lane05_archive_markers);
    try expectOrdered(workflow_source, &lane05_archive_markers);

    const toolchain_archive_check = try markerIndex(workflow_source, current_toolchain_markers[current_toolchain_markers.len - 1]);
    const local_first_selftest = try markerIndex(workflow_source, lane05_archive_markers[0]);
    const install_archive_check = try markerIndex(workflow_source, lane05_archive_markers[lane05_archive_markers.len - 1]);

    try std.testing.expect(toolchain_archive_check < local_first_selftest);
    try std.testing.expect(local_first_selftest < install_archive_check);
}

test "Lane 05 stage helper packet remains after archive checks and before Phase 2 fixdep" {
    const workflow_source = try readWorkflowSource(std.testing.allocator);
    defer std.testing.allocator.free(workflow_source);

    try expectUnique(workflow_source, &lane05_stage_helper_markers);
    try expectUnique(workflow_source, &phase2_fixdep_entry_markers);
    try expectOrdered(workflow_source, &lane05_stage_helper_markers);
    try expectOrdered(workflow_source, &phase2_fixdep_entry_markers);

    const archive_tail = try markerIndex(workflow_source, lane05_archive_markers[lane05_archive_markers.len - 1]);
    const stage_helper_start = try markerIndex(workflow_source, lane05_stage_helper_markers[0]);
    const stage_helper_tail = try markerIndex(workflow_source, lane05_stage_helper_markers[lane05_stage_helper_markers.len - 1]);
    const phase2_fixdep_start = try markerIndex(workflow_source, phase2_fixdep_entry_markers[0]);

    try std.testing.expect(archive_tail < stage_helper_start);
    try std.testing.expect(stage_helper_tail < phase2_fixdep_start);
}
