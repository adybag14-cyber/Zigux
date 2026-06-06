const std = @import("std");
const source_path = @import("source_path").path;

const SourceContract = struct {
    source_path: []const u8,

    const Required = struct {
        label: []const u8,
        marker: []const u8,
    };

    const source_markers = [_]Required{
        .{
            .label = "checker_docstring",
            .marker = "\"\"\"Guard the Phase 1 bitmap direct-anchor packet against helper-local drift.\"\"\"",
        },
        .{
            .label = "bitmap_relative_path",
            .marker = "BITMAP_REL = Path(\"tools/lib/bitmap.zig\")",
        },
        .{
            .label = "test_marker_roster",
            .marker = "REQUIRED_TEST_MARKERS = {",
        },
        .{
            .label = "source_marker_roster",
            .marker = "REQUIRED_SOURCE_MARKERS = {",
        },
        .{
            .label = "marker_count_collector",
            .marker = "def collect_marker_count_failures(text: str, markers: dict[str, str]) -> list[str]:",
        },
        .{
            .label = "source_validator",
            .marker = "def validate_bitmap_source(text: str) -> tuple[str, object]:",
        },
        .{
            .label = "source_loader",
            .marker = "def load_bitmap_source(root: Path) -> tuple[str, object]:",
        },
        .{
            .label = "sample_builder",
            .marker = "def build_sample_source(omit_label: str | None = None, duplicate_label: str | None = None) -> str:",
        },
        .{
            .label = "self_test_runner",
            .marker = "def run_self_test() -> None:",
        },
        .{
            .label = "public_self_test_pass",
            .marker = "PHASE1_BITMAP_DIRECT_ANCHORS_SELF_TEST=pass",
        },
        .{
            .label = "public_self_test_count",
            .marker = "PHASE1_BITMAP_DIRECT_ANCHORS_SELF_TEST_CASE_COUNT={case_count}",
        },
        .{
            .label = "public_live_pass",
            .marker = "PHASE1_BITMAP_DIRECT_ANCHORS=pass",
        },
        .{
            .label = "public_live_helper",
            .marker = "PHASE1_BITMAP_DIRECT_ANCHORS_HELPER={BITMAP_REL.as_posix()}",
        },
    };

    const representative_bitmap_anchors = [_]Required{
        .{
            .label = "copy_zero_sized_views",
            .marker = "\"copy_zero_sized_views\": 'test \"bitmap copy helpers keep zero-sized destination views untouched\" {',",
        },
        .{
            .label = "tail_mask_predicates",
            .marker = "\"tail_mask_predicates\": 'test \"bitmap tail-masked helpers ignore out-of-range differences\" {',",
        },
        .{
            .label = "weighted_and_andnot_tail",
            .marker = "\"weighted_and_andnot_tail\": 'test \"bitmap weighted and andnot clamp counts to the declared tail window\" {',",
        },
        .{
            .label = "linux_alias_size_alloc",
            .marker = "\"linux_alias_size_alloc\": 'test \"bitmap Linux-style aliases mirror size state and allocation helpers\" {',",
        },
        .{
            .label = "bitmap_copy_clear_tail_alias",
            .marker = "\"bitmap_copy_clear_tail_alias\": \"pub fn bitmap_copy_clear_tail(dst: []Word, src: []const Word, nbits: usize) void {\",",
        },
        .{
            .label = "bitmap_weighted_xor_alias",
            .marker = "\"bitmap_weighted_xor_alias\": \"pub fn bitmap_weighted_xor(dst: []Word, src1: []const Word, src2: []const Word, nbits: usize) usize {\",",
        },
        .{
            .label = "bitmap_scnprintf_alias",
            .marker = "\"bitmap_scnprintf_alias\": \"pub fn bitmap_scnprintf(bitmap: []const Word, nbits: usize, buffer: []u8) usize {\",",
        },
        .{
            .label = "empty_buffer_preserved_assert",
            .marker = "\"empty_buffer_preserved_assert\": \"try std.testing.expectEqualSlices(u8, &[_]u8{ 0xaa, 0xaa, 0xaa, 0xaa }, &buffer);\",",
        },
        .{
            .label = "bitmap_zalloc_alias_assert",
            .marker = "\"bitmap_zalloc_alias_assert\": \"var zeroed_alias: ?[]Word = try bitmap_zalloc(allocator, nbits);\",",
        },
    };

    fn readSource(allocator: std.mem.Allocator) ![]u8 {
        return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, source_path, allocator, .limited(1024 * 1024));
    }

    fn requireExactlyOnce(text: []const u8, label: []const u8, marker: []const u8) !void {
        const count = std.mem.count(u8, text, marker);
        if (count != 1) {
            std.debug.print("{s}: expected once, found {d}: {s}\n", .{ label, count, marker });
            return error.MarkerCountMismatch;
        }
    }

    fn assertMarkerSet(text: []const u8, markers: []const Required) !void {
        for (markers) |entry| {
            try requireExactlyOnce(text, entry.label, entry.marker);
        }
    }
};

test "bitmap direct-anchor checker keeps source validation structure" {
    const source = try SourceContract.readSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try SourceContract.assertMarkerSet(source, &SourceContract.source_markers);
}

test "bitmap direct-anchor checker keeps representative helper anchor roster" {
    const source = try SourceContract.readSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try SourceContract.assertMarkerSet(source, &SourceContract.representative_bitmap_anchors);
}

test "bitmap direct-anchor checker self-test covers omit duplicate and missing-file cases" {
    const source = try SourceContract.readSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try SourceContract.requireExactlyOnce(source, "omit_test_loop", "for label in REQUIRED_TEST_MARKERS:");
    try SourceContract.requireExactlyOnce(source, "omit_source_loop", "for label in REQUIRED_SOURCE_MARKERS:");
    try SourceContract.requireExactlyOnce(source, "duplicate_test_loop", "build_sample_source(duplicate_label=label)");
    try SourceContract.requireExactlyOnce(source, "missing_file_case", "assert kind == \"missing_file\", (kind, payload)");
    try SourceContract.requireExactlyOnce(source, "pass_case", "assert kind == \"pass\", (kind, payload)");
}
