const std = @import("std");

const alignment_checker_packet =
    \\DOCS_ROOT_README = ROOT / "Documentation" / "zigux" / "README.md"
    \\PHASE2_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
    \\REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
    \\TESTS_README = ROOT / "zigux" / "tests" / "README.md"
    \\SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
    \\MAKEFILE = ROOT / "zigux" / "Makefile"
    \\TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
    \\TOOLCHAIN_PINNING = ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pinning.py"
    \\TESTS_ALIGNMENT = ROOT / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py"
    \\CROSS_TARGETS = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"
    \\raise SystemExit(f"required file missing: {path}") from exc
    \\except FileNotFoundError as exc:
    \\for path in (
    \\    DOCS_ROOT_README,
    \\    PHASE2_NOTES,
    \\    REVIEW_CHECKLIST,
    \\    TESTS_README,
    \\    SCRIPTS_README,
    \\    MAKEFILE,
    \\    TOOLCHAIN_POLICY,
    \\    TOOLCHAIN_PINNING,
    \\    TESTS_ALIGNMENT,
    \\    CROSS_TARGETS,
    \\):
    \\resolve_path(root, path).unlink()
    \\assert "required file missing" in str(exc)
    \\raise AssertionError(f"missing file did not abort: {path}")
    \\PHASE2_CROSS_ALIGNMENT_SELF_TEST=pass
    \\PHASE2_CROSS_ALIGNMENT_SELF_TEST_CASE_COUNT
;

const fixture_packet =
    \\"route": "make -C zigux phase2-cross",
    \\"target": "x86_64-linux",
    \\"validation_mode": "archive_required",
    \\"target": "aarch64-linux",
    \\"validation_mode": "route_contract_only",
;

fn contains(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(contains(haystack, needle));
}

fn expectOrdered(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

test "alignment checker fail-closes on missing repo-root inputs" {
    const required_inputs = [_][]const u8{
        "DOCS_ROOT_README",
        "PHASE2_NOTES",
        "REVIEW_CHECKLIST",
        "TESTS_README",
        "SCRIPTS_README",
        "MAKEFILE",
        "TOOLCHAIN_POLICY",
        "TOOLCHAIN_PINNING",
        "TESTS_ALIGNMENT",
        "CROSS_TARGETS",
    };

    for (required_inputs) |name| {
        try expectContains(alignment_checker_packet, name);
    }
    try expectContains(alignment_checker_packet, "raise SystemExit(f\"required file missing: {path}\") from exc");
    try expectContains(alignment_checker_packet, "assert \"required file missing\" in str(exc)");
}

test "alignment self-test deletes every primary input in its missing-file sweep" {
    try expectContains(alignment_checker_packet, "for path in (");
    try expectContains(alignment_checker_packet, "resolve_path(root, path).unlink()");
    try expectContains(alignment_checker_packet, "raise AssertionError(f\"missing file did not abort: {path}\")");

    try expectOrdered(alignment_checker_packet, "DOCS_ROOT_README,", "PHASE2_NOTES,");
    try expectOrdered(alignment_checker_packet, "PHASE2_NOTES,", "REVIEW_CHECKLIST,");
    try expectOrdered(alignment_checker_packet, "TOOLCHAIN_PINNING,", "TESTS_ALIGNMENT,");
    try expectOrdered(alignment_checker_packet, "TESTS_ALIGNMENT,", "CROSS_TARGETS,");
}

test "missing-input guard stays tied to current cross fixture boundary" {
    try expectContains(fixture_packet, "\"route\": \"make -C zigux phase2-cross\"");
    try expectContains(fixture_packet, "\"target\": \"x86_64-linux\"");
    try expectContains(fixture_packet, "\"validation_mode\": \"archive_required\"");
    try expectContains(fixture_packet, "\"target\": \"aarch64-linux\"");
    try expectContains(fixture_packet, "\"validation_mode\": \"route_contract_only\"");
    try std.testing.expect(!contains(fixture_packet, "riscv64-linux"));
}

test "public self-test output remains visible after missing-file coverage" {
    try expectContains(alignment_checker_packet, "PHASE2_CROSS_ALIGNMENT_SELF_TEST=pass");
    try expectContains(alignment_checker_packet, "PHASE2_CROSS_ALIGNMENT_SELF_TEST_CASE_COUNT");
    try expectContains(alignment_checker_packet, "except FileNotFoundError as exc:");
}
