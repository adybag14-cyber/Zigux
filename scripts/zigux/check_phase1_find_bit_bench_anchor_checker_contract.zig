const std = @import("std");

const source_option_name = "source-path";
const default_source_path = "scripts/zigux/check-phase1-find-bit-bench-anchors.py";

const Marker = struct {
    label: []const u8,
    text: []const u8,
};

const CountMarker = struct {
    label: []const u8,
    text: []const u8,
    expected: usize,
};

const required_top_level_markers = [_]Marker{
    .{ .label = "find_bit_rel", .text = "FIND_BIT_REL = Path(\"tools/lib/find_bit.zig\")" },
    .{ .label = "required_test_markers", .text = "REQUIRED_TEST_MARKERS = {" },
    .{ .label = "required_source_count_markers", .text = "REQUIRED_SOURCE_COUNT_MARKERS = {" },
    .{ .label = "required_source_exact_markers", .text = "REQUIRED_SOURCE_EXACT_MARKERS = {" },
    .{ .label = "validate_find_bit_source", .text = "def validate_find_bit_source(text: str) -> tuple[str, object]:" },
    .{ .label = "self_test", .text = "def run_self_test() -> None:" },
    .{ .label = "pass_status", .text = "PHASE1_FIND_BIT_BENCH_ANCHORS=pass" },
    .{ .label = "fail_status", .text = "PHASE1_FIND_BIT_BENCH_ANCHORS=fail" },
    .{ .label = "self_test_status", .text = "PHASE1_FIND_BIT_BENCH_ANCHORS_SELF_TEST=pass" },
    .{ .label = "self_test_count_status", .text = "PHASE1_FIND_BIT_BENCH_ANCHORS_SELF_TEST_CASE_COUNT=" },
};

const required_checker_flow_markers = [_]Marker{
    .{ .label = "test_marker_first", .text = "test_failures = collect_marker_count_failures(text, REQUIRED_TEST_MARKERS)" },
    .{ .label = "source_count_second", .text = "source_count_failures = collect_expected_count_failures(text, REQUIRED_SOURCE_COUNT_MARKERS)" },
    .{ .label = "source_exact_third", .text = "source_exact_failures = collect_marker_count_failures(text, REQUIRED_SOURCE_EXACT_MARKERS)" },
    .{ .label = "missing_file_loader", .text = "except FileNotFoundError:" },
    .{ .label = "marker_for_label_coverage", .text = "def marker_for_label(label: str) -> str:" },
    .{ .label = "build_sample_source_coverage", .text = "def build_sample_source(" },
    .{ .label = "omit_self_test_cases", .text = "build_sample_source(omit_label=label)" },
    .{ .label = "duplicate_self_test_cases", .text = "build_sample_source(duplicate_label=label)" },
};

const required_find_bit_anchor_labels = [_]Marker{
    .{ .label = "andnot_gap_test", .text = "\"andnot_gap_test\"" },
    .{ .label = "same_word_start_mask_test", .text = "\"same_word_start_mask_test\"" },
    .{ .label = "single_word_partial_window_test", .text = "\"single_word_partial_window_test\"" },
    .{ .label = "tail_word_zero_shared_skip_test", .text = "\"tail_word_zero_shared_skip_test\"" },
    .{ .label = "clump8_skip_forward_test", .text = "\"clump8_skip_forward_test\"" },
    .{ .label = "clump8_word_boundary_test", .text = "\"clump8_word_boundary_test\"" },
    .{ .label = "underscore_andnot_alias_test", .text = "\"underscore_andnot_alias_test\"" },
    .{ .label = "linux_andnot_alias_test", .text = "\"linux_andnot_alias_test\"" },
    .{ .label = "last_bit_exact_word_boundary_test", .text = "\"last_bit_exact_word_boundary_test\"" },
};

