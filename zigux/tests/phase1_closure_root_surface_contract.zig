const std = @import("std");

const validator_path = @import("config").validator_path;

const RequiredMarker = struct {
    label: []const u8,
    text: []const u8,
};

const required_file_markers = [_]RequiredMarker{
    .{ .label = "closure note", .text = "PHASE1_CLOSURE_REL = Path(\"Documentation/zigux/phase1-closure.md\")" },
    .{ .label = "lane note", .text = "PHASE1_LANE_NOTE_REL = Path(\"Documentation/zigux/phase1-host-helper-lane-sequencing.md\")" },
    .{ .label = "string review checker", .text = "STRING_REVIEW_CHECKER_REL = Path(\"scripts/zigux/check-phase1-string-review-packet.py\")" },
    .{ .label = "find_bit review checker", .text = "FIND_BIT_REVIEW_CHECKER_REL = Path(\"scripts/zigux/check-phase1-find-bit-review-packet.py\")" },
    .{ .label = "rbtree review checker", .text = "RBTREE_REVIEW_CHECKER_REL = Path(\"scripts/zigux/check-phase1-rbtree-review-packet.py\")" },
    .{ .label = "direct owner checker", .text = "DIRECT_OWNER_CHECKER_REL = Path(\"scripts/zigux/check-phase1-direct-owner-markers.py\")" },
    .{ .label = "direct anchor manifest gate", .text = "DIRECT_ANCHOR_MANIFEST_GATE_REL = Path(\"scripts/zigux/check-phase1-direct-anchor-manifest-gate.py\")" },
    .{ .label = "route summary checker", .text = "ROUTE_SUMMARY_CHECKER_REL = Path(\"scripts/zigux/check-phase1-route-summary-counts.py\")" },
    .{ .label = "bench checker", .text = "BENCH_CHECKER_REL = Path(\"scripts/zigux/check-phase1-bench.py\")" },
    .{ .label = "find_bit bench anchor checker", .text = "FIND_BIT_BENCH_ANCHOR_CHECKER_REL = Path(\"scripts/zigux/check-phase1-find-bit-bench-anchors.py\")" },
    .{ .label = "bitmap direct anchor checker", .text = "BITMAP_DIRECT_ANCHOR_CHECKER_REL = Path(\"scripts/zigux/check-phase1-bitmap-direct-anchors.py\")" },
    .{ .label = "shared reminder checker", .text = "SHARED_REMINDER_CHECKER_REL = Path(\"scripts/zigux/check-phase1-shared-reminder-packet.py\")" },
    .{ .label = "tests build route", .text = "TESTS_BUILD_REL = Path(\"zigux/tests/build.zig\")" },
    .{ .label = "phase1 smoke route", .text = "PHASE1_SMOKE_REL = Path(\"zigux/tests/phase1_host_tools_smoke.zig\")" },
    .{ .label = "manifest", .text = "MANIFEST_REL = Path(\"zigux/tests/fixtures/phase1_helper_manifest.json\")" },
    .{ .label = "makefile", .text = "ZIGUX_MAKEFILE_REL = Path(\"zigux/Makefile\")" },
};

const delegated_checker_markers = [_][]const u8{
    "(STRING_REVIEW_CHECKER_REL, \"string_review\")",
    "(FIND_BIT_REVIEW_CHECKER_REL, \"find_bit_review\")",
    "(RBTREE_REVIEW_CHECKER_REL, \"rbtree_review\")",
    "(DIRECT_OWNER_CHECKER_REL, \"direct_owner\")",
    "(DIRECT_ANCHOR_MANIFEST_GATE_REL, \"direct_anchor_manifest_gate\")",
    "(FIND_BIT_BENCH_ANCHOR_CHECKER_REL, \"find_bit_bench_anchor\")",
    "(BITMAP_DIRECT_ANCHOR_CHECKER_REL, \"bitmap_direct_anchor\")",
    "(SHARED_REMINDER_CHECKER_REL, \"shared_reminder\")",
    "(ROUTE_SUMMARY_CHECKER_REL, \"route_summary\")",
    "(BENCH_CHECKER_REL, \"bench\")",
};

fn loadValidatorSource(allocator: std.mem.Allocator) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, validator_path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

test "phase1 closure validator keeps root override and pass-mode outputs" {
    const source = try loadValidatorSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try expectContains(source, "DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent");
    try expectContains(source, "def repo_root(root: str | None) -> Path:");
    try expectContains(source, "return Path(root).resolve() if root else DEFAULT_ROOT.resolve()");
    try expectContains(source, "parser.add_argument(\"--root\", help=\"override the repository root for validation\")");
    try expectContains(source, "failures = collect_failures(repo_root(args.root))");
    try expectContains(source, "print(\"PHASE1_CLOSURE_VALIDATION=pass\")");
    try expectContains(source, "print(\"PHASE1_CLOSURE_MODE=current-master-safe\")");
    try expectNotContains(source, "PHASE1_CLOSURE_MODE=validator-first");
}

test "phase1 closure validator required files cover the live closure surface" {
    const source = try loadValidatorSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try expectContains(source, "REQUIRED_FILES = (");
    try expectContains(source, "failures = [f\"missing_file:{path.as_posix()}\" for path in REQUIRED_FILES if not (root / path).is_file()]");
    try expectBefore(source, "if failures:\n        return failures", "closure_text = load_text(root, PHASE1_CLOSURE_REL)");

    inline for (required_file_markers) |marker| {
        _ = marker.label;
        try expectContains(source, marker.text);
    }
}

test "phase1 closure validator delegates through the current hardening roster" {
    const source = try loadValidatorSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try expectContains(source, "DELEGATED_CHECKERS = (");
    try expectContains(source, "def run_checker(root: Path, script_rel: Path, label: str) -> list[str]:");
    try expectContains(source, "[sys.executable, str(root / script_rel), \"--root\", str(root)]");
    try expectContains(source, "for script_rel, label in DELEGATED_CHECKERS:");
    try expectContains(source, "failures.extend(run_checker(root, script_rel, label))");

    inline for (delegated_checker_markers) |marker| {
        try expectContains(source, marker);
    }
}

test "phase1 closure validator self-test fixture exercises root-surface failures" {
    const source = try loadValidatorSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try expectContains(source, "def make_fixture_tree(root: Path) -> None:");
    try expectContains(source, "for relative_path in REQUIRED_FILES:");
    try expectContains(source, "write_text(root / relative_path, f\"fixture for {relative_path.as_posix()}\\n\")");
    try expectContains(source, "for checker_rel, _ in DELEGATED_CHECKERS:");
    try expectContains(source, "make_checker_stub(root / checker_rel)");
    try expectContains(source, "(\"missing_string_checker\", lambda root: (root / STRING_REVIEW_CHECKER_REL).unlink())");
    try expectContains(source, "(\"missing_find_bit_review_checker\", lambda root: (root / FIND_BIT_REVIEW_CHECKER_REL).unlink())");
    try expectContains(source, "(\"missing_rbtree_review_checker\", lambda root: (root / RBTREE_REVIEW_CHECKER_REL).unlink())");
    try expectContains(source, "(\"missing_bitmap_direct_anchor_checker\", lambda root: (root / BITMAP_DIRECT_ANCHOR_CHECKER_REL).unlink())");
    try expectContains(source, "print(\"PHASE1_CLOSURE_SELF_TEST=pass\")");
}
