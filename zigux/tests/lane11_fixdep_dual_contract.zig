const std = @import("std");

fn readRepoFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(1024 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectAtLeastMarkerCount(haystack: []const u8, needle: []const u8, minimum: usize) !void {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, cursor, needle)) |index| {
        count += 1;
        cursor = index + needle.len;
    }

    try std.testing.expect(count >= minimum);
}

test "lane 11 fixdep packet keeps helper, parity checker, and gate checker tied together" {
    const fixdep = try readRepoFile("scripts/zigux/fixdep.zig");
    defer std.testing.allocator.free(fixdep);

    const diff_checker = try readRepoFile("scripts/zigux/check-fixdep-diff.py");
    defer std.testing.allocator.free(diff_checker);

    const gate_checker = try readRepoFile("scripts/zigux/check-phase2-fixdep-gate.py");
    defer std.testing.allocator.free(gate_checker);

    try expectContains(fixdep, "pub fn runFixdep");
    try expectContains(fixdep, "CONFIG_");
    try expectContains(fixdep, "test \"config parsing");
    try expectContains(fixdep, "test \"dep parsing");
    try expectContains(fixdep, "test \"output");

    try expectContains(diff_checker, "ZIG_FIXDEP");
    try expectContains(diff_checker, "EXPECTED_CASES = {");
    try expectContains(diff_checker, "EXPECTED_CASE_ORDER = list(EXPECTED_CASES)");
    try expectContains(diff_checker, "validate_fixture_inventory");
    try expectContains(diff_checker, "FIXDEP_DIFF=pass");
    try expectContains(diff_checker, "FIXDEP_DETERMINISM=pass");

    try expectContains(gate_checker, "check-phase2-fixdep-gate.py");
    try expectContains(gate_checker, "check-fixdep-diff.py");
    try expectContains(gate_checker, "python3 scripts/zigux/check-phase2-fixdep-gate.py");
    try expectContains(gate_checker, "python3 scripts/zigux/check-fixdep-diff.py");
    try expectContains(gate_checker, "scripts/zigux/fixdep.zig");
    try expectContains(gate_checker, "scripts/zigux/check-fixdep-diff.py");
    try expectContains(gate_checker, "zigux/tests/fixtures/fixdep/cases.json");
}

test "lane 11 fixdep fixture manifest preserves the external parity packet" {
    const cases = try readRepoFile("zigux/tests/fixtures/fixdep/cases.json");
    defer std.testing.allocator.free(cases);

    try expectAtLeastMarkerCount(cases, "\"name\":", 12);
    try expectContains(cases, "\"sample\"");
    try expectContains(cases, "\"sample_multi_target\"");
    try expectContains(cases, "\"sample_escaped_space\"");
    try expectContains(cases, "\"sample_escaped_colon\"");
    try expectContains(cases, "\"sample_dependency_continuation\"");
    try expectContains(cases, "\"sample_comment_continuation\"");
    try expectContains(cases, "\"sample_comment_only\"");
    try expectContains(cases, "\"sample_missing_dep\"");
    try expectContains(cases, "\"sample_output_write\"");
    try expectContains(cases, "\"expected_exit_code\": 0");
    try expectContains(cases, "\"expected_exit_code\": 1");
    try expectContains(cases, "\"expected_exit_code\": 2");
}

test "lane 11 fixdep docs and routes keep the packet review-visible" {
    const survey = try readRepoFile("Documentation/zigux/phase2-fixdep-dual-implementation-survey.md");
    defer std.testing.allocator.free(survey);

    const closure = try readRepoFile("Documentation/zigux/phase2-closure.md");
    defer std.testing.allocator.free(closure);

    const tests_readme = try readRepoFile("zigux/tests/README.md");
    defer std.testing.allocator.free(tests_readme);

    const makefile = try readRepoFile("zigux/Makefile");
    defer std.testing.allocator.free(makefile);

    const workflow = try readRepoFile(".github/workflows/zigux-bootstrap.yml");
    defer std.testing.allocator.free(workflow);

    try expectContains(survey, "scripts/basic/fixdep.c");
    try expectContains(survey, "scripts/zigux/fixdep.zig");
    try expectContains(survey, "scripts/zigux/check-fixdep-diff.py");
    try expectContains(survey, "zigux/tests/fixtures/fixdep/cases.json");

    try expectContains(closure, "scripts/zigux/check-phase2-fixdep-gate.py");
    try expectContains(closure, "scripts/zigux/check-fixdep-diff.py");
    try expectContains(closure, "python3 scripts/zigux/check-phase2-fixdep-gate.py");

    try expectContains(tests_readme, "scripts/zigux/check-phase2-fixdep-gate.py");
    try expectContains(tests_readme, "scripts/zigux/check-fixdep-diff.py");
    try expectContains(tests_readme, "zig test scripts/zigux/fixdep.zig");

    try expectContains(makefile, "phase2-fixdep");
    try expectContains(makefile, "scripts/zigux/check-phase2-fixdep-gate.py");
    try expectContains(makefile, "scripts/zigux/check-fixdep-diff.py");

    try expectContains(workflow, "python3 scripts/zigux/check-phase2-fixdep-gate.py");
    try expectContains(workflow, "python3 scripts/zigux/check-fixdep-diff.py");
    try expectContains(workflow, "zig test scripts/zigux/fixdep.zig");
}
