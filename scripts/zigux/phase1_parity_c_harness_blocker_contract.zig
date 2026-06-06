const std = @import("std");

const checker_source = @embedFile("check-phase1-parity.py");
const blocker_packet_path = "zigux/tests/fixtures/phase1_replay_blockers.json";

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.FirstMarkerMissing;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.SecondMarkerMissing;
    try std.testing.expect(first_index < second_index);
}

test "parity checker keeps the C harness route parked instead of required" {
    try expectContains(
        checker_source,
        "HARNESS_REL = Path(\"zigux/tests/fixtures/phase1_helpers_c_harness.c\")",
    );
    try expectContains(
        checker_source,
        "\"phase1_helpers_c_harness_missing_c_sources\"",
    );
    try expectContains(
        checker_source,
        "for rel in (ARTIFACT_DIFF_REL, FIXTURE_REL, MANIFEST_REL, BLOCKERS_REL, REPLAY_REL, REPLAY_BUILD_REL):",
    );
    try std.testing.expect(std.mem.indexOf(
        u8,
        checker_source,
        "for rel in (ARTIFACT_DIFF_REL, FIXTURE_REL, MANIFEST_REL, BLOCKERS_REL, REPLAY_REL, REPLAY_BUILD_REL, HARNESS_REL):",
    ) == null);
    try expectOrdered(
        checker_source,
        "for rel in (ARTIFACT_DIFF_REL, FIXTURE_REL, MANIFEST_REL, BLOCKERS_REL, REPLAY_REL, REPLAY_BUILD_REL):",
        "harness = blockers_payload.get(\"c_harness\")",
    );
}

test "parity checker validates the blocker packet C harness fields exactly" {
    const required_markers = [_][]const u8{
        "ensure(isinstance(harness, dict), \"blockers:c_harness:not_object\", issues)",
        "ensure(harness.get(\"path\") == HARNESS_REL.as_posix(), \"blockers:c_harness:path\", issues)",
        "ensure(harness.get(\"state\") == \"blocked\", \"blockers:c_harness:state\", issues)",
        "ensure(harness.get(\"helper_count\") == len(EXPECTED_HELPERS), \"blockers:c_harness:helper_count\", issues)",
        "ensure(tuple(harness.get(\"helpers\", ())) == EXPECTED_HELPERS, \"blockers:c_harness:helpers\", issues)",
        "ensure(harness.get(\"blocker_id\") == EXPECTED_REPLAY_BLOCKER_IDS[1], \"blockers:c_harness:blocker_id\", issues)",
    };

    for (required_markers) |marker| {
        try expectContains(checker_source, marker);
    }
    try expectOrdered(
        checker_source,
        "EXPECTED_REPLAY_BLOCKER_IDS = (",
        "\"phase1_helpers_c_harness_missing_c_sources\"",
    );
    try expectOrdered(
        checker_source,
        "harness = blockers_payload.get(\"c_harness\")",
        "ensure(harness.get(\"blocker_id\") == EXPECTED_REPLAY_BLOCKER_IDS[1], \"blockers:c_harness:blocker_id\", issues)",
    );
}

test "phase1 replay blocker packet mirrors the parked C harness roster" {
    const blocker_packet = try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        blocker_packet_path,
        std.testing.allocator,
        .limited(1024 * 1024),
    );
    defer std.testing.allocator.free(blocker_packet);

    const blocker_markers = [_][]const u8{
        "\"c_harness\": {",
        "\"path\": \"zigux/tests/fixtures/phase1_helpers_c_harness.c\"",
        "\"state\": \"blocked\"",
        "\"reason\": \"The old host-side parity route still depends on helper `tools/lib/*.c` inputs that current master no longer ships beside the Phase 1 `.zig` ports.\"",
        "\"helper_count\": 13",
        "\"blocker_id\": \"phase1_helpers_c_harness_missing_c_sources\"",
        "\"tools/lib/argv_split.zig\"",
        "\"tools/lib/bitmap.zig\"",
        "\"tools/lib/cmdline.zig\"",
        "\"tools/lib/ctype.zig\"",
        "\"tools/lib/find_bit.zig\"",
        "\"tools/lib/hweight.zig\"",
        "\"tools/lib/list_sort.zig\"",
        "\"tools/lib/rbtree.zig\"",
        "\"tools/lib/slab.zig\"",
        "\"tools/lib/str_error_r.zig\"",
        "\"tools/lib/string.zig\"",
        "\"tools/lib/vsprintf.zig\"",
        "\"tools/lib/zalloc.zig\"",
    };

    for (blocker_markers) |marker| {
        try expectContains(blocker_packet, marker);
    }
    try expectOrdered(
        blocker_packet,
        "\"c_harness\": {",
        "\"blocker_id\": \"phase1_helpers_c_harness_missing_c_sources\"",
    );
}
