const std = @import("std");

const fixdep_test_lines = [_][]const u8{
    "test \"config parsing trims _MODULE and deduplicates symbols\" {",
    "test \"config parsing ignores prefixed CONFIG tokens like upstream fixdep\" {",
    "test \"config parsing accepts CONFIG tokens after punctuation\" {",
    "test \"config parsing stops at the first embedded NUL\" {",
    "test \"dep parsing returns NoTargets for comment-only depfiles\" {",
    "test \"dep parsing keeps escaped spaces inside tokens\" {",
    "test \"dep parsing continues dependency lines across escaped newlines\" {",
    "test \"dep parsing accepts CRLF lines and continuations\" {",
    "test \"dep parsing does not continue bare carriage-return lines\" {",
    "test \"dep parsing skips bytes after the first embedded NUL\" {",
    "test \"ignored and no-parse file classification matches fixdep rules\" {",
    "test \"file read errors map to C-style messages\" {",
    "test \"file read errors map short reads to unexpected end of file\" {",
    "test \"exact read size helper rejects short reads\" {",
    "test \"path error wording keeps the dedicated fstat prefix\" {",
    "test \"open dependency file classification keeps input-output failures on the C-style path\" {",
    "test \"open dependency file classification keeps PermissionDenied on the C-style path\" {",
    "test \"open dependency file classification preserves unrelated open failures\" {",
    "test \"read failure wording matches C perror prefix\" {",
    "test \"output write failure uses C-style wording\" {",
    "test \"flush helper preserves the primary error\" {",
    "test \"dependency file reads beyond the legacy one mebibyte ceiling\" {",
    "test \"escaped hash dependency survives concatenated target comment path\" {",
    "test \"escaped colon dependency survives concatenated target comment path\" {",
    "test \"escaped colon dependency survives concatenated target CRLF comment path\" {",
    "test \"runFixdep preserves escaped colon dependencies through the public entry path\" {",
};

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn countExactQuotedTrimmedLine(text: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, text, '\n');
    while (lines.next()) |line| {
        const trimmed = std.mem.trim(u8, line, " \t\r");
        if (trimmed.len == needle.len + 3 and
            trimmed[0] == '\'' and
            trimmed[trimmed.len - 2] == '\'' and
            trimmed[trimmed.len - 1] == ',' and
            std.mem.eql(u8, trimmed[1 .. trimmed.len - 2], needle))
        {
            count += 1;
        }
    }
    return count;
}

test "phase2 fixdep next-step note records the parked twenty-six-test roster" {
    const note = try readRepoFile("Documentation/zigux/phase2-fixdep-next-step-note.md", 24 * 1024);
    defer std.testing.allocator.free(note);

    try expectContains(note, "The direct Phase 2 gate is truthful again");
    try expectContains(note, "twenty-six named helper-local tests");
    try expectContains(note, "test \"runFixdep preserves escaped colon dependencies through the public entry path\" {");
    try expectContains(note, "The live helper-local test surface is broad enough that this lane does not currently have an honest parser-side, gate-roster-side, or expected-output-side reopen signal.");
    try expectContains(note, "If `scripts/zigux/fixdep.zig` grows another helper-local test, first teach `scripts/zigux/check-phase2-fixdep-gate.py` about that exact new test line");

    try expectNotContains(note, "twenty-five named helper-local tests");
    try expectNotContains(note, "The latest live helper has advanced one step beyond that gate roster");
    try expectNotContains(note, "The narrowest current hardening follow-up is to teach");
}

test "phase2 fixdep gate pins the same twenty-six exact helper test lines" {
    const gate = try readRepoFile("scripts/zigux/check-phase2-fixdep-gate.py", 192 * 1024);
    defer std.testing.allocator.free(gate);

    try expectContains(gate, "FIXDEP_REQUIRED_EXACT_LINES = (");
    try std.testing.expectEqual(@as(usize, 26), fixdep_test_lines.len);
    for (fixdep_test_lines) |line| {
        try std.testing.expectEqual(@as(usize, 1), countExactQuotedTrimmedLine(gate, line));
    }
}

test "phase2 fixdep helper and reminder surfaces keep the public-entry replay visible" {
    const fixdep = try readRepoFile("scripts/zigux/fixdep.zig", 256 * 1024);
    defer std.testing.allocator.free(fixdep);

    const closure = try readRepoFile("Documentation/zigux/phase2-closure.md", 48 * 1024);
    defer std.testing.allocator.free(closure);

    const tests_readme = try readRepoFile("zigux/tests/README.md", 96 * 1024);
    defer std.testing.allocator.free(tests_readme);

    try expectContains(fixdep, "pub fn runFixdep(");
    try expectContains(fixdep, "test \"runFixdep preserves escaped colon dependencies through the public entry path\" {");
    try expectContains(closure, "`scripts/zigux/check-phase2-fixdep-gate.py`");
    try expectContains(closure, "`make -C zigux phase2-fixdep`");
    try expectContains(tests_readme, "`scripts/zigux/check-phase2-fixdep-gate.py`");
    try expectContains(tests_readme, "`scripts/zigux/fixdep.zig`");
    try expectContains(tests_readme, "`make -C zigux phase2-fixdep`");
}
