const std = @import("std");

const read_limit = 1024 * 1024;

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(read_limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.BeforeMarkerMissing;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.AfterMarkerMissing;
    try std.testing.expect(before_index < after_index);
}

test "workflow keeps Phase 1 closure validation after helper review gates" {
    const allocator = std.testing.allocator;

    const workflow = try readRepoFile(allocator, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow);

    for ([_][]const u8{
        "Self-test current Phase 1 direct-owner checker",
        "Check current Phase 1 direct-owner markers",
        "Self-test current Phase 1 direct-anchor manifest gate",
        "Check current Phase 1 direct-anchor manifest gate",
        "Self-test current Phase 1 string review checker",
        "Check current Phase 1 string review packet",
        "Self-test current Phase 1 find-bit review checker",
        "Check current Phase 1 find-bit review packet",
        "Self-test current Phase 1 bitmap direct-anchor checker",
        "Check current Phase 1 bitmap direct-anchor packet",
        "Self-test current Phase 1 rbtree review checker",
        "Check current Phase 1 rbtree review packet",
        "Self-test current Phase 1 route summary checker",
        "Check current Phase 1 route summary packet",
        "Self-test current Phase 1 bench checker",
        "Check current Phase 1 bench packet",
        "Self-test current Phase 1 shared reminder checker",
        "Check current Phase 1 shared reminder packet",
        "Self-test current Phase 1 closure validator",
        "Check current Phase 1 closure packet",
    }) |marker| {
        try expectContains(workflow, marker);
    }

    try expectOrdered(workflow, "Check current Phase 1 direct-owner markers", "Check current Phase 1 direct-anchor manifest gate");
    try expectOrdered(workflow, "Check current Phase 1 direct-anchor manifest gate", "Check current Phase 1 string review packet");
    try expectOrdered(workflow, "Check current Phase 1 string review packet", "Check current Phase 1 find-bit review packet");
    try expectOrdered(workflow, "Check current Phase 1 find-bit review packet", "Check current Phase 1 bitmap direct-anchor packet");
    try expectOrdered(workflow, "Check current Phase 1 bitmap direct-anchor packet", "Check current Phase 1 rbtree review packet");
    try expectOrdered(workflow, "Check current Phase 1 rbtree review packet", "Check current Phase 1 route summary packet");
    try expectOrdered(workflow, "Check current Phase 1 route summary packet", "Check current Phase 1 bench packet");
    try expectOrdered(workflow, "Check current Phase 1 bench packet", "Check current Phase 1 shared reminder packet");
    try expectOrdered(workflow, "Check current Phase 1 shared reminder packet", "Self-test current Phase 1 closure validator");
    try expectOrdered(workflow, "Self-test current Phase 1 closure validator", "Check current Phase 1 closure packet");
}

test "workflow closure block uses the live closure validator commands" {
    const allocator = std.testing.allocator;

    const workflow = try readRepoFile(allocator, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow);

    for ([_][]const u8{
        "python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
        "python3 scripts/zigux/check-phase1-direct-owner-markers.py",
        "python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test",
        "python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
        "python3 scripts/zigux/check-phase1-bench.py --self-test",
        "python3 scripts/zigux/check-phase1-bench.py",
        "python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
        "python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
        "python3 scripts/zigux/validate-phase1-closure.py --self-test",
        "python3 scripts/zigux/validate-phase1-closure.py",
    }) |marker| {
        try expectContains(workflow, marker);
    }

    try expectNotContains(workflow, "python3 scripts/zigux/validate-phase1.py");
    try expectNotContains(workflow, "make -C zigux phase1-validate");
    try expectNotContains(workflow, "make -C zigux phase1-test");
    try expectNotContains(workflow, "make -C zigux phase1-bench");
}

test "closure note and validator describe the same current workflow packet" {
    const allocator = std.testing.allocator;

    const closure_note = try readRepoFile(allocator, "Documentation/zigux/phase1-closure.md");
    defer allocator.free(closure_note);

    const validator = try readRepoFile(allocator, "scripts/zigux/validate-phase1-closure.py");
    defer allocator.free(validator);

    const workflow = try readRepoFile(allocator, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow);

    for ([_][]const u8{
        "PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py",
        "PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py",
        "PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
        "PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master",
        "PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
        "PHASE1_FIND_BIT_BENCH_ANCHOR_GUARD=python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py",
    }) |marker| {
        try expectContains(closure_note, marker);
    }

    for ([_][]const u8{
        "WORKFLOW_REL = Path(\".github/workflows/zigux-bootstrap.yml\")",
        "ROUTE_SUMMARY_CHECKER_REL = Path(\"scripts/zigux/check-phase1-route-summary-counts.py\")",
        "BENCH_CHECKER_REL = Path(\"scripts/zigux/check-phase1-bench.py\")",
        "SHARED_REMINDER_CHECKER_REL = Path(\"scripts/zigux/check-phase1-shared-reminder-packet.py\")",
        "PHASE1_SMOKE_REL = Path(\"zigux/tests/phase1_host_tools_smoke.zig\")",
        "EXPECTED_CLOSURE_MARKERS",
        "FORBIDDEN_CLOSURE_MARKERS",
    }) |marker| {
        try expectContains(validator, marker);
    }

    try expectOrdered(workflow, "Check current Phase 1 closure packet", "Check current Phase 3 interop packet");
    try expectOrdered(workflow, "Run current Phase 3 shared tests-root packet", "Run current Phase 1 shared tests-root smoke");
}

test "workflow keeps Phase 1 closure narrow instead of reopening historical routes" {
    const allocator = std.testing.allocator;

    const closure_note = try readRepoFile(allocator, "Documentation/zigux/phase1-closure.md");
    defer allocator.free(closure_note);

    const tests_readme = try readRepoFile(allocator, "zigux/tests/README.md");
    defer allocator.free(tests_readme);

    const workflow = try readRepoFile(allocator, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow);

    for ([_][]const u8{
        "scripts/zigux/validate-phase1.py",
        "scripts/zigux/check-phase1-parity.py",
        "zigux/tests/phase1_bench.zig",
        "zigux/tests/fixtures/phase1_bench_expectations.json",
        "zigux/tests/fixtures/phase1_helpers_c_harness.c",
        "historical closure-stack vocabulary",
    }) |marker| {
        try expectContains(closure_note, marker);
    }

    for ([_][]const u8{
        "phase1-host-tools-smoke",
        "phase1_helpers_build.zig",
        "validate-phase1-closure.py",
        "shared tests-root smoke route",
    }) |marker| {
        try expectContains(tests_readme, marker);
    }

    try expectContains(workflow, "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig");
    try expectNotContains(workflow, "zig build phase1-helpers --build-file zigux/tests/build.zig");
}
