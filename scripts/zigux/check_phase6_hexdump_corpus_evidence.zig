const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE6_HEXDUMP_CORPUS_EVIDENCE=pass";
pub const self_test_pass_marker = "PHASE6_HEXDUMP_CORPUS_EVIDENCE_SELF_TEST=pass";

const EXPECTED_PERF_LABELS = [_][]const u8{
    "16B-plain-g1",
    "32B-ascii-g2",
    "16B-ascii-g4",
    "16B-ascii-g8",
};

const EXPECTED_LENGTH_CASES = [_][]const u8{
    "empty plain line reports zero length",
    "empty ascii line reports zero length",
    "plain rowsize-16 group-1 line length",
    "ascii rowsize-16 group-1 line length",
    "plain rowsize-16 group-4 line length",
    "ascii rowsize-16 group-4 line length",
    "ascii rowsize-32 group-1 line length",
    "plain rowsize-16 group-8 line length",
    "ascii rowsize-16 group-8 line length",
    "normalized rowsize and groupsize fallback line length",
    "uneven group fallback line length",
};

const EXPECTED_OVERFLOW_CASES = [_][]const u8{
    "zero-sized caller buffer reports required ascii length",
    "short ascii buffer truncates but stays NUL terminated",
    "grouped plain buffer truncates deterministically",
    "normalized ascii buffer truncates after fallback formatting",
};

const EXPECTED_SLICE_SNIPPETS = [_][]const u8{
    "- `scripts\\zigux/check_phase6_hexdump_corpus_evidence.zig`",
    "- exact fixture-owned corpus counts on current `master`: 10 parity cases, 4 overflow cases, 11 curated length cases, and 4 perf replay cases, all centralized in `zigux/tests/fixtures/phase6_hexdump_vectors.zig` and replayed by `zigux/tests/phase6_hexdump.zig`, `zigux/tests/phase6_hexdump_perf.zig`, or `zigux/tests/phase6_hexdump_perf_matrix.zig`",
    "- the same fixture packet keeps rowsize normalization, uneven-groupsize fallback, grouped-output text, overflow truncation, and the four-case perf matrix reviewable without widening into neighboring Phase 6 helpers",
};

const EXPECTED_CATALOG_SNIPPETS = [_][]const u8{
    "- dedicated corpus checker: `scripts\\zigux/check_phase6_hexdump_corpus_evidence.zig`",
    "- exact fixture-owned corpus counts: 10 parity cases, 4 overflow cases, 11 curated length cases, and 4 perf replay cases in `zigux/tests/fixtures/phase6_hexdump_vectors.zig`",
};

const EXPECTED_PARITY_CATALOG_SNIPPETS = [_][]const u8{
    "`scripts\\zigux/check_phase6_hexdump_corpus_evidence.zig`",
    "direct helper readback is restored across the helper, focused replay, perf replay, perf-matrix preflight, fixture surface, dedicated corpus checker, packet checker, route checker, slice note, and perf-refresh rationale note",
};

const EXPECTED_HELPER_TEST_SNIPPETS = [_][]const u8{
    "test \"phase 6 hexdump helper packet replays the serialized parity matrix\" {",
    "test \"phase 6 hexdump helper packet preserves the overflow contract\" {",
    "test \"phase 6 hexdump helper packet preserves the curated length matrix\" {",
    "test \"phase 6 hexdump direct helper entrypoints stay aligned with the packet\" {",
    "test \"phase 6 hexdump direct pack helpers keep uppercase and lowercase nibble parity\" {",
};

const EXPECTED_PERF_TEST_SNIPPETS = [_][]const u8{
    "fn validatePerfMatrix() !void {",
    "fixtures.perf_cases",
    "PHASE6_HEXDUMP_PERF_CASE_COUNT",
    "error.HexdumpPerfRegression",
};

