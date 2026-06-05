const std = @import("std");
const config = @import("config");

const workflow_path = config.workflow_path;

fn readWorkflow(allocator: std.mem.Allocator) ![]const u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, workflow_path, allocator, .limited(1024 * 1024));
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var rest = haystack;
    while (std.mem.indexOf(u8, rest, needle)) |index| {
        count += 1;
        rest = rest[index + needle.len ..];
    }
    return count;
}

fn requireOnce(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(haystack, needle));
}

fn requireBefore(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

const phase1_smoke = "Run current Phase 1 shared tests-root smoke";
const phase4_repo_reality_selftest = "Self-test current Phase 4 repo-reality warning checker";
const phase4_repo_reality_check = "Check current Phase 4 repo-reality warning packet";
const phase4_reversible_selftest = "Self-test current Phase 4 reversible-delivery pin checker";
const phase4_reversible_check = "Check current Phase 4 reversible-delivery pin packet";
const phase4_tests_readme_selftest = "Self-test current Phase 4 tests README checker";
const phase4_tests_readme_check = "Check current Phase 4 tests README packet";
const phase4_validate = "Validate Phase 4 rollback routes";
const phase4_test = "Run Phase 4 rollback tests";
const phase4_artifact_route = "Run Phase 4 artifact-diff contract make route";
const phase4_artifact_helper_selftest = "Self-test current Phase 4 artifact-diff helper";
const phase4_artifact_contract_selftest = "Self-test current Phase 4 artifact-diff contract checker";
const phase4_artifact_contract_check = "Check current Phase 4 artifact-diff contract packet";

test "phase1 shared smoke hands off to the complete phase4 checker prelude" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try requireOnce(workflow, phase1_smoke);
    try requireOnce(workflow, phase4_repo_reality_selftest);
    try requireOnce(workflow, phase4_repo_reality_check);
    try requireOnce(workflow, phase4_reversible_selftest);
    try requireOnce(workflow, phase4_reversible_check);
    try requireOnce(workflow, phase4_tests_readme_selftest);
    try requireOnce(workflow, phase4_tests_readme_check);

    try requireBefore(workflow, phase1_smoke, phase4_repo_reality_selftest);
    try requireBefore(workflow, phase4_repo_reality_selftest, phase4_repo_reality_check);
    try requireBefore(workflow, phase4_repo_reality_check, phase4_reversible_selftest);
    try requireBefore(workflow, phase4_reversible_selftest, phase4_reversible_check);
    try requireBefore(workflow, phase4_reversible_check, phase4_tests_readme_selftest);
    try requireBefore(workflow, phase4_tests_readme_selftest, phase4_tests_readme_check);
}

test "phase4 rollback and artifact-diff routes remain after phase4 packet checks" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try requireOnce(workflow, phase4_validate);
    try requireOnce(workflow, phase4_test);
    try requireOnce(workflow, phase4_artifact_route);
    try requireOnce(workflow, phase4_artifact_helper_selftest);
    try requireOnce(workflow, phase4_artifact_contract_selftest);
    try requireOnce(workflow, phase4_artifact_contract_check);

    try requireBefore(workflow, phase4_tests_readme_check, phase4_validate);
    try requireBefore(workflow, phase4_validate, phase4_test);
    try requireBefore(workflow, phase4_test, phase4_artifact_route);
    try requireBefore(workflow, phase4_artifact_route, phase4_artifact_helper_selftest);
    try requireBefore(workflow, phase4_artifact_helper_selftest, phase4_artifact_contract_selftest);
    try requireBefore(workflow, phase4_artifact_contract_selftest, phase4_artifact_contract_check);
}

test "phase4 tail does not regress to stale direct checks without selftests" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try std.testing.expectEqual(@as(usize, 0), countOccurrences(workflow, "Run current Phase 4 repo-reality warning checker"));
    try std.testing.expectEqual(@as(usize, 0), countOccurrences(workflow, "Run current Phase 4 reversible-delivery pin checker"));
    try std.testing.expectEqual(@as(usize, 0), countOccurrences(workflow, "Run current Phase 4 tests README checker"));
    try std.testing.expectEqual(@as(usize, 0), countOccurrences(workflow, "make -C zigux phase4\n"));
}
