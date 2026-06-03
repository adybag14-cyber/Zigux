const std = @import("std");

const checker_path = "scripts/zigux/check-phase1-find-bit-bench-anchors.py";
const workflow_path = ".github/workflows/zigux-bootstrap.yml";
const closure_validator_path = "scripts/zigux/validate-phase1-closure.py";

const checker_markers = [_][]const u8{
    "FIND_BIT_REL = Path(\"tools/lib/find_bit.zig\")",
    "REQUIRED_TEST_MARKERS = {",
    "\"boundary_head_test\": 'test \"head-word boundary scans keep the last in-range bit reachable from an inclusive start\" {'",
    "\"boundary_tail_test\": 'test \"tail-word boundary scans keep the last in-range bit reachable from an inclusive start\" {'",
    "\"past_end_no_read_test\": 'test \"next scans past nbits return without reading bitmap words\" {'",
    "\"clump8_no_read_test\": 'test \"clump8 past-end scans return without reading bitmap words\" {'",
    "\"last_bit_tail_test\": 'test \"find last bit clamps tail words to nbits\" {'",
    "REQUIRED_SOURCE_COUNT_MARKERS = {",
    "\"find_next_boundary\": (\"findNextBit(&set_map, nbits, boundary)\", 4)",
    "\"find_next_andnot_boundary\": (\"findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, boundary)\", 4)",
    "\"find_first_clump8_tail_value\": ('try std.testing.expectEqual(@as(u8, 0b0000_1000), clump);', 4)",
    "REQUIRED_SOURCE_EXACT_MARKERS = {",
    "\"find_next_andnot_tail_skip\": \"try std.testing.expectEqual(@as(usize, bits_per_long + 4), findNextAndNotBit(&tail_andnot_lhs, &tail_andnot_rhs, nbits, bits_per_long + 2));\"",
    "\"find_clump8_past_end\": \"findNextClump8(&clump, &empty, 8, 8)\"",
    "\"find_get_value8_last_aligned\": \"try std.testing.expectEqual(@as(u8, 0xa5), getValue8(&bitmap, last_aligned_byte));\"",
    "\"find_next_andnot_linux_alias\": \"try std.testing.expectEqual(findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, bits_per_long), find_next_andnot_bit(&andnot_lhs, &andnot_rhs, nbits, bits_per_long));\"",
    "PHASE1_FIND_BIT_BENCH_ANCHORS_SELF_TEST=pass",
    "PHASE1_FIND_BIT_BENCH_ANCHORS_SELF_TEST_CASE_COUNT",
    "PHASE1_FIND_BIT_BENCH_ANCHORS=pass",
    "PHASE1_FIND_BIT_BENCH_ANCHORS_REASON",
};

const workflow_markers = [_][]const u8{
    "Self-test current Phase 1 find-bit bench anchor checker",
    "run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test\n",
    "Check current Phase 1 find-bit bench anchor packet",
    "run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py\n",
};

const closure_markers = [_][]const u8{
    "FIND_BIT_BENCH_ANCHOR_CHECKER_REL = Path(\"scripts/zigux/check-phase1-find-bit-bench-anchors.py\")",
    "\"find_bit_bench_anchor_guard\": \"`PHASE1_FIND_BIT_BENCH_ANCHOR_GUARD=python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py exact-checks inclusive-boundary, past-nbits no-read, clump8 past-end no-read, and findLastBit tail-clamp anchors directly in tools/lib/find_bit.zig`\"",
    "FIND_BIT_BENCH_ANCHOR_CHECKER_REL,",
    "(\"missing_find_bit_bench_anchor_checker\", lambda root: (root / FIND_BIT_BENCH_ANCHOR_CHECKER_REL).unlink())",
    "(\"failing_find_bit_bench_anchor_checker\", lambda root: make_checker_stub(root / FIND_BIT_BENCH_ANCHOR_CHECKER_REL, ok=False))",
};

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var start: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, start, needle)) |index| {
        count += 1;
        start = index + needle.len;
    }
    return count;
}

fn expectExactlyOnce(text: []const u8, markers: []const []const u8) !void {
    for (markers) |marker| {
        try std.testing.expectEqual(@as(usize, 1), countOccurrences(text, marker));
    }
}

fn expectPresent(text: []const u8, markers: []const []const u8) !void {
    for (markers) |marker| {
        try std.testing.expect(countOccurrences(text, marker) >= 1);
    }
}

fn expectOrderedWorkflow(text: []const u8) !void {
    var previous: usize = 0;
    for (workflow_markers) |marker| {
        const index = std.mem.indexOfPos(u8, text, previous, marker) orelse return error.MissingWorkflowMarker;
        try std.testing.expectEqual(@as(usize, 1), countOccurrences(text, marker));
        previous = index + marker.len;
    }
}

