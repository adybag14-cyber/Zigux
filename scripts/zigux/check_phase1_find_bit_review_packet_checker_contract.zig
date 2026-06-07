const std = @import("std");

const source_path = "scripts/zigux/check-phase1-find-bit-review-packet.py";

fn readSource(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        source_path,
        allocator,
        .limited(512 * 1024),
    );
}

fn expectContains(source: []const u8, marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, source, marker) != null);
}

fn expectContainsInOrder(source: []const u8, markers: []const []const u8) !void {
    var cursor: usize = 0;
    for (markers) |marker| {
        const found = std.mem.indexOf(u8, source[cursor..], marker) orelse return error.MarkerOutOfOrder;
        cursor += found + marker.len;
    }
}

test "find-bit review checker keeps required file roster and duplicate tracking" {
    const source = try readSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    const required_paths = [_][]const u8{
        "HELPER_REL = Path(\"tools/lib/find_bit.zig\")",
        "LANE_NOTE_REL = Path(\"Documentation/zigux/phase1-host-helper-lane-sequencing.md\")",
        "CLOSURE_NOTE_REL = Path(\"Documentation/zigux/phase1-closure.md\")",
        "MANIFEST_REL = Path(\"zigux/tests/fixtures/phase1_helper_manifest.json\")",
        "FIXTURE_REL = Path(\"zigux/tests/fixtures/phase1_helpers.json\")",
        "SMOKE_REL = Path(\"zigux/tests/phase1_host_tools_smoke.zig\")",
        "FIND_BIT_REL = \"tools/lib/find_bit.zig\"",
    };
    for (required_paths) |marker| {
        try expectContains(source, marker);
    }

    try expectContainsInOrder(source, &.{
        "class DuplicateTrackingDict(dict[str, object]):",
        "self.duplicate_keys: list[str] = []",
        "if key in self and key not in self.duplicate_keys:",
        "self.duplicate_keys.append(key)",
        "duplicate_paths(data: object",
    });
}

test "find-bit review checker pins helper symbols anchors and fixture values" {
    const source = try readSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    const helper_symbols = [_][]const u8{
        "findFirstBit",
        "findFirstAndBit",
        "findFirstAndNotBit",
        "findFirstZeroBit",
        "findNextBit",
        "findNextAndBit",
        "findNextOrBit",
        "findNextAndNotBit",
        "findNextZeroBit",
        "findNextClump8",
        "findFirstClump8",
        "findLastBit",
        "getValue8",
        "find_first_andnot_bit",
        "_find_first_andnot_bit",
        "find_next_andnot_bit",
        "_find_next_andnot_bit",
    };
    for (helper_symbols) |marker| {
        try expectContains(source, marker);
    }

    const helper_test_anchors = [_][]const u8{
        "find first and next set bits across words, with andnot gaps explicit",
        "single-word next scans honor start masks",
        "single-word first scans clamp to the declared bit window",
        "head-word boundary scans keep the last in-range bit reachable from an inclusive start",
        "tail-word boundary scans keep the last in-range bit reachable from an inclusive start",
        "single-word tail windows keep the last in-range next matches reachable from an inclusive start",
        "tail-word next zero and shared scans skip earlier in-range matches before clamping",
        "clump8 scans mask tail bits beyond nbits",
        "clump8 past-end scans return without reading bitmap words",
        "find last bit ignores storage beyond an exact word boundary",
        "low-level underscore aliases mirror the primary find helpers, including andnot",
        "Linux-style aliases mirror the primary find helpers, including andnot",
    };
    for (helper_test_anchors) |marker| {
        try expectContains(source, marker);
    }

    try expectContainsInOrder(source, &.{
        "\"bits_per_long\"",
        "\"first\"",
        "\"next_after_6\"",
        "\"next_after_word\"",
        "\"first_zero\"",
        "\"next_zero\"",
        "\"first_and\"",
        "\"next_and\"",
        "\"last\"",
    });
}

test "find-bit review checker keeps manifest smoke note and self-test packets visible" {
    const source = try readSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    const packet_markers = [_][]const u8{
        "MANIFEST_EXPECTED",
        "LANE_MARKERS",
        "CLOSURE_MARKERS",
        "SMOKE_MARKERS",
        "tail_word_inclusive_boundary_contract",
        "andnot_scan_entrypoint_contract",
        "review_packet_summary",
        "next_safe_step_note",
        "PHASE1_FIND_BIT_REVIEW_GUARD=python3 scripts/zigux/check-phase1-find-bit-review-packet.py",
        "PHASE1_FIND_BIT_REVIEW_PACKET_SELF_TEST=pass",
        "PHASE1_FIND_BIT_REVIEW_PACKET_SELF_TEST_CASE_COUNT=7",
        "PHASE1_FIND_BIT_REVIEW_PACKET=fail",
        "phase1-find-bit-review-packet:ok",
    };
    for (packet_markers) |marker| {
        try expectContains(source, marker);
    }

    try expectContainsInOrder(source, &.{
        "expect_case(repo, \"missing_helper\"",
        "expect_case(repo, \"missing_symbol\"",
        "expect_case(repo, \"duplicate_anchor\"",
        "expect_case(repo, \"manifest_drift\"",
        "expect_case(repo, \"fixture_drift\"",
        "expect_case(repo, \"manifest_invalid_json\"",
        "expect_case(repo, \"duplicate_fixture_key\"",
        "expect_case(repo, \"missing_smoke\"",
    });
}
