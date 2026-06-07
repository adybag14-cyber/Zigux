const std = @import("std");

fn readRepoFile(allocator: std.mem.Allocator, rel_path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, rel_path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "closure note parks find_bit bench anchors as validator-owned guard" {
    const allocator = std.testing.allocator;
    const closure = try readRepoFile(allocator, "Documentation/zigux/phase1-closure.md");
    defer allocator.free(closure);

    try expectContains(
        closure,
        "`PHASE1_FIND_BIT_BENCH_ANCHOR_GUARD=python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py exact-checks inclusive-boundary, past-nbits no-read, clump8 past-end no-read, and findLastBit tail-clamp anchors directly in tools/lib/find_bit.zig`",
    );
    try expectContains(
        closure,
        "`PHASE1_FIND_BIT_REVIEW_GUARD=python3 scripts/zigux/check-phase1-find-bit-review-packet.py exact-checks helper-local find_bit anchors plus the committed tail-clamped and tail-inclusive-boundary replay packet across the helper, closure note, lane note, manifest, and fixture`",
    );
    try expectOrdered(
        closure,
        "`PHASE1_FIND_BIT_BENCH_ANCHOR_GUARD=python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py",
        "`PHASE1_FIND_BIT_REVIEW_GUARD=python3 scripts/zigux/check-phase1-find-bit-review-packet.py",
    );
    try expectContains(
        closure,
        "Current `master` now also keeps Linux-style `find_next_or_bit()` tail-word clamping and past-end alias no-read coverage",
    );
}

test "closure validator requires and names the find_bit bench anchor checker" {
    const allocator = std.testing.allocator;
    const validator = try readRepoFile(allocator, "scripts/zigux/validate-phase1-closure.py");
    defer allocator.free(validator);

    try expectContains(
        validator,
        "FIND_BIT_BENCH_ANCHOR_CHECKER_REL = Path(\"scripts/zigux/check-phase1-find-bit-bench-anchors.py\")",
    );
    try expectOrdered(
        validator,
        "BENCH_CHECKER_REL,",
        "FIND_BIT_BENCH_ANCHOR_CHECKER_REL,",
    );
    try expectOrdered(
        validator,
        "FIND_BIT_BENCH_ANCHOR_CHECKER_REL,",
        "BITMAP_DIRECT_ANCHOR_CHECKER_REL,",
    );
    try expectContains(
        validator,
        "\"find_bit_bench_anchor_guard\": \"`PHASE1_FIND_BIT_BENCH_ANCHOR_GUARD=python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py exact-checks inclusive-boundary, past-nbits no-read, clump8 past-end no-read, and findLastBit tail-clamp anchors directly in tools/lib/find_bit.zig`\"",
    );
    try expectNotContains(validator, "PHASE1_FIND_BIT_BENCH_ANCHOR_GUARD=missing_current_master");
}

test "bench anchor checker stays fail-closed over direct find_bit markers" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, "scripts/zigux/check-phase1-find-bit-bench-anchors.py");
    defer allocator.free(checker);

    try expectContains(checker, "REQUIRED_TEST_MARKERS = {");
    try expectContains(checker, "REQUIRED_SOURCE_COUNT_MARKERS = {");
    try expectContains(checker, "REQUIRED_SOURCE_EXACT_MARKERS = {");
    try expectContains(checker, "\"boundary_head_test\": 'test \"head-word boundary scans keep the last in-range bit reachable from an inclusive start\" {'");
    try expectContains(checker, "\"past_end_no_read_test\": 'test \"next scans past nbits return without reading bitmap words\" {'");
    try expectContains(checker, "\"clump8_no_read_test\": 'test \"clump8 past-end scans return without reading bitmap words\" {'");
    try expectContains(checker, "\"last_bit_tail_test\": 'test \"find last bit clamps tail words to nbits\" {'");
    try expectContains(checker, "return (\"invalid_test_marker_counts\", test_failures)");
    try expectContains(checker, "return (\"invalid_source_count_markers\", source_count_failures)");
    try expectContains(checker, "return (\"invalid_source_marker_counts\", source_exact_failures)");
    try expectContains(checker, "PHASE1_FIND_BIT_BENCH_ANCHORS_SELF_TEST=pass");
    try expectContains(checker, "PHASE1_FIND_BIT_BENCH_ANCHORS=pass");
}

test "find_bit helper carries the direct source anchors the closure checker guards" {
    const allocator = std.testing.allocator;
    const find_bit = try readRepoFile(allocator, "tools/lib/find_bit.zig");
    defer allocator.free(find_bit);

    try expectContains(find_bit, "test \"head-word boundary scans keep the last in-range bit reachable from an inclusive start\" {");
    try expectContains(find_bit, "test \"tail-word boundary scans keep the last in-range bit reachable from an inclusive start\" {");
    try expectContains(find_bit, "test \"next scans past nbits return without reading bitmap words\" {");
    try expectContains(find_bit, "test \"clump8 past-end scans return without reading bitmap words\" {");
    try expectContains(find_bit, "test \"find last bit clamps tail words to nbits\" {");
    try expectContains(find_bit, "findNextAndNotBit(&tail_andnot_lhs, &tail_andnot_rhs, nbits, bits_per_long + 2)");
    try expectContains(find_bit, "find_next_clump8(&clump, &empty, 8, 12)");
    try expectContains(find_bit, "try std.testing.expectEqual(@as(usize, 4), findLastBit(&single_word, single_word_nbits));");
}
