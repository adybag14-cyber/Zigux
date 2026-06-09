const std = @import("std");

fn readRepoFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(1024 * 1024),
    );
}

fn expectMarker(haystack: []const u8, marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, marker) != null);
}

fn expectOrderedMarkers(haystack: []const u8, markers: []const []const u8) !void {
    var cursor: usize = 0;
    for (markers) |marker| {
        const index = std.mem.indexOfPos(u8, haystack, cursor, marker) orelse
            return error.MissingOrderedMarker;
        cursor = index + marker.len;
    }
}

fn countLine(text: []const u8, line: []const u8) usize {
    var count: usize = 0;
    var iter = std.mem.splitScalar(u8, text, '\n');
    while (iter.next()) |candidate| {
        if (std.mem.eql(u8, std.mem.trim(u8, candidate, "\r"), line)) {
            count += 1;
        }
    }
    return count;
}

test "phase 1 workflow keeps the current shared helper gate block ordered" {
    const workflow = try readRepoFile(".github/workflows/zigux-bootstrap.yml");
    defer std.testing.allocator.free(workflow);

    try expectOrderedMarkers(workflow, &[_][]const u8{
        "      - name: Self-test current Phase 1 direct-owner checker",
        "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
        "      - name: Check current Phase 1 direct-owner markers",
        "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py",
        "      - name: Self-test current Phase 1 direct-anchor manifest gate",
        "        run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test",
        "      - name: Check current Phase 1 direct-anchor manifest gate",
        "        run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
        "      - name: Self-test current Phase 1 string review checker",
        "        run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
        "      - name: Check current Phase 1 string review packet",
        "        run: python3 scripts/zigux/check-phase1-string-review-packet.py",
        "      - name: Self-test current Phase 1 find-bit review checker",
        "        run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py --self-test",
        "      - name: Check current Phase 1 find-bit review packet",
        "        run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py",
        "      - name: Self-test current Phase 1 bitmap direct-anchor checker",
        "        run: python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py --self-test",
        "      - name: Check current Phase 1 bitmap direct-anchor packet",
        "        run: python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py",
        "      - name: Self-test current Phase 1 rbtree review checker",
        "        run: python3 scripts/zigux/check-phase1-rbtree-review-packet.py --self-test",
        "      - name: Check current Phase 1 rbtree review packet",
        "        run: python3 scripts/zigux/check-phase1-rbtree-review-packet.py",
        "      - name: Self-test current Phase 1 route summary checker",
        "        run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
        "      - name: Check current Phase 1 route summary packet",
        "        run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
        "      - name: Self-test current Phase 1 bench checker",
        "        run: python3 scripts/zigux/check-phase1-bench.py --self-test",
        "      - name: Check current Phase 1 bench packet",
        "        run: python3 scripts/zigux/check-phase1-bench.py",
        "      - name: Self-test current Phase 1 bench live-check workflow guard",
        "        run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py --self-test",
        "      - name: Check current Phase 1 bench live-check workflow guard packet",
        "        run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py",
        "      - name: Self-test current Phase 1 find-bit bench anchor checker",
        "        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test",
        "      - name: Check current Phase 1 find-bit bench anchor packet",
        "        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py",
        "      - name: Self-test current Phase 1 shared reminder checker",
        "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
        "      - name: Check current Phase 1 shared reminder packet",
        "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
        "      - name: Self-test current Phase 1 closure validator",
        "        run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
        "      - name: Check current Phase 1 closure packet",
        "        run: python3 scripts/zigux/validate-phase1-closure.py",
        "      - name: Run current Phase 3 interop packet",
    });
}

test "phase 1 shared smoke route stays wired through the tests-root build file" {
    const build_file = try readRepoFile("zigux/tests/build.zig");
    defer std.testing.allocator.free(build_file);

    try expectMarker(build_file, "fn addPhase1HostToolsSmoke(");
    try expectMarker(build_file, "const phase1_host_tools_smoke = addPhase1HostToolsSmoke(b, target, optimize);");
    try expectMarker(build_file, "\"phase1-host-tools-smoke\"");
    try expectMarker(build_file, "\"Run the shared Phase 1 host-tools smoke anchor from zigux/tests\"");
    try expectMarker(build_file, "phase1_step.dependOn(&phase1_host_tools_smoke.step);");
    try expectMarker(build_file, "smoke_step.dependOn(&phase1_host_tools_smoke.step);");
    try expectMarker(build_file, "test_step.dependOn(&phase1_host_tools_smoke.step);");
}

test "workflow uses each Phase 1 gate command exactly once" {
    const workflow = try readRepoFile(".github/workflows/zigux-bootstrap.yml");
    defer std.testing.allocator.free(workflow);

    const exact_lines = [_][]const u8{
        "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
        "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py",
        "        run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test",
        "        run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
        "        run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
        "        run: python3 scripts/zigux/check-phase1-string-review-packet.py",
        "        run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py --self-test",
        "        run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py",
        "        run: python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py --self-test",
        "        run: python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py",
        "        run: python3 scripts/zigux/check-phase1-rbtree-review-packet.py --self-test",
        "        run: python3 scripts/zigux/check-phase1-rbtree-review-packet.py",
        "        run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
        "        run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
        "        run: python3 scripts/zigux/check-phase1-bench.py --self-test",
        "        run: python3 scripts/zigux/check-phase1-bench.py",
        "        run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py --self-test",
        "        run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py",
        "        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test",
        "        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py",
        "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
        "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
        "        run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
        "        run: python3 scripts/zigux/validate-phase1-closure.py",
        "        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    };

    for (exact_lines) |line| {
        try std.testing.expectEqual(@as(usize, 1), countLine(workflow, line));
    }
}
