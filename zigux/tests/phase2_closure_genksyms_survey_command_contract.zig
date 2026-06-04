const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectAbsent(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "phase 2 closure note keeps genksyms survey replay commands explicit" {
    const closure_note = try readRepoFile("Documentation/zigux/phase2-closure.md", 96 * 1024);
    defer std.testing.allocator.free(closure_note);

    try expectContains(closure_note, "Documentation/zigux/phase2-genksyms-dual-implementation-survey.md");
    try expectContains(closure_note, "scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py");
    try expectContains(closure_note, "`python3 scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py --self-test`");
    try expectContains(closure_note, "`python3 scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py`");
    try expectContains(closure_note, "missing CRC-side dual-implementation gap statement explicit");
    try expectContains(closure_note, "still-missing CRC-side evidence recorded in the survey");
    try expectAbsent(closure_note, "PHASE2_CURRENT_GAP_PACKET=Documentation/zigux/phase2-genksyms-dual-implementation-survey.md");
}

test "phase 2 closure note orders survey replay after wrapper evidence and before terminal helper routes" {
    const closure_note = try readRepoFile("Documentation/zigux/phase2-closure.md", 96 * 1024);
    defer std.testing.allocator.free(closure_note);

    try expectBefore(
        closure_note,
        "`python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py`",
        "`python3 scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py --self-test`",
    );
    try expectBefore(
        closure_note,
        "`python3 scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py --self-test`",
        "`python3 scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py`",
    );
    try expectBefore(
        closure_note,
        "`python3 scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py`",
        "`zig test scripts/zigux/genksyms.zig`",
    );
    try expectBefore(
        closure_note,
        "`zig test scripts/zigux/genksyms.zig`",
        "`make -C zigux phase2-genksyms`",
    );
}

test "phase 2 manifest and validator keep survey surface split visible" {
    const manifest = try readRepoFile("zigux/tests/fixtures/phase2_tool_manifest.json", 160 * 1024);
    defer std.testing.allocator.free(manifest);

    const validator = try readRepoFile("scripts/zigux/validate-phase2-closure.py", 160 * 1024);
    defer std.testing.allocator.free(validator);

    try expectContains(manifest, "\"scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py\"");
    try expectContains(manifest, "\"Documentation/zigux/phase2-closure.md\"");
    try expectContains(manifest, "\"scripts/zigux/validate-phase2-closure.py\"");
    try expectContains(manifest, "\"status\": \"active\"");
    try expectContains(manifest, "\"repo_reality_gaps\": []");

    try expectContains(validator, "GENKSYMS_COMMANDS = (");
    try expectContains(validator, "\"python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py\"");
    try expectContains(validator, "GENKSYMS_REQUIRED_NOTE_MARKERS = (");
    try expectContains(validator, "\"Documentation/zigux/phase2-genksyms-dual-implementation-survey.md\"");
    try expectContains(validator, "expected_workflow_lines = tuple(f\"run: {command}\" for command in GENKSYMS_COMMANDS)");
}
