const std = @import("std");

const checker_path = "scripts/zigux/check-phase1-find-bit-review-packet.py";

fn readCheckerSource() ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        checker_path,
        std.testing.allocator,
        .limited(128 * 1024),
    );
}

fn requireContains(source: []const u8, marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, source, marker) != null);
}

fn requireCount(source: []const u8, marker: []const u8, expected: usize) !void {
    try std.testing.expectEqual(expected, std.mem.count(u8, source, marker));
}

fn requireOrdered(source: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, source, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, source, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "find_bit review checker keeps its live packet path roster" {
    const source = try readCheckerSource();
    defer std.testing.allocator.free(source);

    try requireContains(source, "\"\"\"Guard the Phase 1 find_bit review packet against helper, fixture, and note drift.\"\"\"");
    try requireContains(source, "HELPER_REL = Path(\"tools/lib/find_bit.zig\")");
    try requireContains(source, "LANE_NOTE_REL = Path(\"Documentation/zigux/phase1-host-helper-lane-sequencing.md\")");
    try requireContains(source, "CLOSURE_NOTE_REL = Path(\"Documentation/zigux/phase1-closure.md\")");
    try requireContains(source, "MANIFEST_REL = Path(\"zigux/tests/fixtures/phase1_helper_manifest.json\")");
    try requireContains(source, "FIXTURE_REL = Path(\"zigux/tests/fixtures/phase1_helpers.json\")");
    try requireContains(source, "SMOKE_REL = Path(\"zigux/tests/phase1_host_tools_smoke.zig\")");
    try requireContains(source, "FIND_BIT_REL = \"tools/lib/find_bit.zig\"");
}

test "find_bit review checker keeps helper symbol and anchor families explicit" {
    const source = try readCheckerSource();
    defer std.testing.allocator.free(source);

    try requireContains(source, "SOURCE_SYMBOLS = [");
    try requireContains(source, "\"findFirstAndNotBit\"");
    try requireContains(source, "\"find_next_andnot_bit\"");
    try requireContains(source, "\"_find_next_clump8\"");
    try requireContains(source, "\"_find_last_bit\"");
    try requireContains(source, "HELPER_TEST_ANCHORS = [");
    try requireContains(source, "test \"find first and next set bits across words, with andnot gaps explicit\"");
    try requireContains(source, "test \"clump8 past-end scans return without reading bitmap words\"");
    try requireContains(source, "test \"single-word tail windows keep the last in-range next matches reachable from an inclusive start\"");
    try requireContains(source, "test \"Linux-style aliases mirror the primary find helpers, including andnot\"");
    try requireContains(source, "PARITY_FIXTURE_KEYS = [");
    try requireContains(source, "\"bits_per_long\", \"first\", \"next_after_6\", \"next_after_word\", \"first_zero\"");
    try requireContains(source, "FIXTURE_VALUES = {");
    try requireContains(source, "\"last\": 71");
}

test "find_bit review checker guards manifest fixture and smoke drift" {
    const source = try readCheckerSource();
    defer std.testing.allocator.free(source);

    try requireContains(source, "MANIFEST_EXPECTED = {");
    try requireContains(source, "\"andnot_scan_entrypoints\": [\"findFirstAndNotBit\", \"find_first_andnot_bit\", \"_find_first_andnot_bit\", \"findNextAndNotBit\", \"find_next_andnot_bit\", \"_find_next_andnot_bit\"]");
    try requireContains(source, "\"tail_word_inclusive_boundary_contract\": \"Direct Zig unit coverage keeps tail-clamped set, zero, and shared-bit scans aligned when the inclusive start lands on the last in-range bit of the final partial word, while later starts still return nbits instead of leaking the out-of-range tail.\"");
    try requireContains(source, "\"next_safe_step_note\": \"If this helper lane reopens, keep find_bit parked unless a fresh reread finds drift");
    try requireContains(source, "LANE_MARKERS = [");
    try requireContains(source, "PHASE1_FIND_BIT_NEXT_SAFE_STEP=find_bit reopens only for direct-anchor drift inside same-word start-mask");
    try requireContains(source, "CLOSURE_MARKERS = [");
    try requireContains(source, "PHASE1_FIND_BIT_REVIEW_GUARD=python3 scripts/zigux/check-phase1-find-bit-review-packet.py");
    try requireContains(source, "SMOKE_MARKERS = [");
    try requireContains(source, "find_bit.findFirstAndNotBit(&tail_lhs, &tail_rhs, nbits)");
    try requireContains(source, "find_bit._find_next_clump8(&clump, &clump_map, nbits, nbits)");
}

test "find_bit review checker keeps fail-closed validation and public outputs" {
    const source = try readCheckerSource();
    defer std.testing.allocator.free(source);

    try requireContains(source, "class DuplicateTrackingDict(dict[str, object]):");
    try requireContains(source, "self.duplicate_keys: list[str] = []");
    try requireContains(source, "def duplicate_paths(data: object, prefix: tuple[str, ...] = ()) -> list[str]:");
    try requireContains(source, "failures.extend(f\"manifest:duplicate_json_key:{path}\" for path in duplicate_paths(manifest))");
    try requireContains(source, "failures.extend(f\"fixture:duplicate_json_key:{path}\" for path in duplicate_paths(fixture))");
    try requireContains(source, "def collect_failures(repo: Path) -> list[str]:");
    try requireContains(source, "for symbol in SOURCE_SYMBOLS:");
    try requireContains(source, "for marker in HELPER_TEST_ANCHORS:");
    try requireOrdered(source, "for marker in LANE_MARKERS:", "for marker in CLOSURE_MARKERS:");
    try requireOrdered(source, "for marker in CLOSURE_MARKERS:", "for marker in SMOKE_MARKERS:");
    try requireContains(source, "def run_self_test() -> int:");
    try requireContains(source, "PHASE1_FIND_BIT_REVIEW_PACKET_SELF_TEST=pass");
    try requireContains(source, "PHASE1_FIND_BIT_REVIEW_PACKET_SELF_TEST_CASE_COUNT=7");
    try requireContains(source, "PHASE1_FIND_BIT_REVIEW_PACKET=fail");
    try requireContains(source, "phase1-find-bit-review-packet:ok");
    try requireContains(source, "PHASE1_FIND_BIT_REVIEW_PACKET_HELPER=");
    try requireContains(source, "PHASE1_FIND_BIT_REVIEW_PACKET_MANIFEST=");
    try requireCount(source, "collect_failures(repo)", 2);
}