const required_counted_anchor_labels = [_]Marker{
    .{ .label = "find_next_boundary", .text = "\"find_next_boundary\"" },
    .{ .label = "find_next_and_boundary", .text = "\"find_next_and_boundary\"" },
    .{ .label = "find_next_andnot_boundary", .text = "\"find_next_andnot_boundary\"" },
    .{ .label = "find_next_or_boundary", .text = "\"find_next_or_boundary\"" },
    .{ .label = "find_next_zero_boundary", .text = "\"find_next_zero_boundary\"" },
    .{ .label = "find_first_andnot_low_level_alias", .text = "\"find_first_andnot_low_level_alias\"" },
};

const required_source_exact_labels = [_]Marker{
    .{ .label = "find_next_andnot_word_boundary_follow", .text = "\"find_next_andnot_word_boundary_follow\"" },
    .{ .label = "find_next_andnot_single_word_tail_stop", .text = "\"find_next_andnot_single_word_tail_stop\"" },
    .{ .label = "find_next_andnot_tail_skip", .text = "\"find_next_andnot_tail_skip\"" },
    .{ .label = "find_next_andnot_tail_skip_stop", .text = "\"find_next_andnot_tail_skip_stop\"" },
    .{ .label = "find_clump8_past_end", .text = "\"find_clump8_past_end\"" },
    .{ .label = "find_clump8_linux_alias_past_end", .text = "\"find_clump8_linux_alias_past_end\"" },
    .{ .label = "find_clump8_low_level_alias_past_end", .text = "\"find_clump8_low_level_alias_past_end\"" },
    .{ .label = "find_get_value8_last_aligned", .text = "\"find_get_value8_last_aligned\"" },
    .{ .label = "find_next_andnot_linux_alias", .text = "\"find_next_andnot_linux_alias\"" },
};

const required_count_occurrences = [_]CountMarker{
    .{ .label = "source_marker_group_declarations_and_uses", .text = "REQUIRED_SOURCE_", .expected = 4 },
    .{ .label = "marker_count_helper_reuse", .text = "collect_marker_count_failures", .expected = 2 },
    .{ .label = "expected_count_helper_reuse", .text = "collect_expected_count_failures", .expected = 1 },
    .{ .label = "self_test_case_count_print", .text = "PHASE1_FIND_BIT_BENCH_ANCHORS_SELF_TEST_CASE_COUNT", .expected = 1 },
};

fn readSource(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(512 * 1024),
    );
}

fn expectContains(source: []const u8, marker: Marker) !void {
    if (std.mem.indexOf(u8, source, marker.text) == null) {
        std.debug.print("missing marker: {s}\n", .{marker.label});
        return error.MissingMarker;
    }
}

fn expectCount(source: []const u8, marker: CountMarker) !void {
    const actual = std.mem.count(u8, source, marker.text);
    if (actual != marker.expected) {
        std.debug.print(
            "marker count mismatch: {s}: expected {}, got {}\n",
            .{ marker.label, marker.expected, actual },
        );
        return error.MarkerCountMismatch;
    }
}

fn sourcePath() []const u8 {
    return @import("build_options").source_path;
}

test "find-bit bench checker keeps public source and status contract" {
    const source = try readSource(sourcePath());
    defer std.testing.allocator.free(source);

    inline for (required_top_level_markers) |marker| {
        try expectContains(source, marker);
    }
}

test "find-bit bench checker preserves validation flow and self-test envelope" {
    const source = try readSource(sourcePath());
    defer std.testing.allocator.free(source);

    inline for (required_checker_flow_markers) |marker| {
        try expectContains(source, marker);
    }
    inline for (required_count_occurrences) |marker| {
        try expectCount(source, marker);
    }
}

test "find-bit bench checker guards the bench-adjacent anchor families" {
    const source = try readSource(sourcePath());
    defer std.testing.allocator.free(source);

    inline for (required_find_bit_anchor_labels) |marker| {
        try expectContains(source, marker);
    }
    inline for (required_counted_anchor_labels) |marker| {
        try expectContains(source, marker);
    }
    inline for (required_source_exact_labels) |marker| {
        try expectContains(source, marker);
    }
}
