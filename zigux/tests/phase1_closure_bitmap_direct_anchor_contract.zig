const std = @import("std");

const repo_files = .{
    .closure = "Documentation/zigux/phase1-closure.md",
    .lane_note = "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
    .checker = "scripts/zigux/check-phase1-bitmap-direct-anchors.py",
    .manifest = "zigux/tests/fixtures/phase1_helper_manifest.json",
};

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, allocator, .limited(512 * 1024));
}

fn expectContains(text: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, text, needle) != null);
}

fn expectBefore(text: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, text, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, text, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "phase1 closure keeps bitmap direct anchor authority parked and review-visible" {
    const allocator = std.testing.allocator;
    const closure = try readFile(allocator, repo_files.closure);
    defer allocator.free(closure);
    const lane_note = try readFile(allocator, repo_files.lane_note);
    defer allocator.free(lane_note);

    const closure_markers = [_][]const u8{
        "`PHASE1_BITMAP_DIRECT_REVIEW=helper-local bitmap direct anchors stay explicit through the closure packet",
        "`PHASE1_BITMAP_PARTIAL_XOR_REVIEW=partial_xor_nbits and partial_xor_masked_values stay owned by the shared Phase 1 parity fixture",
        "`PHASE1_BITMAP_UNIT_REVIEW=bitmap multiword-tail xorBits behavior still lets callers clamp the last word",
        "`PHASE1_BITMAP_EMPTY_UNIT_REVIEW=bitmap_scnprintf leaves a non-empty caller buffer untouched when no bits are set",
        "`PHASE1_BITMAP_FINAL_PARTIAL_WORD_REVIEW=helper-local bitmap final partial-word proof stays explicit through the direct bitmap test anchor",
        "`PHASE1_BITMAP_COMPLEMENT_TAIL_REVIEW=helper-local complement-tail masking stays explicit through the direct bitmap tests",
        "`PHASE1_BITMAP_LINUX_ALIAS_REVIEW=helper-local bitmap Linux-style alias proof stays explicit through the direct bitmap test anchor",
        "`PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
        "`PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker",
    };
    inline for (closure_markers) |marker| {
        try expectContains(closure, marker);
    }

    try expectBefore(
        closure,
        "For `tools/lib/bitmap.zig`, current `master` still justifies a parked helper-local follow-up rather than a reopened closure pass.",
        "`PHASE1_BITMAP_DIRECT_REVIEW=helper-local bitmap direct anchors stay explicit through the closure packet",
    );

    const lane_markers = [_][]const u8{
        "`PHASE1_BITMAP_DIRECT_OWNER=bitmap helper-local anchors plus the committed bitmap replay keys it already owns",
        "`PHASE1_BITMAP_NEXT_SAFE_STEP=bitmap stays parked unless a fresh reread finds new direct-anchor drift or committed shared replay drift",
        "The live helper-local bitmap packet already keeps caller-window and multiword-tail `xorBits()` and `orBits()` clamp proofs review-visible",
        "That direct bitmap packet now explicitly includes the caller-window and multiword-tail `xorBits()` and `orBits()` clamp witnesses",
    };
    inline for (lane_markers) |marker| {
        try expectContains(lane_note, marker);
    }
}

test "bitmap direct-anchor checker keeps the helper-local marker packet exact" {
    const allocator = std.testing.allocator;
    const checker = try readFile(allocator, repo_files.checker);
    defer allocator.free(checker);

    const checker_markers = [_][]const u8{
        "\"range_edges\": 'test \"bitmap range helpers preserve edges across whole-word spans\" {'",
        "\"copy_raw_alias\": 'test \"bitmap copy alias preserves raw source words without tail clearing\" {'",
        "\"xor_window\": 'test \"bitmap xor keeps caller-selected bit window\" {'",
        "\"xor_multiword_tail\": 'test \"bitmap xor across a multiword tail still lets callers clamp the last word\" {'",
        "\"or_window\": 'test \"bitmap or keeps caller-selected bit window\" {'",
        "\"or_multiword_tail\": 'test \"bitmap or across a multiword tail still lets callers clamp the last word\" {'",
        "\"weighted_or_xor_tail\": 'test \"bitmap weighted or and xor clamp counts to the declared tail window\" {'",
        "\"weighted_and_andnot_tail\": 'test \"bitmap weighted and andnot clamp counts to the declared tail window\" {'",
        "\"complement_tail\": 'test \"bitmap complement clamps partial tails and leaves zero-sized caller views untouched\" {'",
        "\"linux_alias_copy_logic\": 'test \"bitmap Linux-style aliases mirror copy logical range and format helpers\" {'",
        "\"bitmap_weighted_or_alias\": \"pub fn bitmap_weighted_or(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) usize {\"",
        "\"bitmap_weighted_xor_alias\": \"pub fn bitmap_weighted_xor(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) usize {\"",
        "PHASE1_BITMAP_DIRECT_ANCHORS_SELF_TEST=pass",
        "PHASE1_BITMAP_DIRECT_ANCHORS=pass",
        "PHASE1_BITMAP_DIRECT_ANCHORS_HELPER=",
    };
    inline for (checker_markers) |marker| {
        try expectContains(checker, marker);
    }

    try expectBefore(
        checker,
        "REQUIRED_TEST_MARKERS = {",
        "REQUIRED_SOURCE_MARKERS = {",
    );
    try expectBefore(
        checker,
        "\"xor_window\"",
        "\"bitmap_xor_alias\"",
    );
}

test "manifest bitmap packet names the same next safe direct-anchor boundary" {
    const allocator = std.testing.allocator;
    const manifest = try readFile(allocator, repo_files.manifest);
    defer allocator.free(manifest);

    const manifest_markers = [_][]const u8{
        "\"tools/lib/bitmap.zig\": {",
        "\"helper_test_anchors\": [",
        "\"test \\\"bitmap xor keeps caller-selected bit window\\\"\"",
        "\"test \\\"bitmap xor across a multiword tail still lets callers clamp the last word\\\"\"",
        "\"test \\\"bitmap or keeps caller-selected bit window\\\"\"",
        "\"test \\\"bitmap or across a multiword tail still lets callers clamp the last word\\\"\"",
        "\"test \\\"bitmap weighted or and xor clamp counts to the declared tail window\\\"\"",
        "\"test \\\"bitmap weighted and andnot clamp counts to the declared tail window\\\"\"",
        "\"complement_tail_review_summary\": \"helper-local complement-tail masking stays explicit through the direct bitmap tests",
        "\"linux_alias_anchor\": \"test \\\"bitmap Linux-style aliases mirror copy logical range and format helpers\\\"\"",
        "\"partial_xor_review_fields\": [",
        "\"partial_xor_nbits\"",
        "\"partial_xor_masked_values\"",
        "\"next_safe_step_note\": \"If this helper lane reopens, keep bitmap parked unless a fresh reread finds new direct-anchor drift",
    };
    inline for (manifest_markers) |marker| {
        try expectContains(manifest, marker);
    }

    try expectBefore(
        manifest,
        "\"tools/lib/bitmap.zig\": {",
        "\"tools/lib/find_bit.zig\": {",
    );
}
