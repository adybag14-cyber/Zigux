const std = @import("std");

const closure_note_path = "Documentation/zigux/phase2-closure.md";
const genksyms_survey_path = "Documentation/zigux/phase2-genksyms-dual-implementation-survey.md";

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.containsAtLeast(u8, haystack, 1, needle));
}

fn expectMissing(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "phase2 closure names crc-side genksyms evidence as the next implementation step" {
    const closure_note = try std.Io.Dir.cwd().readFileAlloc(std.testing.io, closure_note_path, std.testing.allocator, .limited(64 * 1024));
    defer std.testing.allocator.free(closure_note);

    try expectContains(closure_note, "## Next Step");
    try expectContains(
        closure_note,
        "If the `genksyms` lane resumes substantive implementation instead of closure upkeep",
    );
    try expectContains(
        closure_note,
        "the still-missing CRC-side evidence recorded in the survey",
    );
}

test "phase2 genksyms survey keeps the crc-side files in the missing-evidence packet" {
    const genksyms_survey = try std.Io.Dir.cwd().readFileAlloc(std.testing.io, genksyms_survey_path, std.testing.allocator, .limited(64 * 1024));
    defer std.testing.allocator.free(genksyms_survey);

    try expectContains(genksyms_survey, "## Current repo-reality gap");
    try expectContains(
        genksyms_survey,
        "Authenticated current-`master` reads for `scripts/zigux/genksyms_crc.zig` and `scripts/zigux/check-genksyms-crc-diff.py` return missing.",
    );
    try expectContains(
        genksyms_survey,
        "The current directly readable Phase 2 closure packet and validator packet also no longer name the CRC-side tool, checker, or fixture family as active current-master proof",
    );
}

test "phase2 genksyms survey distinguishes wrapper bridge from full dual implementation closure" {
    const genksyms_survey = try std.Io.Dir.cwd().readFileAlloc(std.testing.io, genksyms_survey_path, std.testing.allocator, .limited(64 * 1024));
    defer std.testing.allocator.free(genksyms_survey);

    try expectContains(
        genksyms_survey,
        "The truthful current state for lane `P2-L07` is therefore: wrapper bridge landed, deeper same-family dual-implementation evidence missing.",
    );
    try expectContains(
        genksyms_survey,
        "start with one smallest same-family closure step around the missing CRC-side packet",
    );
    try expectContains(
        genksyms_survey,
        "restore the missing CRC-side tool-plus-checker evidence before widening beyond `genksyms`",
    );
}

test "phase2 closure does not advertise crc-side genksyms as active replay evidence" {
    const closure_note = try std.Io.Dir.cwd().readFileAlloc(std.testing.io, closure_note_path, std.testing.allocator, .limited(64 * 1024));
    defer std.testing.allocator.free(closure_note);

    try expectContains(closure_note, "## Current Genksyms Evidence");
    try expectContains(closure_note, "scripts/zigux/genksyms.zig");
    try expectContains(closure_note, "scripts/zigux/check-genksyms-bridge.py");
    try expectMissing(closure_note, "scripts/zigux/genksyms_crc.zig remains");
    try expectMissing(closure_note, "scripts/zigux/check-genksyms-crc-diff.py remains");
}
