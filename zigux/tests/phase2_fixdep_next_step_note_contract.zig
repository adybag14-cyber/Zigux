const std = @import("std");

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1 << 22));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var start: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, start, needle)) |index| {
        count += 1;
        start = index + needle.len;
    }
    return count;
}

test "fixdep note stays parked on the current Phase 2 lane and repo packet" {
    const note = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase2-fixdep-next-step-note.md");
    defer std.testing.allocator.free(note);

    try expectContains(note, "Lane: `P2-L06`");
    try expectContains(note, "Current `master` still carries the bounded `scripts/zigux/fixdep.zig` dual-implementation anchor");
    try expectContains(note, "twenty-four helper-local tests");
    try expectContains(note, "13 external fixdep cases");
    try expectContains(note, "Repeated exact-path contents reads still return missing for `scripts/basic/fixdep.c`");
    try expectContains(note, "keep the lane parked until a fresh fixdep-local failure appears");
    try expectContains(note, "Do not widen from this reminder lane into parser behavior, fixture expected outputs, genksyms, kconfig bridge, or the broader shared Phase 2 route inventory");
}

test "fixdep fixture roster matches the note's thirteen-case surface" {
    const cases = try readRepoFile(std.testing.allocator, "zigux/tests/fixtures/fixdep/cases.json");
    defer std.testing.allocator.free(cases);

    try std.testing.expectEqual(@as(usize, 13), countOccurrences(cases, "\"name\""));
    try expectContains(cases, "\"name\": \"sample_dependency_continuation\"");
    try expectContains(cases, "\"name\": \"sample_comment_continuation\"");
    try expectContains(cases, "\"name\": \"sample_double_backslash_comment\"");
    try expectContains(cases, "\"name\": \"sample_comment_only_stdout_full\"");
    try expectContains(cases, "\"name\": \"sample_missing_dep_stdout_full\"");
    try expectContains(cases, "\"name\": \"sample_output_write\"");
    try std.testing.expectEqual(@as(usize, 3), countOccurrences(cases, "\"stdout_mode\": \"dev_full\""));
}

test "fixdep routes and helper-local coverage remain directly named" {
    const note = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase2-fixdep-next-step-note.md");
    defer std.testing.allocator.free(note);
    const makefile = try readRepoFile(std.testing.allocator, "zigux/Makefile");
    defer std.testing.allocator.free(makefile);
    const workflow = try readRepoFile(std.testing.allocator, ".github/workflows/zigux-bootstrap.yml");
    defer std.testing.allocator.free(workflow);
    const fixdep = try readRepoFile(std.testing.allocator, "scripts/zigux/fixdep.zig");
    defer std.testing.allocator.free(fixdep);

    try expectContains(note, "python3 scripts/zigux/check-phase2-fixdep-gate.py");
    try expectContains(note, "python3 scripts/zigux/check-fixdep-diff.py");
    try expectContains(note, "zig test scripts/zigux/fixdep.zig");
    try expectContains(makefile, "$(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py");
    try expectContains(makefile, "$(PYTHON) scripts/zigux/check-fixdep-diff.py");
    try expectContains(makefile, "$(ZIG) test scripts/zigux/fixdep.zig");
    try expectContains(workflow, "python3 scripts/zigux/check-phase2-fixdep-gate.py");
    try expectContains(workflow, "python3 scripts/zigux/check-fixdep-diff.py");
    try expectContains(workflow, "zig test scripts/zigux/fixdep.zig");

    try expectContains(note, "Documentation/zigux/artifact-diff.md");
    try expectContains(note, "scripts/zigux/check-phase2-fixdep-gate.py");
    try expectContains(note, "scripts/zigux/check-fixdep-diff.py");
    try expectContains(fixdep, "test \"config parsing stops at the first embedded NUL\"");
    try expectContains(fixdep, "test \"dep parsing skips bytes after the first embedded NUL\"");
    try expectContains(fixdep, "test \"dep parsing unescapes escaped hash and colon dependency tokens\"");
}
