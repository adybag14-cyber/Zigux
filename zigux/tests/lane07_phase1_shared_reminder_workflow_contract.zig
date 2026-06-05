const std = @import("std");
const testing = std.testing;
const options = @import("contract_options");

const max_file_size = 512 * 1024;

fn readText(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(testing.io, path, testing.allocator, .limited(max_file_size));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try testing.expect(earlier_index < later_index);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var offset: usize = 0;

    while (offset <= haystack.len) {
        const found = std.mem.indexOf(u8, haystack[offset..], needle) orelse break;
        count += 1;
        offset += found + needle.len;
    }

    return count;
}

fn expectExactCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    try testing.expectEqual(expected, countOccurrences(haystack, needle));
}

test "tests README keeps the shared-reminder gate members in the Phase 1 packet" {
    const readme = try readText(options.tests_readme_path);
    defer testing.allocator.free(readme);

    try expectContains(readme, "## Phase 1 host-tools review packet");
    try expectContains(readme, "  * current direct-readback Phase 1 reminder packet:");
    try expectContains(readme, "- `scripts/zigux/check-phase1-shared-reminder-packet.py`");
    try expectContains(readme, "- `.github/workflows/zigux-bootstrap.yml`");
    try expectContains(readme, "  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`");

    try expectBefore(
        readme,
        "- `scripts/zigux/check-phase1-bench.py`",
        "- `scripts/zigux/check-phase1-shared-reminder-packet.py`",
    );
    try expectBefore(
        readme,
        "- `scripts/zigux/check-phase1-shared-reminder-packet.py`",
        "- `scripts/zigux/validate-phase1-closure.py`",
    );
    try expectBefore(
        readme,
        "- `.github/workflows/zigux-bootstrap.yml`",
        "  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    );
}

test "bootstrap workflow runs shared reminder checks between bench anchors and closure" {
    const workflow = try readText(options.workflow_path);
    defer testing.allocator.free(workflow);

    const bench_check = "python3 scripts/zigux/check-phase1-bench.py";
    const bench_live = "python3 scripts/zigux/check-phase1-bench-live-check-workflow.py";
    const find_bit_bench = "python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py";
    const reminder_self_test = "python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test";
    const reminder_live = "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py\n";
    const closure_self_test = "python3 scripts/zigux/validate-phase1-closure.py --self-test";
    const closure_live = "        run: python3 scripts/zigux/validate-phase1-closure.py\n";

    try expectExactCount(workflow, reminder_self_test, 1);
    try expectExactCount(workflow, reminder_live, 1);
    try expectContains(workflow, "- name: Self-test current Phase 1 shared reminder checker");
    try expectContains(workflow, "- name: Check current Phase 1 shared reminder packet");

    try expectBefore(workflow, bench_check, bench_live);
    try expectBefore(workflow, bench_live, find_bit_bench);
    try expectBefore(workflow, find_bit_bench, reminder_self_test);
    try expectBefore(workflow, reminder_self_test, reminder_live);
    try expectBefore(workflow, reminder_live, closure_self_test);
    try expectBefore(workflow, closure_self_test, closure_live);
}

test "shared reminder remains before the cross-phase smoke handoff" {
    const workflow = try readText(options.workflow_path);
    defer testing.allocator.free(workflow);

    const reminder_live = "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py\n";
    const closure_live = "        run: python3 scripts/zigux/validate-phase1-closure.py\n";
    const phase3_interop = "python3 scripts/zigux/validate_phase3_selftest.py";
    const phase3_build = "zig build phase3-test --build-file zigux/tests/build.zig";
    const phase1_smoke = "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig";

    try expectExactCount(workflow, phase1_smoke, 1);
    try expectContains(workflow, "- name: Run current Phase 1 shared tests-root smoke");

    try expectBefore(workflow, reminder_live, closure_live);
    try expectBefore(workflow, closure_live, phase3_interop);
    try expectBefore(workflow, phase3_interop, phase3_build);
    try expectBefore(workflow, phase3_build, phase1_smoke);

    try expectNotContains(workflow, "zig test zigux/tests/phase1_host_tools_smoke.zig");
}
