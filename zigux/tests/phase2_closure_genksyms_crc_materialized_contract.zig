const std = @import("std");

const repo_files = .{
    .closure = "Documentation/zigux/phase2-closure.md",
    .survey = "Documentation/zigux/phase2-genksyms-dual-implementation-survey.md",
    .survey_checker = "scripts\zigux/check_phase2_genksyms_dual_implementation_survey.zig",
    .manifest = "zigux/tests/fixtures/phase2_tool_manifest.json",
};

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        allocator,
        .limited(1024 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.EarlierMarkerMissing;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.LaterMarkerMissing;
    try std.testing.expect(earlier_index < later_index);
}

test "closure note keeps genksyms CRC evidence materialized beside wrapper bridge evidence" {
    const closure = try readRepoFile(std.testing.allocator, repo_files.closure);
    defer std.testing.allocator.free(closure);

    try expectContains(closure, "scripts\zigux/check_phase2_genksyms_dual_implementation_survey.zig");
    try expectContains(closure, "scripts\zigux/check_genksyms_bridge.zig");
    try expectContains(closure, "scripts/zigux/genksyms.zig");
    try expectContains(closure, "The bridge expected-output packet now explicitly records the eleven committed replay cases");
    try expectContains(closure, "If the `genksyms` lane resumes substantive implementation instead of closure upkeep");
    try expectContains(closure, "preserves the restored CRC-side evidence and wrapper bridge packet");

    try expectContains(closure, "zig run scripts/zigux/check_phase2_genksyms_dual_implementation_survey.zig -- --self-test");
    try expectContains(closure, "zig run scripts/zigux/check_phase2_genksyms_dual_implementation_survey.zig");
    try expectContains(closure, "zig test scripts/zigux/genksyms.zig");
    try expectContains(closure, "make -C zigux phase2-genksyms");
}

test "dedicated survey checker guards the restored CRC-side materialization markers" {
    const survey = try readRepoFile(std.testing.allocator, repo_files.survey);
    defer std.testing.allocator.free(survey);
    const checker = try readRepoFile(std.testing.allocator, repo_files.survey_checker);
    defer std.testing.allocator.free(checker);

    try expectContains(survey, "scripts/zigux/genksyms_crc.zig");
    try expectContains(survey, "scripts\zigux/check_genksyms_crc_diff.zig");
    try expectContains(survey, "CRC-side tool-plus-checker evidence restored");
    try expectContains(survey, "wrapper bridge and CRC-side dual-implementation evidence both materialized.");
    try expectContains(survey, "older inventory-shaped governance gap is no longer truthful on current `master`");

    try expectContains(checker, "scripts/zigux/genksyms_crc.zig");
    try expectContains(checker, "scripts\zigux/check_genksyms_crc_diff.zig");
    try expectContains(checker, "CRC-side tool-plus-checker evidence restored");
    try expectContains(checker, "wrapper bridge and CRC-side dual-implementation evidence both materialized.");
    try expectContains(checker, "PHASE2_GENKSYMS_SURVEY_MARKER_COUNT");
}

test "tool manifest keeps CRC checker and wrapper bridge as distinct Phase 2 surfaces" {
    const manifest = try readRepoFile(std.testing.allocator, repo_files.manifest);
    defer std.testing.allocator.free(manifest);

    try expectContains(manifest, "the dedicated genksyms dual-implementation survey guard");
    try expectContains(manifest, "the manifest-backed genksyms bridge checker");
    try expectContains(manifest, "scripts\zigux/check_phase2_genksyms_dual_implementation_survey.zig");
    try expectContains(manifest, "scripts\zigux/check_genksyms_bridge.zig");
    try expectContains(manifest, "scripts/zigux/genksyms.zig");
    try expectContains(manifest, "zigux/tests/fixtures/genksyms_bridge/manifest.json");
    try expectContains(manifest, "zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json");

    try expectBefore(
        manifest,
        "scripts\zigux/check_phase2_genksyms_dual_implementation_survey.zig",
        "scripts\zigux/check_genksyms_bridge.zig",
    );
}
