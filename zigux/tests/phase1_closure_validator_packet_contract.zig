const std = @import("std");

const closure_note_path = "Documentation/zigux/phase1-closure.md";
const closure_validator_path = "scripts/zigux/validate-phase1-closure.py";

const ReminderEntry = struct {
    path: []const u8,
    validator_symbol: ?[]const u8 = null,
};

const current_reminder_packet = [_]ReminderEntry{
    .{ .path = "Documentation/zigux/phase1-closure.md", .validator_symbol = "PHASE1_CLOSURE_REL" },
    .{ .path = "Documentation/zigux/phase1-host-helper-lane-sequencing.md", .validator_symbol = "PHASE1_LANE_NOTE_REL" },
    .{ .path = "Documentation/zigux/README.md", .validator_symbol = "DOCS_ROOT_REL" },
    .{ .path = "Documentation/zigux/review-checklist.md", .validator_symbol = "REVIEW_CHECKLIST_REL" },
    .{ .path = "scripts/zigux/README.md", .validator_symbol = "SCRIPTS_README_REL" },
    .{ .path = "scripts/zigux/check-phase1-string-review-packet.py", .validator_symbol = "STRING_REVIEW_CHECKER_REL" },
    .{ .path = "scripts/zigux/check-phase1-direct-owner-markers.py", .validator_symbol = "DIRECT_OWNER_CHECKER_REL" },
    .{ .path = "scripts/zigux/check-phase1-direct-anchor-manifest-gate.py", .validator_symbol = "DIRECT_ANCHOR_MANIFEST_GATE_REL" },
    .{ .path = "scripts/zigux/check-phase1-bench.py", .validator_symbol = "BENCH_CHECKER_REL" },
    .{ .path = "scripts/zigux/check-phase1-shared-reminder-packet.py", .validator_symbol = "SHARED_REMINDER_CHECKER_REL" },
    .{ .path = "scripts/zigux/validate-phase1-closure.py", .validator_symbol = null },
    .{ .path = "zigux/tests/README.md", .validator_symbol = "TESTS_README_REL" },
    .{ .path = "zigux/tests/build.zig", .validator_symbol = "TESTS_BUILD_REL" },
    .{ .path = "zigux/tests/phase1_helpers.zig", .validator_symbol = "PHASE1_HELPERS_REPLAY_REL" },
    .{ .path = "zigux/tests/phase1_helpers_build.zig", .validator_symbol = "PHASE1_HELPERS_BUILD_REL" },
    .{ .path = "zigux/tests/phase1_host_tools_smoke.zig", .validator_symbol = "PHASE1_SMOKE_REL" },
    .{ .path = ".github/workflows/zigux-bootstrap.yml", .validator_symbol = "WORKFLOW_REL" },
    .{ .path = "zigux/tests/fixtures/phase1_helper_manifest.json", .validator_symbol = "MANIFEST_REL" },
};

const gap_packet = [_][]const u8{
    "scripts/zigux/validate-phase1.py",
    "scripts/zigux/check-phase1-parity.py",
    "zigux/tests/phase1_bench.zig",
    "zigux/tests/fixtures/phase1_bench_expectations.json",
    "zigux/tests/fixtures/phase1_helpers_c_harness.c",
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectOrderedAfter(haystack: []const u8, start: usize, needle: []const u8) !usize {
    const offset = std.mem.indexOfPos(u8, haystack, start, needle) orelse return error.MissingOrderedNeedle;
    return offset + needle.len;
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var start: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, start, needle)) |offset| {
        count += 1;
        start = offset + needle.len;
    }
    return count;
}

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, std.testing.allocator, .limited(limit));
}

test "phase1 closure note keeps the current reminder packet exact and ordered" {
    const closure_note = try readRepoFile(closure_note_path, 128 * 1024);
    defer std.testing.allocator.free(closure_note);

    try expectContains(closure_note, "`PHASE1_STATUS=parked`");
    try expectContains(closure_note, "`PHASE1_CLOSURE_RESTORE_STATE=docs_plus_validator`");
    try expectContains(closure_note, "`PHASE1_HELPER_COUNT=13`");
    try expectContains(closure_note, "`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`");
    try expectNotContains(closure_note, "`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`");

    var cursor = try expectOrderedAfter(closure_note, 0, "## Current Reminder Packet");
    inline for (current_reminder_packet) |entry| {
        cursor = try expectOrderedAfter(closure_note, cursor, entry.path);
    }

    const exact_packet_prefix = "`PHASE1_CURRENT_REMINDER_PACKET=";
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(closure_note, exact_packet_prefix));
    inline for (current_reminder_packet) |entry| {
        try expectContains(closure_note, entry.path);
    }
}

test "phase1 closure keeps broader closure companions parked outside the current packet" {
    const closure_note = try readRepoFile(closure_note_path, 128 * 1024);
    defer std.testing.allocator.free(closure_note);

    try expectContains(closure_note, "## Broader Closure Companions");
    try expectContains(closure_note, "`PHASE1_CURRENT_GAP_PACKET=");
    inline for (gap_packet) |path| {
        try expectContains(closure_note, path);
    }

    try expectContains(closure_note, "It still does not expose `make -C zigux phase1-validate`");
    try expectContains(closure_note, "older Phase 1 wrapper names remain historical packet members rather than active closure proof");
}

test "phase1 closure validator owns the same current authority files" {
    const closure_validator = try readRepoFile(closure_validator_path, 256 * 1024);
    defer std.testing.allocator.free(closure_validator);

    try expectContains(closure_validator, "REQUIRED_FILES = (");
    try expectContains(closure_validator, "EXPECTED_CLOSURE_MARKERS = {");
    try expectContains(closure_validator, "FORBIDDEN_CLOSURE_MARKERS = {");

    inline for (current_reminder_packet) |entry| {
        try expectContains(closure_validator, entry.path);
        if (entry.validator_symbol) |symbol| {
            try expectContains(closure_validator, symbol);
        }
    }
}

test "phase1 closure validator protects helper-family closure review guards" {
    const closure_note = try readRepoFile(closure_note_path, 128 * 1024);
    defer std.testing.allocator.free(closure_note);
    const closure_validator = try readRepoFile(closure_validator_path, 256 * 1024);
    defer std.testing.allocator.free(closure_validator);

    const required_guard_markers = [_][]const u8{
        "PHASE1_DIRECT_ANCHOR_MANIFEST_GATE",
        "PHASE1_FIND_BIT_BENCH_ANCHOR_GUARD",
        "PHASE1_FIND_BIT_REVIEW_GUARD",
        "PHASE1_RBTREE_REVIEW_GUARD",
        "PHASE1_STRING_REVIEW_GUARD",
        "PHASE1_BITMAP_DIRECT_REVIEW",
        "PHASE1_NEXT_SAFE_STEP",
    };
    inline for (required_guard_markers) |marker| {
        try expectContains(closure_note, marker);
        try expectContains(closure_validator, marker);
    }
}
