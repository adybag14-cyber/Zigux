const std = @import("std");

const closure_note_path = "Documentation/zigux/phase2-closure.md";
const survey_path = "Documentation/zigux/phase2-genksyms-dual-implementation-survey.md";
const survey_checker_path = "scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py";
const wrapper_helper_path = "scripts/zigux/genksyms.zig";
const wrapper_checker_path = "scripts/zigux/check-genksyms-bridge.py";
const crc_helper_path = "scripts/zigux/genksyms_crc.zig";
const crc_checker_path = "scripts/zigux/check-genksyms-crc-diff.py";

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1 << 20));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectFilePresent(path: []const u8) !void {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const file = try std.Io.Dir.cwd().openFile(io_instance.io(), path, .{});
    file.close(io_instance.io());
}

fn expectFileMissing(path: []const u8) !void {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    if (std.Io.Dir.cwd().openFile(io_instance.io(), path, .{})) |file| {
        file.close(io_instance.io());
        return error.ExpectedMissingFileWasPresent;
    } else |err| switch (err) {
        error.FileNotFound => {},
        else => return err,
    }
}

test "phase2 closure note points genksyms follow-through at the CRC-side gap" {
    const allocator = std.testing.allocator;
    const closure_note = try readFile(allocator, closure_note_path);
    defer allocator.free(closure_note);

    try expectContains(closure_note, "`PHASE2_STATUS=parked`");
    try expectContains(closure_note, "`PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest`");
    try expectContains(closure_note, "`PHASE2_CURRENT_GENKSYMS_PROCESS_OUTPUT_PACKET=");
    try expectContains(closure_note, "If the `genksyms` lane resumes substantive implementation instead of closure upkeep");
    try expectContains(closure_note, "still-missing CRC-side evidence recorded in the survey");
    try expectContains(closure_note, "rather than widening this shared note again");
    try expectNotContains(closure_note, crc_helper_path);
    try expectNotContains(closure_note, crc_checker_path);
}

test "genksyms survey and survey checker agree on the missing CRC-side packet" {
    const allocator = std.testing.allocator;

    const survey = try readFile(allocator, survey_path);
    defer allocator.free(survey);
    const survey_checker = try readFile(allocator, survey_checker_path);
    defer allocator.free(survey_checker);

    try expectContains(survey, "wrapper bridge landed, deeper same-family dual-implementation evidence missing.");
    try expectContains(survey, "Authenticated current-`master` reads for `" ++ crc_helper_path ++ "` and `" ++ crc_checker_path ++ "` return missing.");
    try expectContains(survey, "restore the missing CRC-side tool-plus-checker evidence");
    try expectContains(survey, "wire the dedicated survey checker into the shared `phase2-genksyms` replay surfaces");

    try expectContains(survey_checker, "\"" ++ crc_helper_path ++ "\",");
    try expectContains(survey_checker, "\"" ++ crc_checker_path ++ "\",");
    try expectContains(survey_checker, "\"wrapper bridge landed, deeper same-family dual-implementation evidence missing.\",");
    try expectContains(survey_checker, "\"restore the missing CRC-side tool-plus-checker evidence\",");
    try expectContains(survey_checker, "EXPECTED_SELF_TEST_CASE_COUNT = 4");
}

test "current repo surface has wrapper genksyms evidence but no CRC-side files" {
    try expectFilePresent(wrapper_helper_path);
    try expectFilePresent(wrapper_checker_path);
    try expectFilePresent(survey_checker_path);

    try expectFileMissing(crc_helper_path);
    try expectFileMissing(crc_checker_path);
}