fn currentCheckerSample() []const u8 {
    return
    \\FIND_BIT_REL = Path("tools/lib/find_bit.zig")
    \\REQUIRED_TEST_MARKERS = {
    \\\"boundary_head_test": 'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start" {'
    \\\"boundary_tail_test": 'test "tail-word boundary scans keep the last in-range bit reachable from an inclusive start" {'
    \\\"past_end_no_read_test": 'test "next scans past nbits return without reading bitmap words" {'
    \\\"clump8_no_read_test": 'test "clump8 past-end scans return without reading bitmap words" {'
    \\\"last_bit_tail_test": 'test "find last bit clamps tail words to nbits" {'
    \\REQUIRED_SOURCE_COUNT_MARKERS = {
    \\\"find_next_boundary": ("findNextBit(&set_map, nbits, boundary)", 4)
    \\\"find_next_andnot_boundary": ("findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, boundary)", 4)
    \\\"find_first_clump8_tail_value": ('try std.testing.expectEqual(@as(u8, 0b0000_1000), clump);', 4)
    \\REQUIRED_SOURCE_EXACT_MARKERS = {
    \\\"find_next_andnot_tail_skip": "try std.testing.expectEqual(@as(usize, bits_per_long + 4), findNextAndNotBit(&tail_andnot_lhs, &tail_andnot_rhs, nbits, bits_per_long + 2));"
    \\\"find_clump8_past_end": "findNextClump8(&clump, &empty, 8, 8)"
    \\\"find_get_value8_last_aligned": "try std.testing.expectEqual(@as(u8, 0xa5), getValue8(&bitmap, last_aligned_byte));"
    \\\"find_next_andnot_linux_alias": "try std.testing.expectEqual(findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, bits_per_long), find_next_andnot_bit(&andnot_lhs, &andnot_rhs, nbits, bits_per_long));"
    \\PHASE1_FIND_BIT_BENCH_ANCHORS_SELF_TEST=pass
    \\PHASE1_FIND_BIT_BENCH_ANCHORS_SELF_TEST_CASE_COUNT
    \\PHASE1_FIND_BIT_BENCH_ANCHORS=pass
    \\PHASE1_FIND_BIT_BENCH_ANCHORS_REASON
    \\
    ;
}

fn currentWorkflowSample() []const u8 {
    return
    \\      - name: Self-test current Phase 1 find-bit bench anchor checker
    \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test
    \\
    \\      - name: Check current Phase 1 find-bit bench anchor packet
    \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py
    \\
    ;
}

fn currentClosureSample() []const u8 {
    return
    \\FIND_BIT_BENCH_ANCHOR_CHECKER_REL = Path("scripts/zigux/check-phase1-find-bit-bench-anchors.py")
    \\\"find_bit_bench_anchor_guard": "`PHASE1_FIND_BIT_BENCH_ANCHOR_GUARD=python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py exact-checks inclusive-boundary, past-nbits no-read, clump8 past-end no-read, and findLastBit tail-clamp anchors directly in tools/lib/find_bit.zig`"
    \\FIND_BIT_BENCH_ANCHOR_CHECKER_REL,
    \\("missing_find_bit_bench_anchor_checker", lambda root: (root / FIND_BIT_BENCH_ANCHOR_CHECKER_REL).unlink())
    \\("failing_find_bit_bench_anchor_checker", lambda root: make_checker_stub(root / FIND_BIT_BENCH_ANCHOR_CHECKER_REL, ok=False))
    \\
    ;
}

fn readFileFromCwd(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        std.testing.allocator,
        .limited(limit),
    );
}

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    return readFileFromCwd(path, limit) catch |err| switch (err) {
        error.FileNotFound => {
            const fallback = try std.mem.concat(std.testing.allocator, u8, &.{ "../../", path });
            defer std.testing.allocator.free(fallback);
            return readFileFromCwd(fallback, limit);
        },
        else => return err,
    };
}

test "find-bit bench anchor checker contract pins current checker marker packet" {
    try expectExactlyOnce(currentCheckerSample(), &checker_markers);

    const duplicate = try std.mem.concat(std.testing.allocator, u8, &.{
        currentCheckerSample(),
        checker_markers[2],
    });
    defer std.testing.allocator.free(duplicate);
    try std.testing.expectEqual(@as(usize, 2), countOccurrences(duplicate, checker_markers[2]));

    const missing = try std.mem.replaceOwned(u8, std.testing.allocator, currentCheckerSample(), checker_markers[11], "REQUIRED_SOURCE_EXACT_MARKERS_DRIFT = {");
    defer std.testing.allocator.free(missing);
    try std.testing.expectEqual(@as(usize, 0), countOccurrences(missing, checker_markers[11]));
}

test "find-bit bench anchor workflow pair remains ordered and exact" {
    try expectOrderedWorkflow(currentWorkflowSample());

    const reordered =
        \\      - name: Check current Phase 1 find-bit bench anchor packet
        \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py
        \\
        \\      - name: Self-test current Phase 1 find-bit bench anchor checker
        \\        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test
        \\
    ;
    try std.testing.expectError(error.MissingWorkflowMarker, expectOrderedWorkflow(reordered));
}

test "closure validator keeps find-bit bench checker delegated" {
    try expectPresent(currentClosureSample(), &closure_markers);

    const missing = try std.mem.replaceOwned(u8, std.testing.allocator, currentClosureSample(), closure_markers[1], "find_bit_bench_anchor_guard: drifted");
    defer std.testing.allocator.free(missing);
    try std.testing.expectEqual(@as(usize, 0), countOccurrences(missing, closure_markers[1]));
}

test "repository files carry the current find-bit bench checker packet" {
    const checker = try readRepoFile(checker_path, 96 * 1024);
    defer std.testing.allocator.free(checker);
    try expectExactlyOnce(checker, &checker_markers);

    const workflow = try readRepoFile(workflow_path, 128 * 1024);
    defer std.testing.allocator.free(workflow);
    try expectOrderedWorkflow(workflow);

    const closure = try readRepoFile(closure_validator_path, 256 * 1024);
    defer std.testing.allocator.free(closure);
    try expectPresent(closure, &closure_markers);
}