const EXPECTED_PERF_MATRIX_SNIPPETS = [_][]const u8{
    "test \"phase 6 hexdump perf matrix preflight stays aligned with the documented packet\" {",
    ".label = \"16B-plain-g1\",",
    ".label = \"32B-ascii-g2\",",
    ".label = \"16B-ascii-g4\",",
    ".label = \"16B-ascii-g8\",",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_expected_perf_labels_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-hexdump-slice.md");
    defer allocator.free(text_expected_perf_labels_path);
    const text_expected_perf_labels = try guard.readUtf8File(io, allocator, text_expected_perf_labels_path);
    defer allocator.free(text_expected_perf_labels);
    for (EXPECTED_PERF_LABELS) |marker| try guard.requireMarker(text_expected_perf_labels, marker);
    const text_expected_length_cases_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-hexdump-slice.md");
    defer allocator.free(text_expected_length_cases_path);
    const text_expected_length_cases = try guard.readUtf8File(io, allocator, text_expected_length_cases_path);
    defer allocator.free(text_expected_length_cases);
    for (EXPECTED_LENGTH_CASES) |marker| try guard.requireMarker(text_expected_length_cases, marker);
    const text_expected_overflow_cases_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-hexdump-slice.md");
    defer allocator.free(text_expected_overflow_cases_path);
    const text_expected_overflow_cases = try guard.readUtf8File(io, allocator, text_expected_overflow_cases_path);
    defer allocator.free(text_expected_overflow_cases);
    for (EXPECTED_OVERFLOW_CASES) |marker| try guard.requireMarker(text_expected_overflow_cases, marker);
    const text_expected_slice_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-hexdump-slice.md");
    defer allocator.free(text_expected_slice_snippets_path);
    const text_expected_slice_snippets = try guard.readUtf8File(io, allocator, text_expected_slice_snippets_path);
    defer allocator.free(text_expected_slice_snippets);
    for (EXPECTED_SLICE_SNIPPETS) |marker| try guard.requireMarker(text_expected_slice_snippets, marker);
    const text_expected_catalog_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-hexdump-slice.md");
    defer allocator.free(text_expected_catalog_snippets_path);
    const text_expected_catalog_snippets = try guard.readUtf8File(io, allocator, text_expected_catalog_snippets_path);
    defer allocator.free(text_expected_catalog_snippets);
    for (EXPECTED_CATALOG_SNIPPETS) |marker| try guard.requireMarker(text_expected_catalog_snippets, marker);
    const text_expected_parity_catalog_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-hexdump-slice.md");
    defer allocator.free(text_expected_parity_catalog_snippets_path);
    const text_expected_parity_catalog_snippets = try guard.readUtf8File(io, allocator, text_expected_parity_catalog_snippets_path);
    defer allocator.free(text_expected_parity_catalog_snippets);
    for (EXPECTED_PARITY_CATALOG_SNIPPETS) |marker| try guard.requireMarker(text_expected_parity_catalog_snippets, marker);
    const text_expected_helper_test_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-hexdump-slice.md");
    defer allocator.free(text_expected_helper_test_snippets_path);
    const text_expected_helper_test_snippets = try guard.readUtf8File(io, allocator, text_expected_helper_test_snippets_path);
    defer allocator.free(text_expected_helper_test_snippets);
    for (EXPECTED_HELPER_TEST_SNIPPETS) |marker| try guard.requireMarker(text_expected_helper_test_snippets, marker);
    const text_expected_perf_test_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-hexdump-slice.md");
    defer allocator.free(text_expected_perf_test_snippets_path);
    const text_expected_perf_test_snippets = try guard.readUtf8File(io, allocator, text_expected_perf_test_snippets_path);
    defer allocator.free(text_expected_perf_test_snippets);
    for (EXPECTED_PERF_TEST_SNIPPETS) |marker| try guard.requireMarker(text_expected_perf_test_snippets, marker);
    const text_expected_perf_matrix_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-hexdump-slice.md");
    defer allocator.free(text_expected_perf_matrix_snippets_path);
    const text_expected_perf_matrix_snippets = try guard.readUtf8File(io, allocator, text_expected_perf_matrix_snippets_path);
    defer allocator.free(text_expected_perf_matrix_snippets);
    for (EXPECTED_PERF_MATRIX_SNIPPETS) |marker| try guard.requireMarker(text_expected_perf_matrix_snippets, marker);
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
