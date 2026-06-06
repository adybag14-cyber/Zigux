const std = @import("std");

const checker_source = @embedFile("check-phase1-parity.py");

const replay_markers = [_][]const u8{
    "EXPECTED_REPLAY_MARKERS = (",
    "'test \"phase 1 helper ports match committed parity fixture\" {',",
    "'const fixture_bytes = @embedFile(\"fixtures/phase1_helpers.json\");',",
    "\"const Fixture = struct {\",",
};

const replay_build_markers = [_][]const u8{
    "EXPECTED_REPLAY_BUILD_MARKERS = (",
    "'.root_source_file = b.path(\"phase1_helpers.zig\"),',",
    "'.name = \"phase1-helpers\",',",
    "'\"Run the focused Phase 1 helper replay anchor from zigux/tests\",'",
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.TestUnexpectedResult;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.TestUnexpectedResult;
    try std.testing.expect(first_index < second_index);
}

fn expectExactlyOnce(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), std.mem.count(u8, haystack, needle));
}

test "phase1 parity checker owns replay marker rosters" {
    for (replay_markers) |marker| {
        try expectContains(checker_source, marker);
    }
    for (replay_build_markers) |marker| {
        try expectContains(checker_source, marker);
    }

    try expectOrdered(checker_source, "EXPECTED_REPLAY_MARKERS = (", "EXPECTED_REPLAY_BUILD_MARKERS = (");
    try expectOrdered(checker_source, "EXPECTED_REPLAY_BUILD_MARKERS = (", "def check_replay_routes");
}

test "phase1 parity checker validates replay route markers exactly once" {
    try expectContains(checker_source, "def check_replay_routes(root: Path, issues: list[str]) -> None:");
    try expectContains(checker_source, "replay_text = read_text(root / REPLAY_REL)");
    try expectContains(checker_source, "build_text = read_text(root / REPLAY_BUILD_REL)");
    try expectContains(checker_source, "ensure_exact_occurrence(replay_text, f\"replay:{marker}\", marker, issues)");
    try expectContains(checker_source, "ensure_exact_occurrence(build_text, f\"replay_build:{marker}\", marker, issues)");

    try expectExactlyOnce(checker_source, "for marker in EXPECTED_REPLAY_MARKERS:");
    try expectExactlyOnce(checker_source, "for marker in EXPECTED_REPLAY_BUILD_MARKERS:");
    try expectOrdered(checker_source, "check_artifact_diff(root, issues)", "check_replay_routes(root, issues)");
}

test "phase1 parity checker self-test samples replay and build markers" {
    try expectContains(checker_source, "replay_text = \"\\n\".join(EXPECTED_REPLAY_MARKERS) + \"\\n\"");
    try expectContains(checker_source, "replay_build_text = \"\\n\".join(EXPECTED_REPLAY_BUILD_MARKERS) + \"\\n\"");
    try expectContains(checker_source, "write_text(root / REPLAY_REL, replay_text)");
    try expectContains(checker_source, "write_text(root / REPLAY_BUILD_REL, replay_build_text)");
    try expectOrdered(checker_source, "replay_text = \"\\n\".join(EXPECTED_REPLAY_MARKERS) + \"\\n\"", "write_text(root / REPLAY_REL, replay_text)");
    try expectOrdered(checker_source, "replay_build_text = \"\\n\".join(EXPECTED_REPLAY_BUILD_MARKERS) + \"\\n\"", "write_text(root / REPLAY_BUILD_REL, replay_build_text)");
}
