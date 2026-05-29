const std = @import("std");

const checker_source = @embedFile("check-phase2-cross-selftest-alignment.py");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase2 cross alignment checker keeps public self-test action path" {
    try expectContains(checker_source, "def run_self_test() -> int:");
    try expectContains(checker_source, "PHASE2_CROSS_ALIGNMENT_SELF_TEST=pass");
    try expectContains(checker_source, "PHASE2_CROSS_ALIGNMENT_SELF_TEST_CASE_COUNT");
    try expectContains(checker_source, "--self-test");
    try expectContains(checker_source, "Run built-in");
    try expectContains(checker_source, "PHASE2_CROSS_ALIGNMENT=pass");
}

test "phase2 cross alignment checker anchors the live route files" {
    try expectContains(checker_source, "scripts/zigux/check-phase2-cross.py");
    try expectContains(checker_source, "scripts/zigux/check-phase2-cross-selftest-alignment.py");
    try expectContains(checker_source, "phase2-toolchain-bootstrap-notes.md");
    try expectContains(checker_source, "review-checklist.md");
    try expectContains(checker_source, "zigux/tests/fixtures/phase2_cross_targets.json");
    try expectContains(checker_source, "make -C zigux phase2-cross");
}

test "phase2 cross alignment checker preserves action-path diagnostics" {
    try expectContains(checker_source, "PHASE2_CROSS_ALIGNMENT=fail");
    try expectContains(checker_source, "INVALID_PHASE2_CROSS_ALIGNMENT_START");
    try expectContains(checker_source, "INVALID_PHASE2_CROSS_ALIGNMENT_END");
    try expectContains(checker_source, "missing_marker");
    try expectContains(checker_source, "MISSING_PHASE2_CROSS_ALIGNMENT_FILES_START");
    try expectContains(checker_source, "phase2_cross_targets");
}
