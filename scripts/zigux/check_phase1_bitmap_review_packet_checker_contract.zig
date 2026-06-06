const std = @import("std");
const source_path = @import("source_path").path;

const SourceContract = struct {
    const Required = struct {
        label: []const u8,
        marker: []const u8,
    };

    const source_markers = [_]Required{
        .{
            .label = "checker_docstring",
            .marker = "\"\"\"Guard the Phase 1 bitmap review packet against helper-local drift.\"\"\"",
        },
        .{
            .label = "bitmap_relative_path",
            .marker = "BITMAP_REL = Path(\"tools/lib/bitmap.zig\")",
        },
        .{
            .label = "manifest_relative_path",
            .marker = "MANIFEST_REL = Path(\"zigux/tests/fixtures/phase1_helper_manifest.json\")",
        },
        .{
            .label = "fixture_relative_path",
            .marker = "FIXTURE_REL = Path(\"zigux/tests/fixtures/phase1_helpers.json\")",
        },
        .{
            .label = "closure_relative_path",
            .marker = "CLOSURE_REL = Path(\"Documentation/zigux/phase1-closure.md\")",
        },
        .{
            .label = "helper_test_roster",
            .marker = "REQUIRED_HELPER_TESTS = [",
        },
        .{
            .label = "manifest_field_roster",
            .marker = "REQUIRED_MANIFEST_FIELDS: dict[str, Any] = {",
        },
        .{
            .label = "fixture_key_roster",
            .marker = "REQUIRED_FIXTURE_KEYS = [",
        },
        .{
            .label = "closure_marker_roster",
            .marker = "REQUIRED_CLOSURE_MARKERS = [",
        },
        .{
            .label = "exact_text_count_helper",
            .marker = "def require_text_once(text: str, rel: Path, markers: list[str], issues: list[str]) -> None:",
        },
        .{
            .label = "issue_collector",
            .marker = "def collect_issues(root: Path) -> list[str]:",
        },
        .{
            .label = "sample_root_builder",
            .marker = "def write_sample_root(root: Path) -> None:",
        },
        .{
            .label = "self_test_runner",
            .marker = "def run_self_test() -> None:",
        },
        .{
            .label = "public_self_test_pass",
            .marker = "PHASE1_BITMAP_REVIEW_PACKET_SELF_TEST=pass",
        },
        .{
            .label = "public_self_test_count",
            .marker = "PHASE1_BITMAP_REVIEW_PACKET_SELF_TEST_CASE_COUNT={case_count}",
        },
        .{
            .label = "public_live_pass",
            .marker = "PHASE1_BITMAP_REVIEW_PACKET=pass",
        },
        .{
            .label = "public_helper_output",
            .marker = "PHASE1_BITMAP_REVIEW_PACKET_HELPER={BITMAP_HELPER}",
        },
        .{
            .label = "public_fixture_key_count",
            .marker = "PHASE1_BITMAP_REVIEW_PACKET_FIXTURE_KEY_COUNT={len(REQUIRED_FIXTURE_KEYS)}",
        },
        .{
            .label = "public_helper_test_count",
            .marker = "PHASE1_BITMAP_REVIEW_PACKET_HELPER_TEST_COUNT={len(REQUIRED_HELPER_TESTS)}",
        },
    };

    const helper_anchor_markers = [_]Required{
        .{
            .label = "range_edges",
            .marker = "    'test \"bitmap range helpers preserve edges across whole-word spans\"',",
        },
        .{
            .label = "copy_zero_sized_views",
            .marker = "    'test \"bitmap copy helpers keep zero-sized destination views untouched\"',",
        },
        .{
            .label = "tail_mask_predicates",
            .marker = "    'test \"bitmap tail-masked helpers ignore out-of-range differences\"',",
        },
        .{
            .label = "weighted_tail_count",
            .marker = "    'test \"bitmap weighted or and xor clamp counts to the declared tail window\"',",
        },
        .{
            .label = "scnprintf_cross_word",
            .marker = "    'test \"bitmap scnprintf keeps contiguous ranges merged across word boundaries\"',",
        },
        .{
            .label = "empty_buffer",
            .marker = "    'test \"bitmap scnprintf leaves the caller buffer untouched for an empty bitmap\"',",
        },
        .{
            .label = "linux_aliases",
            .marker = "    'test \"bitmap Linux-style aliases mirror copy logical range and format helpers\"',",
        },
        .{
            .label = "allocation_helpers",
            .marker = "    'test \"bitmap allocation helpers size zero fill and reset optionals\"',",
        },
    };

    const manifest_and_fixture_markers = [_]Required{
        .{
            .label = "final_partial_word_anchor",
            .marker = "\"final_partial_word_anchor\": 'test \"bitmap range helpers preserve edges across whole-word spans\"',",
        },
        .{
            .label = "partial_xor_review_fields",
            .marker = "\"partial_xor_review_fields\": [\"partial_xor_nbits\", \"partial_xor_masked_values\"],",
        },
        .{
            .label = "helper_test_anchor_validation",
            .marker = "if marker not in helper_tests:",
        },
        .{
            .label = "manifest_field_validation",
            .marker = "if bitmap_anchors.get(field) != expected:",
        },
        .{
            .label = "bitmap_fixture_section",
            .marker = "bitmap_fixture = fixture.get(\"bitmap\")",
        },
        .{
            .label = "fixture_key_missing_output",
            .marker = "issues.append(f\"{FIXTURE_REL.as_posix()}:bitmap:{key}:missing\")",
        },
        .{
            .label = "partial_xor_masked_fixture_key",
            .marker = "\"partial_xor_masked_values\",",
        },
    };

    const closure_markers = [_]Required{
        .{
            .label = "bitmap_direct_review",
            .marker = "\"PHASE1_BITMAP_DIRECT_REVIEW=helper-local bitmap direct anchors stay explicit\",",
        },
        .{
            .label = "bitmap_unit_review",
            .marker = "\"PHASE1_BITMAP_UNIT_REVIEW=bitmap multiword-tail xorBits behavior still lets callers clamp\",",
        },
        .{
            .label = "bitmap_empty_unit_review",
            .marker = "\"PHASE1_BITMAP_EMPTY_UNIT_REVIEW=bitmap_scnprintf leaves a non-empty caller buffer untouched\",",
        },
        .{
            .label = "bitmap_final_partial_review",
            .marker = "\"PHASE1_BITMAP_FINAL_PARTIAL_WORD_REVIEW=helper-local bitmap final partial-word proof stays explicit\",",
        },
        .{
            .label = "bitmap_linux_alias_review",
            .marker = "\"PHASE1_BITMAP_LINUX_ALIAS_REVIEW=helper-local bitmap Linux-style alias proof stays explicit\",",
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

test "bitmap review checker keeps validation structure and public outputs" {
    const source = try SourceContract.readSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try SourceContract.assertMarkerSet(source, &SourceContract.source_markers);
}

test "bitmap review checker keeps helper manifest and fixture anchors" {
    const source = try SourceContract.readSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try SourceContract.assertMarkerSet(source, &SourceContract.helper_anchor_markers);
    try SourceContract.assertMarkerSet(source, &SourceContract.manifest_and_fixture_markers);
}

test "bitmap review checker keeps closure marker and negative self-test coverage" {
    const source = try SourceContract.readSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try SourceContract.assertMarkerSet(source, &SourceContract.closure_markers);
    try SourceContract.requireExactlyOnce(source, "missing_helper_test_self_test", "bitmap_text.replace(REQUIRED_HELPER_TESTS[0] + \" {}\\n\", \"\", 1)");
    try SourceContract.requireExactlyOnce(source, "manifest_drift_self_test", "manifest[\"review_anchors\"][BITMAP_HELPER][\"zero_bit_noop_anchor\"] = \"drifted\"");
    try SourceContract.requireExactlyOnce(source, "fixture_missing_key_self_test", "del fixture[\"bitmap\"][\"partial_xor_masked_values\"]");
    try SourceContract.requireExactlyOnce(source, "closure_drift_self_test", "replace(REQUIRED_CLOSURE_MARKERS[-1], \"drifted\", 1)");
}
