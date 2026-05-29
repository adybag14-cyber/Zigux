const std = @import("std");
const testing = std.testing;

test "phase2-cross make route keeps the direct checker pair wired" {
    const makefile = try readTestFile("../Makefile");
    defer testing.allocator.free(makefile);

    const phase2_cross = targetBody(makefile, "phase2-cross") orelse return error.MissingPhase2CrossTarget;

    try expectContains(phase2_cross, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py --self-test");
    try expectContains(phase2_cross, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py");
    try expectContains(phase2_cross, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py --self-test");
    try expectContains(phase2_cross, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py");
    try expectContains(makefile, "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep");
}

test "phase2-cross route stays aligned with the cross target fixture" {
    const fixture = try readTestFile("fixtures/phase2_cross_targets.json");
    defer testing.allocator.free(fixture);

    try expectContains(fixture, "\"route\": \"make -C zigux phase2-cross\"");
    try testing.expectEqual(@as(usize, 3), std.mem.count(u8, fixture, "make -C zigux phase2-cross"));
    try expectContains(fixture, "\"target\": \"x86_64-linux\"");
    try expectContains(fixture, "\"validation_mode\": \"archive_required\"");
    try expectContains(fixture, "\"target\": \"aarch64-linux\"");
    try expectContains(fixture, "\"validation_mode\": \"route_contract_only\"");
}

fn readTestFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(testing.io, path, testing.allocator, .limited(128 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn targetBody(text: []const u8, target: []const u8) ?[]const u8 {
    var line_start: usize = 0;
    while (line_start < text.len) {
        const line_end = std.mem.indexOfScalarPos(u8, text, line_start, '\n') orelse text.len;
        const line = text[line_start..line_end];
        if (isTargetLine(line, target)) {
            const body_start = if (line_end < text.len) line_end + 1 else line_end;
            return text[body_start..targetEnd(text, body_start)];
        }
        line_start = if (line_end < text.len) line_end + 1 else text.len;
    }
    return null;
}

fn targetEnd(text: []const u8, body_start: usize) usize {
    var line_start = body_start;
    while (line_start < text.len) {
        const line_end = std.mem.indexOfScalarPos(u8, text, line_start, '\n') orelse text.len;
        const line = text[line_start..line_end];
        if (line.len != 0 and line[0] != '\t' and std.mem.indexOfScalar(u8, line, ':') != null) {
            return line_start;
        }
        line_start = if (line_end < text.len) line_end + 1 else text.len;
    }
    return text.len;
}

fn isTargetLine(line: []const u8, target: []const u8) bool {
    if (!std.mem.startsWith(u8, line, target)) return false;
    if (line.len <= target.len or line[target.len] != ':') return false;
    return std.mem.indexOfScalar(u8, line, '=') == null;
}
