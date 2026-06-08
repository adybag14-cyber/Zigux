const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

fn expectLineBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    var first_index: ?usize = null;
    var second_index: ?usize = null;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    var line_index: usize = 0;
    while (lines.next()) |line| : (line_index += 1) {
        const trimmed = std.mem.trim(u8, line, " \t\r");
        if (std.mem.eql(u8, trimmed, first) and first_index == null) first_index = line_index;
        if (std.mem.eql(u8, trimmed, second) and second_index == null) second_index = line_index;
    }

    const found_first = first_index orelse return error.MissingFirstMarker;
    const found_second = second_index orelse return error.MissingSecondMarker;
    try std.testing.expect(found_first < found_second);
}

test "phase2 tool manifest keeps the cross selftest alignment checker in the shared packet" {
    const manifest = try readRepoFile("zigux/tests/fixtures/phase2_tool_manifest.json", 256 * 1024);
    defer std.testing.allocator.free(manifest);

    try expectContains(manifest, "\"phase\": \"Phase 2\"");
    try expectContains(manifest, "\"status\": \"active\"");
    try expectContains(manifest, "\"repo_reality_gaps\": []");
    try expectContains(manifest, "\"scripts/zigux/check-phase2-cross.py\"");
    try expectContains(manifest, "\"scripts/zigux/check-phase2-cross-selftest-alignment.py\"");
    try expectContains(manifest, "\"zigux/tests/fixtures/phase2_cross_targets.json\"");
    try expectContains(manifest, "\"make -C zigux phase2-cross\"");
    try expectContains(manifest, "\"make -C zigux phase2-validate\"");
}

test "phase2 tests root and scripts checker name the cross selftest alignment surface" {
    const tests_readme = try readRepoFile("zigux/tests/README.md", 384 * 1024);
    defer std.testing.allocator.free(tests_readme);

    try expectContains(tests_readme, "## Phase 2 review packet");
    try expectContains(tests_readme, "`scripts/zigux/check-phase2-cross.py`");
    try expectContains(tests_readme, "`scripts/zigux/check-phase2-cross-selftest-alignment.py`");
    try expectContains(tests_readme, "direct cross-route, cross-selftest");
    try expectContains(tests_readme, "`zigux/tests/fixtures/phase2_cross_targets.json`");

    const checker = try readRepoFile("scripts/zigux/check-phase2-cross-selftest-alignment.py", 192 * 1024);
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "PHASE2_CROSS_ALIGNMENT_SELF_TEST=pass");
    try expectContains(checker, "PHASE2_CROSS_ALIGNMENT=pass");
    try expectContains(checker, "SUPPORTED_CROSS_TARGETS");
    try expectContains(checker, "EXPECTED_REQUIRED_MAKE_ROUTES");
    try expectContains(checker, "check-phase2-cross-selftest-alignment.py --self-test");
}

test "phase2 make and workflow routes run cross selftest before the live alignment check" {
    const makefile = try readRepoFile("zigux/Makefile", 128 * 1024);
    defer std.testing.allocator.free(makefile);

    const direct_cross = "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py";
    const alignment_self_test = "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py --self-test";
    const alignment_live = "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py";
    const phase2_validate = "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep";

    try expectContains(makefile, "phase2-cross:");
    try expectContains(makefile, direct_cross);
    try expectContains(makefile, alignment_self_test);
    try expectContains(makefile, alignment_live);
    try expectContains(makefile, phase2_validate);
    try expectLineBefore(makefile, direct_cross, alignment_self_test);
    try expectLineBefore(makefile, alignment_self_test, alignment_live);
    try expectLineBefore(makefile, alignment_live, phase2_validate);

    const workflow = try readRepoFile(".github/workflows/zigux-bootstrap.yml", 512 * 1024);
    defer std.testing.allocator.free(workflow);

    const workflow_cross_self_test = "run: python3 scripts/zigux/check-phase2-cross.py --self-test";
    const workflow_cross_live = "run: python3 scripts/zigux/check-phase2-cross.py";
    const workflow_alignment_self_test = "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test";
    const workflow_alignment_live = "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py";

    try expectContains(workflow, "Self-test current Phase 2 cross selftest alignment checker");
    try expectContains(workflow, "Check current Phase 2 cross alignment packet");
    try expectLineBefore(workflow, workflow_cross_self_test, workflow_cross_live);
    try expectLineBefore(workflow, workflow_cross_live, workflow_alignment_self_test);
    try expectLineBefore(workflow, workflow_alignment_self_test, workflow_alignment_live);
}

test "phase2 cross targets fixture stays policy-backed and route-scoped" {
    const fixture = try readRepoFile("zigux/tests/fixtures/phase2_cross_targets.json", 64 * 1024);
    defer std.testing.allocator.free(fixture);

    try expectContains(fixture, "\"phase\": \"Phase 2\"");
    try expectContains(fixture, "\"status\": \"active\"");
    try expectContains(fixture, "\"route\": \"make -C zigux phase2-cross\"");
    try expectContains(fixture, "\"archive_target_scope\"");
    try expectContains(fixture, "\"target\": \"x86_64-linux\"");
    try expectContains(fixture, "\"validation_mode\": \"archive_required\"");
    try expectContains(fixture, "\"target\": \"aarch64-linux\"");
    try expectContains(fixture, "\"validation_mode\": \"route_contract_only\"");

    const policy = try readRepoFile("scripts/zigux/zig-toolchain-policy.json", 64 * 1024);
    defer std.testing.allocator.free(policy);

    try expectContains(policy, "\"archive_target_scope\"");
    try expectContains(policy, "\"required_make_routes\"");
    try expectContains(policy, "\"phase2-cross\"");
}
