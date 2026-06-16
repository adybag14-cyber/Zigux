const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE6_BSEARCH_CORPUS_EVIDENCE=pass";
pub const self_test_pass_marker = "PHASE6_BSEARCH_CORPUS_EVIDENCE_SELF_TEST=pass";

const PERF_BUDGET_FORMULA = [_][]const u8{
    "\"std.math.log2_int_ceil(len) + 1\"",
};

const BOUND_BUDGET_FORMULA = [_][]const u8{
    "\"len == 0 ? 0 : std.math.log2_int_floor(len) + 1\"",
};

const SLICE_SUMMARY = [_][]const u8{
    "- direct helper-local evidence now covers typed and raw representative lookups, descending-order comparator handling, duplicate-span `equalRange` wrappers, `IndexRange` typed and byte-view companions, mutable write-through aliases, typed and raw C ABI lower-bound and upper-bound insertion-point parity, runtime-selected typed and raw C ABI comparator pointers under logarithmic comparison budgets, a representative external C-vs-Zig parity replay covering 17 sorted lookup cases across ascending and descending comparator-driven lookups, duplicate hits, heterogeneous string-key lookup, and mutable write-through behavior, and a fixture-backed dedicated perf replay that reports lookup cost plus average and worst-case comparator work across representative lengths",
};

const C_PARITY_COMPANIONS = [_][]const u8{
    "- direct C parity companions: `zigux/tests/phase6_bsearch_c_parity.zig`, `zigux/tests/fixtures/phase6_bsearch_c_harness.c`, and `scripts\\zigux/check_phase6_bsearch_c_parity.zig`",
};

const HELPER_EVIDENCE_FOCUSED_C_ABI_REPLAYS = [_][]const u8{
    "- focused C ABI replays: `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig` and `zigux/tests/phase6_bsearch_c_abi_budget.zig`",
};

const HELPER_EVIDENCE_C_PARITY_POSTURE = [_][]const u8{
    "the direct C parity spot check now keeps 17 sorted lookup cases explicit across ascending and descending comparator-driven lookups, duplicate hits, heterogeneous string-key lookup, and mutable write-through behavior",
};

const HELPER_POSTURE = [_][]const u8{
    "- current posture: direct helper readback is restored across the helper, focused replay, perf replay, C ABI review routes, direct C parity runner, direct C parity harness, fixture surface, dedicated corpus checker, direct C parity checker, and slice note",
};

const PARITY_HELPER_EVIDENCE_ROW = [_][]const u8{
    "- helper-evidence row: `zigux/tests/phase6_bsearch_perf.zig`, `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`, `zigux/tests/phase6_bsearch_c_abi_budget.zig`, `zigux/tests/phase6_bsearch_c_parity.zig`, `zigux/tests/fixtures/phase6_bsearch_c_harness.c`, `zigux/tests/fixtures/phase6_bsearch_vectors.zig`, `scripts\\zigux/check_phase6_bsearch_corpus_evidence.zig`, `scripts\\zigux/check_phase6_bsearch_c_parity.zig`, `Documentation/zigux/phase6-bsearch-slice.md`, `Documentation/zigux/phase6-helper-evidence-catalog.md`, `zigux/tests/phase6_helper_evidence_manifest.json`, and `zigux/tests/phase6_helper_parity_manifest.json`",
};

const MANIFEST_POSTURE = [_][]const u8{
    "\"current_review_posture\": \"direct-helper-readback-restored\"",
};

const NO_MISSING_COMPANIONS = [_][]const u8{
    "\"still_missing_direct_companions\": []",
};

const LIB_INDEX_RANGE_TEST = [_][]const u8{
    "test \"index range views keep typed and byte aliases aligned for hits and insertion sites\" {",
};

const LIB_FIRST_CONST = [_][]const u8{
    "const first_const = duplicate_range.firstConst(i32, duplicates[0..]) orelse return error.TestUnexpectedResult;",
};

const LIB_LAST_CONST = [_][]const u8{
    "const last_const = duplicate_range.lastConst(i32, duplicates[0..]) orelse return error.TestUnexpectedResult;",
};

const LIB_MUTABLE_BYTE_VIEW = [_][]const u8{
    "const mutable_byte_view = duplicate_range.bytesMutable(@ptrCast(mutable_raw_duplicates[0..].ptr), @sizeOf(i32));",
};

const PERF_BUDGET_LINE = [_][]const u8{
    "const max_compare_budget = std.math.log2_int_ceil(usize, case.len) + 1;",
};

