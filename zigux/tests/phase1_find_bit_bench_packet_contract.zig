const std = @import("std");
const options = @import("phase1_find_bit_bench_packet_contract_options");

const checker_text = options.checker_text;

const required_file_markers = [_][]const u8{
    "PHASE1_CLOSURE_REL = Path(\"Documentation/zigux/phase1-closure.md\")",
    "CLOSURE_VALIDATOR_REL = Path(\"scripts\zigux/validate_phase1_closure.zig\")",
    "FIND_BIT_BENCH_ANCHORS_REL = Path(\"scripts\zigux/check_phase1_find_bit_bench_anchors.zig\")",
    "FIND_BIT_HELPER_REL = Path(\"tools/lib/find_bit.zig\")",
    "WORKFLOW_REL = Path(\".github/workflows/zigux-bootstrap.yml\")",
};

const checker_surface_markers = [_][]const u8{
    "REQUIRED_FILES = (",
    "REQUIRED_MARKERS = {",
    "FORBIDDEN_WORKFLOW_LINES = (",
    "def collect_failures(root: Path) -> list[str]:",
    "def build_sample_repo(root: Path) -> None:",
    "def run_self_test() -> int:",
    "PHASE1_FIND_BIT_BENCH_PACKET_SELF_TEST=pass",
    "PHASE1_FIND_BIT_BENCH_PACKET_SELF_TEST_CASE_COUNT=",
    "PHASE1_FIND_BIT_BENCH_PACKET=pass",
    "PHASE1_FIND_BIT_BENCH_PACKET_REQUIRED_FILE_COUNT=",
};

const closure_packet_markers = [_][]const u8{
    "FIND_BIT_REVIEW_CHECKER_REL = Path(\"scripts\zigux/check_phase1_find_bit_review_packet.zig\")",
    "FIND_BIT_BENCH_ANCHOR_CHECKER_REL = Path(\"scripts\zigux/check_phase1_find_bit_bench_anchors.zig\")",
    "\"find_bit_bench_anchor_guard\"",
    "(FIND_BIT_REVIEW_CHECKER_REL, \"phase1-find-bit-review-packet\")",
    "(FIND_BIT_BENCH_ANCHOR_CHECKER_REL, \"phase1-find-bit-bench-anchors\")",
};

const find_bit_anchor_markers = [_][]const u8{
    "head-word boundary scans keep the last in-range bit reachable from an inclusive start",
    "single-word tail windows keep the last in-range next matches reachable from an inclusive start",
    "clump8 past-end scans return without reading bitmap words",
    "findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, boundary)",
    "_find_next_clump8(&clump, &empty, 8, 20)",
};

const workflow_markers = [_][]const u8{
    "Self-test current Phase 1 bench checker",
    "run: zig run scripts/zigux/check_phase1_bench.zig -- --self-test",
    "Self-test current Phase 1 shared reminder checker",
    "Check current Phase 1 shared reminder packet",
    "Self-test current Phase 1 closure validator",
};

const forbidden_workflow_lines = [_][]const u8{
    "run: zig run scripts/zigux/check_phase1_bench.zig",
    "run: zig run scripts/zigux/check_phase1_find_bit_bench_anchors.zig -- --self-test",
    "run: zig run scripts/zigux/check_phase1_find_bit_bench_anchors.zig",
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectExactOccurrences(haystack: []const u8, needle: []const u8, expected_count: usize) !void {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOf(u8, haystack[offset..], needle)) |relative| {
        count += 1;
        offset += relative + needle.len;
    }
    try std.testing.expectEqual(expected_count, count);
}

test "find_bit bench packet checker keeps the live file roster" {
    for (required_file_markers) |marker| {
        try expectContains(checker_text, marker);
    }

    try expectExactOccurrences(checker_text, "REQUIRED_FILES = (", 1);
    try expectContains(checker_text, "PHASE1_CLOSURE_REL,");
    try expectContains(checker_text, "CLOSURE_VALIDATOR_REL,");
    try expectContains(checker_text, "FIND_BIT_BENCH_ANCHORS_REL,");
    try expectContains(checker_text, "FIND_BIT_HELPER_REL,");
    try expectContains(checker_text, "WORKFLOW_REL,");
}

test "find_bit bench packet checker keeps fail-closed validation surfaces" {
    for (checker_surface_markers) |marker| {
        try expectContains(checker_text, marker);
    }

    try expectContains(checker_text, "missing_file:");
    try expectContains(checker_text, "expected_once:actual_count=");
    try expectContains(checker_text, "forbidden_line:actual_count=");
    try expectContains(checker_text, "self-test:{name}:expected_failure");
}

test "find_bit bench packet checker guards closure and helper anchor text" {
    for (closure_packet_markers) |marker| {
        try expectContains(checker_text, marker);
    }
    for (find_bit_anchor_markers) |marker| {
        try expectContains(checker_text, marker);
    }
}

test "find_bit bench packet checker preserves workflow boundary posture" {
    for (workflow_markers) |marker| {
        try expectContains(checker_text, marker);
    }
    for (forbidden_workflow_lines) |marker| {
        try expectContains(checker_text, marker);
    }

    try expectContains(checker_text, "sum(1 for current in workflow_text.splitlines() if current == line)");
}
