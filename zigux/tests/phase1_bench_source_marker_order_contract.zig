const std = @import("std");

const checker_source =
    \\SOURCE_MARKER_SETS = (
    \\    FIND_BIT_REQUIRED_SOURCE_MARKERS,
    \\    RBTREE_REQUIRED_SOURCE_MARKERS,
    \\)
    \\
    \\def duplicate_marker_labels(text: str, marker_set: dict[str, str]) -> list[str]:
    \\    duplicates: list[str] = []
    \\    for label, marker in marker_set.items():
    \\        if text.count(marker) > 1:
    \\            duplicates.append(label)
    \\    return duplicates
    \\
    \\def validate_bench_source(text: str) -> tuple[str, object]:
    \\    missing: list[str] = []
    \\    for marker_set in SOURCE_MARKER_SETS:
    \\        for label, marker in marker_set.items():
    \\            if marker not in text:
    \\                missing.append(label)
    \\    if missing:
    \\        return ("bench_source_missing_markers", missing)
    \\    duplicate_rbtree_markers = duplicate_marker_labels(text, RBTREE_REQUIRED_SOURCE_MARKERS)
    \\    if duplicate_rbtree_markers:
    \\        return ("bench_source_duplicate_rbtree_markers", duplicate_rbtree_markers)
    \\    return ("pass", text)
;

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "bench source marker sets keep find_bit before rbtree" {
    try requireContains(checker_source, "SOURCE_MARKER_SETS = (");
    try requireContains(checker_source, "FIND_BIT_REQUIRED_SOURCE_MARKERS,");
    try requireContains(checker_source, "RBTREE_REQUIRED_SOURCE_MARKERS,");
    try requireBefore(
        checker_source,
        "FIND_BIT_REQUIRED_SOURCE_MARKERS,",
        "RBTREE_REQUIRED_SOURCE_MARKERS,",
    );
}

test "bench source validation fails closed before duplicate checks" {
    try requireBefore(
        checker_source,
        "if missing:",
        "duplicate_rbtree_markers = duplicate_marker_labels(text, RBTREE_REQUIRED_SOURCE_MARKERS)",
    );
    try requireContains(checker_source, "return (\"bench_source_missing_markers\", missing)");
}

test "rbtree duplicate marker guard remains explicit" {
    try requireContains(
        checker_source,
        "duplicate_rbtree_markers = duplicate_marker_labels(text, RBTREE_REQUIRED_SOURCE_MARKERS)",
    );
    try requireContains(
        checker_source,
        "return (\"bench_source_duplicate_rbtree_markers\", duplicate_rbtree_markers)",
    );
    try requireBefore(
        checker_source,
        "duplicate_rbtree_markers = duplicate_marker_labels(text, RBTREE_REQUIRED_SOURCE_MARKERS)",
        "return (\"pass\", text)",
    );
}