const BOUND_BUDGET_HELPER = [_][]const u8{
    "fn maxBinarySearchComparisons(len: usize) usize {",
};

const BOUND_BUDGET_SHIFT = [_][]const u8{
    "while (remaining > 0) : (remaining >>= 1) {",
};

const SELF_TEST_CASES = [_][]const u8{
    "(SLICE_PATH",
    "- `IndexRange.firstConst`",
    "- `IndexRange.firstHead`)",
    "(SLICE_PATH",
    "- `IndexRange.bytesMutable`",
    "- `IndexRange.rawBytesMutable`)",
    "(SLICE_PATH",
    "SLICE_SUMMARY",
    "- direct helper-local evidence now covers typed and raw representative lookups, descending-order comparator handling, duplicate-span `equalRange` wrappers, mutable write-through aliases, raw C ABI lower-bound and upper-bound insertion-point parity, runtime-selected raw C ABI comparator pointers under logarithmic comparison budgets, and a fixture-backed dedicated perf replay that reports lookup cost plus average and worst-case comparator work across representative lengths",
    ")",
    "(SLICE_PATH",
    "- `zigux/tests/phase6_bsearch_c_parity.zig`",
    "- `zigux/tests/phase6_bsearch_c_parity_casegen.zig`)",
    "(SLICE_PATH",
    "zig run scripts\\zigux/check_phase6_bsearch_c_parity.zig",
    "zig run scripts\\zigux/check_phase6_bsearch_corpus_evidence.zig)",
    "(LIB_PATH",
    "LIB_INDEX_RANGE_TEST",
    "test \"equal-range index views keep typed and byte aliases aligned for hits and insertion sites\" {)",
    "(LIB_PATH",
    "LIB_FIRST_CONST",
    "const first_const = duplicate_range.firstHead(i32, duplicates[0..]) orelse return error.TestUnexpectedResult;)",
    "(LIB_PATH",
    "LIB_LAST_CONST",
    "const last_const = duplicate_range.lastHead(i32, duplicates[0..]) orelse return error.TestUnexpectedResult;)",
    "(LIB_PATH",
    "LIB_MUTABLE_BYTE_VIEW",
    "const mutable_byte_view = duplicate_range.rawBytesMutable(@ptrCast(mutable_raw_duplicates[0..].ptr), @sizeOf(i32));)",
    "(LIB_PATH",
    "pub fn firstConst(self: @This(), comptime T: type, items: []const T) ?*const T {",
    "pub fn firstHead(self: @This(), comptime T: type, items: []const T) ?*const T {)",
    "(LIB_PATH",
    "pub fn bytesMutable(self: @This(), base: [*]u8, size: usize) []u8 {",
    "pub fn rawBytesMutable(self: @This(), base: [*]u8, size: usize) []u8 {)",
    "(CATALOG_PATH",
    "- dedicated slowdown replay: `zigux/tests/phase6_bsearch_perf.zig`",
    "- dedicated slowdown replay: `zigux/tests/phase6_bsearch_perf_matrix.zig`)",
    "(CATALOG_PATH",
    "HELPER_EVIDENCE_FOCUSED_C_ABI_REPLAYS",
    "- focused C ABI replays: `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig` only)",
    "(CATALOG_PATH",
    "C_PARITY_COMPANIONS",
    "- direct C parity companions: `zigux/tests/phase6_bsearch_c_parity.zig`, `zigux/tests/fixtures/phase6_bsearch_c_harness.c`, and `scripts\\zigux/check_phase6_bsearch_corpus_evidence.zig`)",
    "(CATALOG_PATH",
    "HELPER_EVIDENCE_C_PARITY_POSTURE",
    "the direct C parity spot check now keeps 15 sorted lookup cases explicit across ascending and descending comparator-driven lookups, duplicate hits, heterogeneous string-key lookup, and mutable write-through behavior)",
    "(PARITY_CATALOG_PATH",
    "PARITY_HELPER_EVIDENCE_ROW",
    "- helper-evidence row: `zigux/tests/phase6_bsearch_perf.zig`, `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`, `zigux/tests/phase6_bsearch_c_abi_budget.zig`, `zigux/tests/fixtures/phase6_bsearch_c_harness.c`, `zigux/tests/fixtures/phase6_bsearch_vectors.zig`, `scripts\\zigux/check_phase6_bsearch_corpus_evidence.zig`, `scripts\\zigux/check_phase6_bsearch_c_parity.zig`, `Documentation/zigux/phase6-bsearch-slice.md`, `Documentation/zigux/phase6-helper-evidence-catalog.md`, `zigux/tests/phase6_helper_evidence_manifest.json`, and `zigux/tests/phase6_helper_parity_manifest.json`)",
    "(PARITY_CATALOG_PATH",
    "HELPER_POSTURE",
    "- current posture: direct helper readback is restored across the helper, focused replay, perf replay, C ABI review routes, fixture surface, and slice note)",
    "(PARITY_CATALOG_PATH",
    "PHASE6_BSEARCH_C_PARITY_CASES=17",
    "PHASE6_BSEARCH_C_PARITY_CASES=15)",
    "(HELPER_EVIDENCE_MANIFEST_PATH",
    "MANIFEST_POSTURE",
    "\"current_review_posture\": \"direct-helper-readback-stale\")",
    "(HELPER_EVIDENCE_MANIFEST_PATH",
    "NO_MISSING_COMPANIONS",
    "\"still_missing_direct_companions\": [\"zigux/tests/phase6_bsearch_casegen.zig\"])",
    "(HELPER_EVIDENCE_MANIFEST_PATH",
    "\"query_count\": 16",
    "\"query_count\": 8)",
    "(HELPER_EVIDENCE_MANIFEST_PATH",
    "f\"budget_formula\": {PERF_BUDGET_FORMULA}",
    "\"budget_formula\": \"std.math.log2_int_floor(len) + 1\")",
    "(HELPER_PARITY_MANIFEST_PATH",
    "MANIFEST_POSTURE",
    "\"current_review_posture\": \"direct-helper-readback-stale\")",
    "(HELPER_PARITY_MANIFEST_PATH",
    "NO_MISSING_COMPANIONS",
    "\"still_missing_direct_companions\": [\"zigux/tests/phase6_bsearch_casegen.zig\"])",
    "(HELPER_PARITY_MANIFEST_PATH",
    "f\"budget_formula\": {PERF_BUDGET_FORMULA}",
    "\"budget_formula\": \"std.math.log2_int_floor(len) + 1\")",
    "(HELPER_PARITY_MANIFEST_PATH",
    "f\"bound_budget_formula\": {BOUND_BUDGET_FORMULA}",
    "\"bound_budget_formula\": \"std.math.log2_int_ceil(len) + 1\")",
    "(BUDGET_TEST_PATH",
    "BOUND_BUDGET_HELPER",
    "fn maxBinarySearchBudget(len: usize) usize {)",
    "(BUDGET_TEST_PATH",
    "BOUND_BUDGET_SHIFT",
    "while (remaining > 1) : (remaining >>= 1) {)",
    "(LOWER_BOUND_TEST_PATH",
    "const mutable_lower = bsearch.bsearchLowerBoundMutable(",
    "const mutable_alias = bsearch.bsearchLowerBoundMutable()",
    "(LOWER_BOUND_TEST_PATH",
    "try std.testing.expectEqual(@intFromPtr(&insertion_duplicates[6]), @intFromPtr(typed_missing_lower));",
    "try std.testing.expectEqual(@intFromPtr(&insertion_duplicates[5]), @intFromPtr(typed_missing_lower));)",
    "(FIXTURES_PATH",
    "pub const query_count: usize = 16;",
    "pub const query_count: usize = 15;)",
    "(PERF_TEST_PATH",
    "avg_compare_calls",
    "avg_probe_calls)",
    "(PERF_TEST_PATH",
    "PERF_BUDGET_LINE",
    "const max_compare_budget = std.math.log2_int_floor(usize, case.len) + 1;)",
    "(PERF_TEST_PATH",
    "compareCountedDescending",
    "compareCountedReverse)",
    "(PERF_TEST_PATH",
    "compareCountedOpaqueDescending",
    "compareCountedOpaqueReverse)",
    "(PERF_TEST_PATH",
    "populateDescending(descending_values, ascending_values);",
    "populateDescendingPerf(descending_values, ascending_values);)",
    "(PERF_TEST_PATH",
    "const descending_witness = try runWitnessCases(",
    "const alternate_witness = try runWitnessCases()",
    "(PERF_TEST_PATH",
    "for (descending_queries, descending_expected_hits) |query, expected_hit| {",
    "for (ascending_queries, descending_expected_hits) |query, expected_hit| {)",
    "(PERF_TEST_PATH",
    "try std.testing.expect(descending_witness.max_compare_calls <= max_compare_budget);",
    "try std.testing.expect(descending_witness.max_compare_calls < max_compare_budget);)",
    "(C_PARITY_CHECKER_PATH",
    "print(f\"PHASE6_BSEARCH_C_PARITY_CASES={len(c_lines)}\")",
    "print(f\"PHASE6_BSEARCH_C_PARITY_TOTAL={len(c_lines)}\"))",
    "(C_PARITY_RUNNER_PATH",
    "try writeIndexCase(writer, \"descending-hit\", 34, bsearch.searchIndex(u32, u32, &@as(u32, 34), descending_values[0..], compareDescendingU32));",
    "try writeIndexCase(writer, \"descending-found\", 34, bsearch.searchIndex(u32, u32, &@as(u32, 34), descending_values[0..], compareDescendingU32));)",
    "(C_HARNESS_PATH",
    "static int compare_descending_u32(const void *key, const void *elt)",
    "static int compare_reverse_u32(const void *key, const void *elt))",
    "(BUILD_PATH",
    "const bsearch_perf_step = b.step(\"phase6-bsearch-perf\", \"Run Phase 6 bsearch helper perf gate\");",
    "const bsearch_perf_step = b.step(\"phase6-bsearch-scan\", \"Run Phase 6 bsearch helper perf gate\");)",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_perf_budget_formula_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-bsearch-slice.md");
    defer allocator.free(text_perf_budget_formula_path);
    const text_perf_budget_formula = try guard.readUtf8File(io, allocator, text_perf_budget_formula_path);
    defer allocator.free(text_perf_budget_formula);
    for (PERF_BUDGET_FORMULA) |marker| try guard.requireMarker(text_perf_budget_formula, marker);
    const text_bound_budget_formula_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-bsearch-slice.md");
    defer allocator.free(text_bound_budget_formula_path);
    const text_bound_budget_formula = try guard.readUtf8File(io, allocator, text_bound_budget_formula_path);
    defer allocator.free(text_bound_budget_formula);
    for (BOUND_BUDGET_FORMULA) |marker| try guard.requireMarker(text_bound_budget_formula, marker);
    const text_slice_summary_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-bsearch-slice.md");
    defer allocator.free(text_slice_summary_path);
    const text_slice_summary = try guard.readUtf8File(io, allocator, text_slice_summary_path);
    defer allocator.free(text_slice_summary);
    for (SLICE_SUMMARY) |marker| try guard.requireMarker(text_slice_summary, marker);
    const text_c_parity_companions_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-bsearch-slice.md");
    defer allocator.free(text_c_parity_companions_path);
    const text_c_parity_companions = try guard.readUtf8File(io, allocator, text_c_parity_companions_path);
    defer allocator.free(text_c_parity_companions);
    for (C_PARITY_COMPANIONS) |marker| try guard.requireMarker(text_c_parity_companions, marker);
    const text_helper_evidence_focused_c_abi_replays_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-bsearch-slice.md");
    defer allocator.free(text_helper_evidence_focused_c_abi_replays_path);
    const text_helper_evidence_focused_c_abi_replays = try guard.readUtf8File(io, allocator, text_helper_evidence_focused_c_abi_replays_path);
    defer allocator.free(text_helper_evidence_focused_c_abi_replays);
    for (HELPER_EVIDENCE_FOCUSED_C_ABI_REPLAYS) |marker| try guard.requireMarker(text_helper_evidence_focused_c_abi_replays, marker);
    const text_helper_evidence_c_parity_posture_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-bsearch-slice.md");
    defer allocator.free(text_helper_evidence_c_parity_posture_path);
    const text_helper_evidence_c_parity_posture = try guard.readUtf8File(io, allocator, text_helper_evidence_c_parity_posture_path);
    defer allocator.free(text_helper_evidence_c_parity_posture);
    for (HELPER_EVIDENCE_C_PARITY_POSTURE) |marker| try guard.requireMarker(text_helper_evidence_c_parity_posture, marker);
    const text_helper_posture_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-bsearch-slice.md");
    defer allocator.free(text_helper_posture_path);
    const text_helper_posture = try guard.readUtf8File(io, allocator, text_helper_posture_path);
    defer allocator.free(text_helper_posture);
    for (HELPER_POSTURE) |marker| try guard.requireMarker(text_helper_posture, marker);
    const text_parity_helper_evidence_row_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-bsearch-slice.md");
    defer allocator.free(text_parity_helper_evidence_row_path);
    const text_parity_helper_evidence_row = try guard.readUtf8File(io, allocator, text_parity_helper_evidence_row_path);
    defer allocator.free(text_parity_helper_evidence_row);
    for (PARITY_HELPER_EVIDENCE_ROW) |marker| try guard.requireMarker(text_parity_helper_evidence_row, marker);
    const text_manifest_posture_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-bsearch-slice.md");
    defer allocator.free(text_manifest_posture_path);
    const text_manifest_posture = try guard.readUtf8File(io, allocator, text_manifest_posture_path);
    defer allocator.free(text_manifest_posture);
    for (MANIFEST_POSTURE) |marker| try guard.requireMarker(text_manifest_posture, marker);
    const text_no_missing_companions_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-bsearch-slice.md");
    defer allocator.free(text_no_missing_companions_path);
    const text_no_missing_companions = try guard.readUtf8File(io, allocator, text_no_missing_companions_path);
    defer allocator.free(text_no_missing_companions);
    for (NO_MISSING_COMPANIONS) |marker| try guard.requireMarker(text_no_missing_companions, marker);
    const text_lib_index_range_test_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-bsearch-slice.md");
    defer allocator.free(text_lib_index_range_test_path);
    const text_lib_index_range_test = try guard.readUtf8File(io, allocator, text_lib_index_range_test_path);
    defer allocator.free(text_lib_index_range_test);
    for (LIB_INDEX_RANGE_TEST) |marker| try guard.requireMarker(text_lib_index_range_test, marker);
    const text_lib_first_const_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-bsearch-slice.md");
    defer allocator.free(text_lib_first_const_path);
    const text_lib_first_const = try guard.readUtf8File(io, allocator, text_lib_first_const_path);
    defer allocator.free(text_lib_first_const);
    for (LIB_FIRST_CONST) |marker| try guard.requireMarker(text_lib_first_const, marker);
    const text_lib_last_const_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-bsearch-slice.md");
    defer allocator.free(text_lib_last_const_path);
    const text_lib_last_const = try guard.readUtf8File(io, allocator, text_lib_last_const_path);
    defer allocator.free(text_lib_last_const);
    for (LIB_LAST_CONST) |marker| try guard.requireMarker(text_lib_last_const, marker);
    const text_lib_mutable_byte_view_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-bsearch-slice.md");
    defer allocator.free(text_lib_mutable_byte_view_path);
    const text_lib_mutable_byte_view = try guard.readUtf8File(io, allocator, text_lib_mutable_byte_view_path);
    defer allocator.free(text_lib_mutable_byte_view);
    for (LIB_MUTABLE_BYTE_VIEW) |marker| try guard.requireMarker(text_lib_mutable_byte_view, marker);
    const text_perf_budget_line_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-bsearch-slice.md");
    defer allocator.free(text_perf_budget_line_path);
    const text_perf_budget_line = try guard.readUtf8File(io, allocator, text_perf_budget_line_path);
    defer allocator.free(text_perf_budget_line);
    for (PERF_BUDGET_LINE) |marker| try guard.requireMarker(text_perf_budget_line, marker);
    const text_bound_budget_helper_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-bsearch-slice.md");
    defer allocator.free(text_bound_budget_helper_path);
    const text_bound_budget_helper = try guard.readUtf8File(io, allocator, text_bound_budget_helper_path);
    defer allocator.free(text_bound_budget_helper);
    for (BOUND_BUDGET_HELPER) |marker| try guard.requireMarker(text_bound_budget_helper, marker);
    const text_bound_budget_shift_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-bsearch-slice.md");
    defer allocator.free(text_bound_budget_shift_path);
    const text_bound_budget_shift = try guard.readUtf8File(io, allocator, text_bound_budget_shift_path);
    defer allocator.free(text_bound_budget_shift);
    for (BOUND_BUDGET_SHIFT) |marker| try guard.requireMarker(text_bound_budget_shift, marker);
    const text_self_test_cases_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_self_test_cases_path);
    const text_self_test_cases = try guard.readUtf8File(io, allocator, text_self_test_cases_path);
    defer allocator.free(text_self_test_cases);
    for (SELF_TEST_CASES) |marker| try guard.requireMarker(text_self_test_cases, marker);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    try checkRepo(io, allocator, try guard.defaultRepoRoot(allocator));
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    checkRepo(io, allocator, root) catch {
        std.process.exit(1);
    };
    try guard.printLine(io, "{s}", .{live_pass_marker});
}
