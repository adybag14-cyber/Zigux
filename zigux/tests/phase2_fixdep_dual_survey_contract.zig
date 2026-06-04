const std = @import("std");
const testing = std.testing;

const max_file_bytes = 4 * 1024 * 1024;

const survey_path = "Documentation/zigux/phase2-fixdep-dual-implementation-survey.md";
const fixdep_gate_path = "scripts/zigux/check-phase2-fixdep-gate.py";
const fixdep_diff_path = "scripts/zigux/check-fixdep-diff.py";
const fixdep_helper_path = "scripts/zigux/fixdep.zig";
const fixdep_cases_path = "zigux/tests/fixtures/fixdep/cases.json";
const closure_path = "Documentation/zigux/phase2-closure.md";
const tests_readme_path = "zigux/tests/README.md";
const scripts_readme_path = "scripts/zigux/README.md";
const makefile_path = "zigux/Makefile";
const c_anchor_path = "scripts/basic/fixdep.c";

fn readRepoFile(allocator: std.mem.Allocator, rel_path: []const u8) ![]u8 {
    const roots = [_][]const u8{ ".", "../.." };
    for (roots) |root| {
        const path = try std.fs.path.join(allocator, &.{ root, rel_path });
        defer allocator.free(path);
        return std.Io.Dir.cwd().readFileAlloc(
            std.testing.io,
            path,
            allocator,
            .limited(max_file_bytes),
        ) catch |err| switch (err) {
            error.FileNotFound => continue,
            else => return err,
        };
    }
    return error.FileNotFound;
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "fixdep dual survey records the current Phase 2 packet" {
    const allocator = testing.allocator;
    const survey = try readRepoFile(allocator, survey_path);
    defer allocator.free(survey);

    try expectContains(survey, "Lane: `P2-L01`");
    try expectContains(survey, "The Phase 2 roadmap still keeps `scripts/basic/fixdep.c` and `scripts/zigux/fixdep.zig` inside the selected dual-implementation tranche");
    try expectContains(survey, "bounded thirteen-case external fixdep packet");
    try expectContains(survey, "Current `scripts/zigux/fixdep.zig` already captures `error.PermissionDenied`");
    try expectContains(survey, "Exact-path authenticated contents reads still return missing for `scripts/basic/fixdep.c`");
    try expectContains(survey, "Current `master` now directly serves `Documentation/zigux/artifact-diff.md`");
    try expectContains(survey, "The shared closure note now enumerates `Documentation/zigux/phase2-fixdep-dual-implementation-survey.md`");
    try expectContains(survey, "Keep `scripts/zigux/check-phase2-fixdep-gate.py` aligned with the current helper-local test roster");
    try expectNotContains(survey, "bounded twelve-case external fixdep packet");
    try expectNotContains(survey, "helper still omits `error.PermissionDenied`");
}

test "fixdep gate and fixtures match the survey roster" {
    const allocator = testing.allocator;
    const gate = try readRepoFile(allocator, fixdep_gate_path);
    defer allocator.free(gate);
    const diff_checker = try readRepoFile(allocator, fixdep_diff_path);
    defer allocator.free(diff_checker);
    const cases = try readRepoFile(allocator, fixdep_cases_path);
    defer allocator.free(cases);
    const parsed_cases = try std.json.parseFromSlice(std.json.Value, allocator, cases, .{});
    defer parsed_cases.deinit();

    try testing.expectEqual(@as(usize, 13), parsed_cases.value.array.items.len);
    try expectContains(gate, "EXPECTED_FIXDEP_TEST_COUNT = 26");
    try expectContains(gate, "\"sample_dependency_continuation\"");
    try expectContains(gate, "\"sample_comment_continuation\"");
    try expectContains(gate, "\"sample_double_backslash_comment\"");
    try expectContains(gate, "\"sample_missing_dep_stdout_full\"");
    try expectContains(gate, "runFixdep preserves escaped colon dependencies through the public entry path");
    try expectContains(diff_checker, "EXPECTED_SELF_TEST_CASE_COUNT = 16");
    try expectContains(diff_checker, "EXPECTED_CASE_ORDER = list(EXPECTED_CASES)");
}

test "fixdep helper and reminder surfaces keep the survey packet replayable" {
    const allocator = testing.allocator;
    const helper = try readRepoFile(allocator, fixdep_helper_path);
    defer allocator.free(helper);
    const closure = try readRepoFile(allocator, closure_path);
    defer allocator.free(closure);
    const tests_readme = try readRepoFile(allocator, tests_readme_path);
    defer allocator.free(tests_readme);
    const scripts_readme = try readRepoFile(allocator, scripts_readme_path);
    defer allocator.free(scripts_readme);
    const makefile = try readRepoFile(allocator, makefile_path);
    defer allocator.free(makefile);

    try expectContains(helper, "error.AccessDenied,");
    try expectContains(helper, "error.PermissionDenied,");
    try expectContains(helper, "test \"open dependency file classification keeps PermissionDenied on the C-style path\" {");
    try expectContains(helper, "test \"runFixdep preserves escaped colon dependencies through the public entry path\" {");

    try expectContains(closure, survey_path);
    try expectContains(closure, "scripts/zigux/check-phase2-fixdep-gate.py");
    try expectContains(closure, "scripts/zigux/check-fixdep-diff.py");
    try expectContains(closure, "make -C zigux phase2-fixdep");

    try expectContains(tests_readme, survey_path);
    try expectContains(tests_readme, "zigux/tests/fixtures/fixdep/cases.json");
    try expectContains(scripts_readme, "scripts/zigux/check-phase2-fixdep-gate.py");
    try expectContains(scripts_readme, "python3 scripts/zigux/check-fixdep-diff.py --self-test");
    try expectContains(makefile, "phase2-fixdep: phase2-toolchain");
    try expectContains(makefile, "check-phase2-fixdep-gate.py --self-test");
    try expectContains(makefile, "check-fixdep-diff.py --zig");

    try testing.expectError(error.FileNotFound, readRepoFile(allocator, c_anchor_path));
}
