const std = @import("std");

const allocator = std.testing.allocator;

const RequiredFixdepFixture = struct {
    path: []const u8,
    expected_kind: []const u8,
};

const required_fixdep_fixtures = [_]RequiredFixdepFixture{
    .{ .path = "zigux/tests/fixtures/fixdep/cases.json", .expected_kind = "fixture_roster" },
    .{ .path = "zigux/tests/fixtures/fixdep/sample_comment_only_expected.stderr.txt", .expected_kind = "fixdep_support" },
    .{ .path = "zigux/tests/fixtures/fixdep/sample_comment_only_expected.txt", .expected_kind = "fixdep_support" },
    .{ .path = "zigux/tests/fixtures/fixdep/sample_double_backslash_comment_expected.stderr.txt", .expected_kind = "fixdep_support" },
    .{ .path = "zigux/tests/fixtures/fixdep/sample_double_backslash_comment_expected.txt", .expected_kind = "fixdep_support" },
    .{ .path = "zigux/tests/fixtures/fixdep/sample_missing_dep_expected.stderr.txt", .expected_kind = "fixdep_support" },
    .{ .path = "zigux/tests/fixtures/fixdep/sample_missing_dep_expected.txt", .expected_kind = "fixdep_support" },
    .{ .path = "zigux/tests/fixtures/fixdep/sample_output_write_expected.stderr.txt", .expected_kind = "fixdep_support" },
    .{ .path = "zigux/tests/fixtures/fixdep/sample_output_write_expected.txt", .expected_kind = "fixdep_support" },
    .{ .path = "zigux/tests/fixtures/fixdep/shared#config.h", .expected_kind = "fixdep_support" },
    .{ .path = "zigux/tests/fixtures/fixdep/shared:config.h", .expected_kind = "fixdep_support" },
};

fn readRootFile(path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.FirstMarkerMissing;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.SecondMarkerMissing;
    try std.testing.expect(first_index < second_index);
}

fn countExactLines(text: []const u8, marker: []const u8) usize {
    var count: usize = 0;
    var it = std.mem.splitScalar(u8, text, '\n');
    while (it.next()) |line| {
        const normalized = if (line.len > 0 and line[line.len - 1] == '\r')
            line[0 .. line.len - 1]
        else
            line;
        if (std.mem.eql(u8, normalized, marker)) {
            count += 1;
        }
    }
    return count;
}

fn expectExactLineOnce(text: []const u8, marker: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countExactLines(text, marker));
}

test "closure note keeps fixdep support visible in the shared Phase 2 packet" {
    const closure = try readRootFile("Documentation/zigux/phase2-closure.md");
    defer allocator.free(closure);

    try expectContains(closure, "Documentation/zigux/phase2-fixdep-dual-implementation-survey.md");
    try expectContains(closure, "scripts/zigux/check-phase2-fixdep-gate.py");
    try expectContains(closure, "scripts/zigux/check-fixdep-diff.py");
    try expectContains(closure, "make -C zigux phase2-fixdep");
    try expectContains(closure, "fixdep governance/parity packet directly replayable beside the closure note");
    try expectContains(closure, "PHASE2_SHARED_TOOLING_CHECKERS=python3 scripts/zigux/check-phase2-tool-manifest.py,python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py,python3 scripts/zigux/check-phase2-artifact-tools-manifest.py,python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py,python3 scripts/zigux/check-phase2-cross.py,python3 scripts/zigux/check-phase2-fixdep-gate.py,python3 scripts/zigux/check-fixdep-diff.py");
    try expectContains(closure, "PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2");
    try expectOrdered(closure, "scripts/zigux/check-phase2-cross.py", "scripts/zigux/check-phase2-fixdep-gate.py");
    try expectOrdered(closure, "scripts/zigux/check-phase2-fixdep-gate.py", "scripts/zigux/check-fixdep-diff.py");
}

test "tool manifest preserves the fixdep checker helper and fixture roster" {
    const manifest = try readRootFile("zigux/tests/fixtures/phase2_tool_manifest.json");
    defer allocator.free(manifest);

    try expectContains(manifest, "\"fixdep_support\"");
    try expectContains(manifest, "\"scripts/zigux/check-phase2-fixdep-gate.py\"");
    try expectContains(manifest, "\"scripts/zigux/check-fixdep-diff.py\"");
    try expectContains(manifest, "\"scripts/zigux/fixdep.zig\"");
    try expectContains(manifest, "\"repo_reality_gaps\": []");

    inline for (required_fixdep_fixtures) |fixture| {
        try expectContains(manifest, fixture.path);
        try expectContains(manifest, fixture.expected_kind);
    }

    try expectNotContains(manifest, "\"scripts/basic/fixdep.c\"");
    try expectOrdered(manifest, "\"scripts/zigux/check-phase2-fixdep-gate.py\"", "\"scripts/zigux/check-fixdep-diff.py\"");
    try expectOrdered(manifest, "\"zigux/tests/fixtures/fixdep/sample_comment_only_expected.stderr.txt\"", "\"zigux/tests/fixtures/fixdep/sample_output_write_expected.txt\"");
}

test "makefile and fixdep gate keep the closure route executable" {
    const makefile = try readRootFile("zigux/Makefile");
    defer allocator.free(makefile);
    const gate = try readRootFile("scripts/zigux/check-phase2-fixdep-gate.py");
    defer allocator.free(gate);

    try expectExactLineOnce(makefile, "phase2-fixdep: phase2-toolchain");
    try expectExactLineOnce(makefile, "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py --self-test");
    try expectExactLineOnce(makefile, "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py");
    try expectExactLineOnce(makefile, "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --self-test");
    try expectExactLineOnce(makefile, "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --zig \"$(ZIG_REPO_ROOT)\"");
    try expectExactLineOnce(makefile, "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/fixdep.zig");
    try expectContains(makefile, "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep");

    try expectContains(gate, "\"sample_double_backslash_comment\"");
    try expectContains(gate, "\"sample_missing_dep_stdout_full\"");
    try expectContains(gate, "EXPECTED_SELF_TEST_CASE_COUNT = 16");
    try expectContains(gate, "FIXDEP_SELF_TEST=pass");
    try expectContains(gate, "FIXDEP_DIFF=pass");
    try expectContains(gate, "FIXDEP_DETERMINISM=pass");
    try expectContains(gate, "Documentation/zigux/phase2-fixdep-dual-implementation-survey.md");
    try expectContains(gate, "scripts/zigux/fixdep.zig");
    try expectOrdered(gate, "\"sample_double_backslash_comment\"", "\"sample_missing_dep\"");
}
