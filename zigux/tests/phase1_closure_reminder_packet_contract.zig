const std = @import("std");
const testing = std.testing;

const closure_reminder_packet =
    \\`PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,scripts/zigux/README.md,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-direct-anchor-manifest-gate.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py,scripts/zigux/validate-phase1-closure.py,zigux/tests/README.md,zigux/tests/build.zig,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_helpers_build.zig,zigux/tests/phase1_host_tools_smoke.zig,.github/workflows/zigux-bootstrap.yml,zigux/tests/fixtures/phase1_helper_manifest.json`
;

const validator_required_files_packet =
    \\REQUIRED_FILES = (
    \\    PHASE1_CLOSURE_REL,
    \\    PHASE1_LANE_NOTE_REL,
    \\    DOCS_ROOT_REL,
    \\    REVIEW_CHECKLIST_REL,
    \\    SCRIPTS_README_REL,
    \\    STRING_REVIEW_CHECKER_REL,
    \\    FIND_BIT_REVIEW_CHECKER_REL,
    \\    RBTREE_REVIEW_CHECKER_REL,
    \\    DIRECT_OWNER_CHECKER_REL,
    \\    DIRECT_ANCHOR_MANIFEST_GATE_REL,
    \\    ROUTE_SUMMARY_CHECKER_REL,
    \\    BENCH_CHECKER_REL,
    \\    FIND_BIT_BENCH_ANCHOR_CHECKER_REL,
    \\    BITMAP_DIRECT_ANCHOR_CHECKER_REL,
    \\    SHARED_REMINDER_CHECKER_REL,
    \\    TESTS_README_REL,
    \\    TESTS_BUILD_REL,
    \\    PHASE1_HELPERS_REPLAY_REL,
    \\    PHASE1_HELPERS_BUILD_REL,
    \\    PHASE1_SMOKE_REL,
    \\    WORKFLOW_REL,
    \\    MANIFEST_REL,
    \\    ZIGUX_MAKEFILE_REL,
    \\    BITMAP_HELPER_REL,
    \\    FIND_BIT_HELPER_REL,
    \\    RBTREE_HELPER_REL,
    \\    STRING_HELPER_REL,
    \\)
;

const expected_reminder_entries = [_]ReminderEntry{
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
    .{ .path = "scripts/zigux/validate-phase1-closure.py" },
    .{ .path = "zigux/tests/README.md", .validator_symbol = "TESTS_README_REL" },
    .{ .path = "zigux/tests/build.zig", .validator_symbol = "TESTS_BUILD_REL" },
    .{ .path = "zigux/tests/phase1_helpers.zig", .validator_symbol = "PHASE1_HELPERS_REPLAY_REL" },
    .{ .path = "zigux/tests/phase1_helpers_build.zig", .validator_symbol = "PHASE1_HELPERS_BUILD_REL" },
    .{ .path = "zigux/tests/phase1_host_tools_smoke.zig", .validator_symbol = "PHASE1_SMOKE_REL" },
    .{ .path = ".github/workflows/zigux-bootstrap.yml", .validator_symbol = "WORKFLOW_REL" },
    .{ .path = "zigux/tests/fixtures/phase1_helper_manifest.json", .validator_symbol = "MANIFEST_REL" },
};

const adjacent_validator_only_symbols = [_][]const u8{
    "FIND_BIT_REVIEW_CHECKER_REL",
    "RBTREE_REVIEW_CHECKER_REL",
    "ROUTE_SUMMARY_CHECKER_REL",
    "FIND_BIT_BENCH_ANCHOR_CHECKER_REL",
    "BITMAP_DIRECT_ANCHOR_CHECKER_REL",
    "ZIGUX_MAKEFILE_REL",
    "BITMAP_HELPER_REL",
    "FIND_BIT_HELPER_REL",
    "RBTREE_HELPER_REL",
    "STRING_HELPER_REL",
};

const ReminderEntry = struct {
    path: []const u8,
    validator_symbol: ?[]const u8 = null,
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, left: []const u8, right: []const u8) !void {
    const left_index = std.mem.indexOf(u8, haystack, left) orelse return error.MissingLeftNeedle;
    const right_index = std.mem.indexOf(u8, haystack, right) orelse return error.MissingRightNeedle;
    try testing.expect(left_index < right_index);
}

fn expectOccursOnce(haystack: []const u8, needle: []const u8) !void {
    const first = std.mem.indexOf(u8, haystack, needle) orelse return error.MissingNeedle;
    const after_first = first + needle.len;
    try testing.expect(std.mem.indexOf(u8, haystack[after_first..], needle) == null);
}

test "closure reminder packet keeps the exact current roster and order" {
    try expectContains(closure_reminder_packet, "PHASE1_CURRENT_REMINDER_PACKET=");

    inline for (expected_reminder_entries, 0..) |entry, index| {
        try expectContains(closure_reminder_packet, entry.path);
        try expectOccursOnce(closure_reminder_packet, entry.path);

        if (index > 0) {
            try expectBefore(
                closure_reminder_packet,
                expected_reminder_entries[index - 1].path,
                entry.path,
            );
        }
    }

    try testing.expectEqual(@as(usize, 18), expected_reminder_entries.len);
    try expectBefore(closure_reminder_packet, "scripts/zigux/validate-phase1-closure.py", "zigux/tests/README.md");
    try expectBefore(closure_reminder_packet, "zigux/tests/phase1_host_tools_smoke.zig", ".github/workflows/zigux-bootstrap.yml");
}

test "closure reminder entries stay backed by validator required-file symbols" {
    inline for (expected_reminder_entries) |entry| {
        if (entry.validator_symbol) |symbol| {
            try expectContains(validator_required_files_packet, symbol);
        } else {
            try testing.expectEqualStrings("scripts/zigux/validate-phase1-closure.py", entry.path);
        }
    }

    try expectContains(validator_required_files_packet, "REQUIRED_FILES = (");
    try expectBefore(validator_required_files_packet, "PHASE1_CLOSURE_REL", "MANIFEST_REL");
    try expectBefore(validator_required_files_packet, "TESTS_README_REL", "WORKFLOW_REL");
}

test "validator-only closure guards remain adjacent to the public reminder roster" {
    inline for (adjacent_validator_only_symbols) |symbol| {
        try expectContains(validator_required_files_packet, symbol);
        try testing.expect(std.mem.indexOf(u8, closure_reminder_packet, symbol) == null);
    }

    try expectContains(validator_required_files_packet, "ROUTE_SUMMARY_CHECKER_REL");
    try expectContains(closure_reminder_packet, "scripts/zigux/check-phase1-shared-reminder-packet.py");
    try testing.expect(std.mem.indexOf(u8, closure_reminder_packet, "scripts/zigux/check-phase1-route-summary-counts.py") == null);
}
