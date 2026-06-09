const std = @import("std");

const Source = struct {
    text: []const u8,

    fn requireContains(self: Source, needle: []const u8) !void {
        try std.testing.expect(std.mem.indexOf(u8, self.text, needle) != null);
    }

    fn requireBefore(self: Source, before: []const u8, after: []const u8) !void {
        const before_index = std.mem.indexOf(u8, self.text, before) orelse return error.MissingBeforeMarker;
        const after_index = std.mem.indexOf(u8, self.text, after) orelse return error.MissingAfterMarker;
        try std.testing.expect(before_index < after_index);
    }
};

fn readSource() !Source {
    const path = "scripts/zigux/check-phase1-bitmap-review-packet.py";
    const text = try std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, std.testing.allocator, .limited(1024 * 1024));
    return .{ .text = text };
}

test "bitmap review checker owns the Phase 1 bitmap packet surfaces" {
    const source = try readSource();
    defer std.testing.allocator.free(source.text);

    try source.requireContains("\"\"\"Guard the Phase 1 bitmap review packet against helper-local drift.\"\"\"");
    try source.requireContains("BITMAP_REL = Path(\"tools/lib/bitmap.zig\")");
    try source.requireContains("MANIFEST_REL = Path(\"zigux/tests/fixtures/phase1_helper_manifest.json\")");
    try source.requireContains("FIXTURE_REL = Path(\"zigux/tests/fixtures/phase1_helpers.json\")");
    try source.requireContains("CLOSURE_REL = Path(\"Documentation/zigux/phase1-closure.md\")");
    try source.requireContains("BITMAP_HELPER = \"tools/lib/bitmap.zig\"");
    try source.requireContains("REQUIRED_HELPER_TESTS = [");
    try source.requireContains("REQUIRED_MANIFEST_FIELDS: dict[str, Any] = {");
    try source.requireContains("REQUIRED_FIXTURE_KEYS = [");
    try source.requireContains("REQUIRED_CLOSURE_MARKERS = [");
    try source.requireBefore("REQUIRED_HELPER_TESTS = [", "REQUIRED_MANIFEST_FIELDS: dict[str, Any] = {");
    try source.requireBefore("REQUIRED_MANIFEST_FIELDS: dict[str, Any] = {", "REQUIRED_FIXTURE_KEYS = [");
    try source.requireBefore("REQUIRED_FIXTURE_KEYS = [", "REQUIRED_CLOSURE_MARKERS = [");
}

test "bitmap review marker rosters keep helper manifest fixture and closure anchors" {
    const source = try readSource();
    defer std.testing.allocator.free(source.text);

    try source.requireContains("'test \"bitmap range helpers preserve edges across whole-word spans\"'");
    try source.requireContains("'test \"bitmap copy alias preserves raw source words without tail clearing\"'");
    try source.requireContains("'test \"bitmap weighted or and xor clamp counts to the declared tail window\"'");
    try source.requireContains("'test \"bitmap scnprintf leaves the caller buffer untouched for an empty bitmap\"'");
    try source.requireContains("'test \"bitmap Linux-style aliases mirror copy logical range and format helpers\"'");
    try source.requireContains("\"first_word_boundary_anchor\": 'test \"bitmap range helpers preserve edges across whole-word spans\"'");
    try source.requireContains("\"partial_xor_review_fields\": [\"partial_xor_nbits\", \"partial_xor_masked_values\"]");
    try source.requireContains("\"partial_xor_masked_values\"");
    try source.requireContains("\"copy_clear_tail_values\"");
    try source.requireContains("\"PHASE1_BITMAP_DIRECT_REVIEW=helper-local bitmap direct anchors stay explicit\"");
    try source.requireContains("\"PHASE1_BITMAP_EMPTY_UNIT_REVIEW=bitmap_scnprintf leaves a non-empty caller buffer untouched\"");
    try source.requireContains("\"PHASE1_BITMAP_LINUX_ALIAS_REVIEW=helper-local bitmap Linux-style alias proof stays explicit\"");
}

test "issue collection self-test and public outputs stay wired into the checker" {
    const source = try readSource();
    defer std.testing.allocator.free(source.text);

    try source.requireContains("def require_text_once(text: str, rel: Path, markers: list[str], issues: list[str]) -> None:");
    try source.requireContains("if count != 1:");
    try source.requireContains("def collect_issues(root: Path) -> list[str]:");
    try source.requireContains("helper_tests = bitmap_anchors.get(\"helper_test_anchors\")");
    try source.requireContains("if bitmap_anchors.get(field) != expected:");
    try source.requireContains("def write_sample_root(root: Path) -> None:");
    try source.requireContains("def run_self_test() -> None:");
    try source.requireContains("assert collect_issues(root) == []");
    try source.requireContains("assert f\"{MANIFEST_REL.as_posix()}:zero_bit_noop_anchor:drift\" in collect_issues(root)");
    try source.requireContains("assert f\"{FIXTURE_REL.as_posix()}:bitmap:partial_xor_masked_values:missing\" in collect_issues(root)");
    try source.requireContains("print(\"PHASE1_BITMAP_REVIEW_PACKET_SELF_TEST=pass\")");
    try source.requireContains("print(\"PHASE1_BITMAP_REVIEW_PACKET=fail\")");
    try source.requireContains("print(\"PHASE1_BITMAP_REVIEW_PACKET=pass\")");
    try source.requireContains("print(f\"PHASE1_BITMAP_REVIEW_PACKET_FIXTURE_KEY_COUNT={len(REQUIRED_FIXTURE_KEYS)}\")");
    try source.requireContains("print(f\"PHASE1_BITMAP_REVIEW_PACKET_HELPER_TEST_COUNT={len(REQUIRED_HELPER_TESTS)}\")");
    try source.requireBefore("if args.self_test:", "issues = collect_issues(repo_root(args.root))");
}
