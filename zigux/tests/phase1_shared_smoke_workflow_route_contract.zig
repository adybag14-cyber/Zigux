const std = @import("std");
const options = @import("phase1_shared_smoke_workflow_route_options");

const workflow = options.workflow_text;

const shared_smoke_name =
    "      - name: Run current Phase 1 shared tests-root smoke\n";
const shared_smoke_run =
    "        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig\n";
const phase3_shared_test_run =
    "        run: zig build phase3-test --build-file zigux/tests/build.zig\n";
const phase3_dump_run =
    "        run: zig build phase3-dump --build-file zigux/tests/build.zig\n";
const phase4_repo_reality_self_test =
    "        run: python3 scripts/zigux/check-phase4-repo-reality-warning.py --self-test\n";

fn contains(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

fn indexOfRequired(haystack: []const u8, needle: []const u8) !usize {
    return std.mem.indexOf(u8, haystack, needle) orelse error.MissingWorkflowMarker;
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var remaining = haystack;
    var count: usize = 0;
    while (std.mem.indexOf(u8, remaining, needle)) |index| {
        count += 1;
        remaining = remaining[index + needle.len ..];
    }
    return count;
}

test "workflow keeps exact Phase 1 shared tests-root smoke route" {
    try std.testing.expect(contains(workflow, shared_smoke_name));
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(workflow, shared_smoke_run));

    try std.testing.expect(!contains(
        workflow,
        "        run: zig build test --build-file zigux/tests/build.zig\n",
    ));
    try std.testing.expect(!contains(
        workflow,
        "        run: zig test zigux/tests/phase1_host_tools_smoke.zig\n",
    ));
    try std.testing.expect(!contains(
        workflow,
        "        run: make -C zigux phase1-host-tools-smoke\n",
    ));
}

test "workflow runs shared smoke after Phase 3 shared tests-root gates" {
    const phase3_test_index = try indexOfRequired(workflow, phase3_shared_test_run);
    const phase3_dump_index = try indexOfRequired(workflow, phase3_dump_run);
    const shared_smoke_index = try indexOfRequired(workflow, shared_smoke_run);

    try std.testing.expect(phase3_test_index < shared_smoke_index);
    try std.testing.expect(phase3_dump_index < shared_smoke_index);
}

test "workflow keeps Phase 1 shared smoke before Phase 4 gates" {
    const shared_smoke_name_index = try indexOfRequired(workflow, shared_smoke_name);
    const shared_smoke_run_index = try indexOfRequired(workflow, shared_smoke_run);
    const phase4_index = try indexOfRequired(workflow, phase4_repo_reality_self_test);

    try std.testing.expect(shared_smoke_name_index < shared_smoke_run_index);
    try std.testing.expect(shared_smoke_run_index < phase4_index);
}
