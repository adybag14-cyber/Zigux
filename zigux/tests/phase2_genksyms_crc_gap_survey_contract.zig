const std = @import("std");

const closure_note_path = "Documentation/zigux/phase2-closure.md";
const survey_note_path = "Documentation/zigux/phase2-genksyms-dual-implementation-survey.md";

const missing_crc_evidence = [_][]const u8{
    "scripts/zigux/genksyms_crc.zig",
    "scripts/zigux/check-genksyms-crc-diff.py",
};

const lean_crc_restore_packet = [_][]const u8{
    "scripts/zigux/genksyms_crc.zig",
    "scripts/zigux/check-genksyms-crc-diff.py",
    "zigux/tests/fixtures/genksyms_crc/genksyms_crc_c_harness.c",
    "zigux/tests/fixtures/genksyms_crc/inputs.txt",
    "zigux/tests/fixtures/genksyms_crc/expected.json",
};

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        allocator,
        .limited(limit),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "genksyms survey keeps the dual-implementation roadmap and ledger split explicit" {
    const survey_note = try readRepoFile(std.testing.allocator, survey_note_path, 24 * 1024);
    defer std.testing.allocator.free(survey_note);

    try expectContains(survey_note, "## Roadmap and ledger anchor");
    try expectContains(survey_note, "scripts/genksyms/genksyms.c");
    try expectContains(survey_note, "scripts/zigux/genksyms.zig");
    try expectContains(survey_note, "selected dual implementations");
    try expectContains(survey_note, "wrapper-first");
    try expectContains(survey_note, "The bootstrap ledger records two same-family genksyms steps rather than one");
    for (missing_crc_evidence) |needle| {
        try expectContains(survey_note, needle);
    }
}

test "genksyms survey states the current CRC-side repo-reality gap" {
    const survey_note = try readRepoFile(std.testing.allocator, survey_note_path, 24 * 1024);
    defer std.testing.allocator.free(survey_note);

    try expectContains(survey_note, "## Current repo-reality gap");
    try expectContains(survey_note, "return missing");
    try expectContains(survey_note, "no longer name the CRC-side tool, checker, or fixture family as active current-master proof");
    try expectContains(survey_note, "wrapper bridge landed, deeper same-family dual-implementation evidence missing");
}

test "closure note and survey point the next genksyms work back to CRC-side evidence" {
    const closure_note = try readRepoFile(std.testing.allocator, closure_note_path, 24 * 1024);
    defer std.testing.allocator.free(closure_note);
    const survey_note = try readRepoFile(std.testing.allocator, survey_note_path, 24 * 1024);
    defer std.testing.allocator.free(survey_note);

    try expectContains(closure_note, "If the `genksyms` lane resumes substantive implementation instead of closure upkeep");
    try expectContains(closure_note, "still-missing CRC-side evidence recorded in the survey");
    try expectContains(closure_note, "rather than widening this shared note again");
    try expectContains(survey_note, "start with one smallest same-family closure step around the missing CRC-side packet");
    try expectContains(survey_note, "restore the missing CRC-side tool-plus-checker evidence before widening beyond `genksyms`");
}

test "lean CRC restore packet stays implementation-evidence scoped" {
    try std.testing.expectEqual(@as(usize, 5), lean_crc_restore_packet.len);

    var saw_tool = false;
    var saw_checker = false;
    var fixture_count: usize = 0;
    for (lean_crc_restore_packet) |path| {
        if (std.mem.eql(u8, path, "scripts/zigux/genksyms_crc.zig")) saw_tool = true;
        if (std.mem.eql(u8, path, "scripts/zigux/check-genksyms-crc-diff.py")) saw_checker = true;
        if (std.mem.startsWith(u8, path, "zigux/tests/fixtures/genksyms_crc/")) fixture_count += 1;

        try expectNotContains(path, ".github/workflows/");
        try expectNotContains(path, "Documentation/zigux/phase2-closure.md");
        try expectNotContains(path, "zigux/Makefile");
    }

    try std.testing.expect(saw_tool);
    try std.testing.expect(saw_checker);
    try std.testing.expectEqual(@as(usize, 3), fixture_count);
}
