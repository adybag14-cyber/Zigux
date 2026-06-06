const std = @import("std");

const checker_path = "scripts/zigux/check-phase1-direct-anchor-manifest-gate.py";

const required_markers = [_][]const u8{
    "MANIFEST_REL = Path(\"zigux/tests/fixtures/phase1_helper_manifest.json\")",
    "BITMAP_DIRECT_ANCHOR_CHECKER_REL = Path(\"scripts/zigux/check-phase1-bitmap-direct-anchors.py\")",
    "FIND_BIT_REVIEW_CHECKER_REL = Path(\"scripts/zigux/check-phase1-find-bit-review-packet.py\")",
    "RBTREE_DIRECT_ANCHOR_CHECKER_REL = Path(\"scripts/zigux/check-phase1-rbtree-direct-anchors.py\")",
    "RBTREE_REVIEW_CHECKER_REL = Path(\"scripts/zigux/check-phase1-rbtree-review-packet.py\")",
    "STRING_REVIEW_CHECKER_REL = Path(\"scripts/zigux/check-phase1-string-review-packet.py\")",
    "EXPECTED_SHARED_REPLAY_PARKED_HELPERS = [",
    "EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [",
    "\"tools/lib/bitmap.zig\",",
    "\"tools/lib/find_bit.zig\",",
    "\"tools/lib/rbtree.zig\",",
    "\"tools/lib/string.zig\",",
    "EXPECTED_RULE_SUMMARY = (",
    "EXPECTED_ANTI_OVERLAP_RULE = (",
    "EXPECTED_REVIEW_FIELDS = {",
    "\"copy_raw_alias_anchor\"",
    "\"andnot_scan_entrypoints\"",
    "\"cached_root_followup_anchors\"",
    "\"strcmp_review_anchors\"",
    "DELEGATED_CHECKERS = (",
    "\"bitmap_direct_anchor_checker\"",
    "\"find_bit_review_checker\"",
    "\"rbtree_direct_anchor_checker\"",
    "\"rbtree_review_checker\"",
    "\"string_review_checker\"",
    "def collect_duplicate_json_key_paths(data: object, prefix: tuple[str, ...] = ()) -> list[str]:",
    "def collect_issues(manifest: dict) -> list[str]:",
    "def run_checker(root: Path, script_rel: Path, label: str, success_stdout: str) -> list[str]:",
    "def run_self_test() -> None:",
    "\"PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_SELF_TEST=pass\"",
    "\"PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=pass\"",
    "\"PHASE1_DIRECT_ANCHOR_DELEGATED_CHECKER_COUNT=\"",
};

const ordered_markers = [_][]const u8{
    "EXPECTED_HELPERS = [",
    "EXPECTED_SHARED_REPLAY_PARKED_HELPERS = [",
    "EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [",
    "EXPECTED_RULE_SUMMARY = (",
    "EXPECTED_ANTI_OVERLAP_RULE = (",
    "EXPECTED_REVIEW_FIELDS = {",
    "DELEGATED_CHECKERS = (",
    "def collect_issues(manifest: dict) -> list[str]:",
    "def run_checker(root: Path, script_rel: Path, label: str, success_stdout: str) -> list[str]:",
    "def run_self_test() -> None:",
    "def main() -> int:",
};

const delegated_status_lines = [_][]const u8{
    "\"PHASE1_BITMAP_DIRECT_ANCHOR_CHECKER=pass\"",
    "\"PHASE1_FIND_BIT_REVIEW_CHECKER=pass\"",
    "\"PHASE1_RBTREE_DIRECT_ANCHOR_CHECKER=pass\"",
    "\"PHASE1_RBTREE_REVIEW_CHECKER=pass\"",
    "\"PHASE1_STRING_REVIEW_CHECKER=pass\"",
};

fn readFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(512 * 1024),
    );
}

fn countNeedle(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, index, needle)) |found| {
        count += 1;
        index = found + needle.len;
    }
    return count;
}

fn expectExactlyOnce(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countNeedle(haystack, needle));
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "direct-anchor manifest gate checker keeps current marker roster" {
    const source = try readFile(checker_path);
    defer std.testing.allocator.free(source);

    for (required_markers) |marker| {
        try expectExactlyOnce(source, marker);
    }
}

test "direct-anchor manifest gate checker keeps delegated status outputs" {
    const source = try readFile(checker_path);
    defer std.testing.allocator.free(source);

    for (delegated_status_lines) |marker| {
        try expectExactlyOnce(source, marker);
    }

    try expectExactlyOnce(source, "\"PHASE1_DIRECT_ANCHOR_HELPER_COUNT=\"");
    try expectExactlyOnce(source, "\"PHASE1_DIRECT_ANCHOR_REVIEW_FIELD_COUNT=\"");
}

test "direct-anchor manifest gate source keeps validation flow ordered" {
    const source = try readFile(checker_path);
    defer std.testing.allocator.free(source);

    for (ordered_markers[0 .. ordered_markers.len - 1], ordered_markers[1..]) |before, after| {
        try expectOrdered(source, before, after);
    }
}
