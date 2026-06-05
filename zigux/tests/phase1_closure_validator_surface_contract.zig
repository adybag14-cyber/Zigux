const std = @import("std");

const read_limit = 512 * 1024;

const required_validator_paths = [_][]const u8{
    "PHASE1_CLOSURE_REL = Path(\"Documentation/zigux/phase1-closure.md\")",
    "PHASE1_LANE_NOTE_REL = Path(\"Documentation/zigux/phase1-host-helper-lane-sequencing.md\")",
    "DOCS_ROOT_REL = Path(\"Documentation/zigux/README.md\")",
    "REVIEW_CHECKLIST_REL = Path(\"Documentation/zigux/review-checklist.md\")",
    "SCRIPTS_README_REL = Path(\"scripts/zigux/README.md\")",
    "STRING_REVIEW_CHECKER_REL = Path(\"scripts/zigux/check-phase1-string-review-packet.py\")",
    "FIND_BIT_REVIEW_CHECKER_REL = Path(\"scripts/zigux/check-phase1-find-bit-review-packet.py\")",
    "RBTREE_REVIEW_CHECKER_REL = Path(\"scripts/zigux/check-phase1-rbtree-review-packet.py\")",
    "DIRECT_OWNER_CHECKER_REL = Path(\"scripts/zigux/check-phase1-direct-owner-markers.py\")",
    "DIRECT_ANCHOR_MANIFEST_GATE_REL = Path(\"scripts/zigux/check-phase1-direct-anchor-manifest-gate.py\")",
    "ROUTE_SUMMARY_CHECKER_REL = Path(\"scripts/zigux/check-phase1-route-summary-counts.py\")",
    "BENCH_CHECKER_REL = Path(\"scripts/zigux/check-phase1-bench.py\")",
    "FIND_BIT_BENCH_ANCHOR_CHECKER_REL = Path(\"scripts/zigux/check-phase1-find-bit-bench-anchors.py\")",
    "BITMAP_DIRECT_ANCHOR_CHECKER_REL = Path(\"scripts/zigux/check-phase1-bitmap-direct-anchors.py\")",
    "SHARED_REMINDER_CHECKER_REL = Path(\"scripts/zigux/check-phase1-shared-reminder-packet.py\")",
    "TESTS_BUILD_REL = Path(\"zigux/tests/build.zig\")",
    "PHASE1_HELPERS_REPLAY_REL = Path(\"zigux/tests/phase1_helpers.zig\")",
    "PHASE1_HELPERS_BUILD_REL = Path(\"zigux/tests/phase1_helpers_build.zig\")",
    "PHASE1_SMOKE_REL = Path(\"zigux/tests/phase1_host_tools_smoke.zig\")",
    "WORKFLOW_REL = Path(\".github/workflows/zigux-bootstrap.yml\")",
    "MANIFEST_REL = Path(\"zigux/tests/fixtures/phase1_helper_manifest.json\")",
    "ZIGUX_MAKEFILE_REL = Path(\"zigux/Makefile\")",
    "BITMAP_HELPER_REL = Path(\"tools/lib/bitmap.zig\")",
    "FIND_BIT_HELPER_REL = Path(\"tools/lib/find_bit.zig\")",
    "RBTREE_HELPER_REL = Path(\"tools/lib/rbtree.zig\")",
    "STRING_HELPER_REL = Path(\"tools/lib/string.zig\")",
};

const delegated_checkers = [_][]const u8{
    "(STRING_REVIEW_CHECKER_REL, \"phase1-string-review-packet\")",
    "(FIND_BIT_REVIEW_CHECKER_REL, \"phase1-find-bit-review-packet\")",
    "(RBTREE_REVIEW_CHECKER_REL, \"phase1-rbtree-review-packet\")",
    "(DIRECT_OWNER_CHECKER_REL, \"phase1-direct-owner-markers\")",
    "(DIRECT_ANCHOR_MANIFEST_GATE_REL, \"phase1-direct-anchor-manifest-gate\")",
    "(ROUTE_SUMMARY_CHECKER_REL, \"phase1-route-summary-counts\")",
    "(FIND_BIT_BENCH_ANCHOR_CHECKER_REL, \"phase1-find-bit-bench-anchors\")",
    "(BITMAP_DIRECT_ANCHOR_CHECKER_REL, \"phase1-bitmap-direct-anchors\")",
    "(SHARED_REMINDER_CHECKER_REL, \"phase1-shared-reminder-packet\")",
};

const expected_helpers = [_][]const u8{
    "tools/lib/argv_split.zig",
    "tools/lib/bitmap.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/string.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
};

const expected_makefile_markers = [_][]const u8{
    "\"phase2-toolchain:\"",
    "\"phase2-cross:\"",
    "\"phase3-validate:\"",
    "\"phase4-validate:\"",
    "\"phase6-validate:\"",
    "\"phase8-validate:\"",
    "\"phase12-validate:\"",
    "\"phase12-smoke:\"",
    "\"phase12-test:\"",
    "\"phase14-validate:\"",
};

const forbidden_makefile_markers = [_][]const u8{
    "\"phase1-validate:\"",
    "\"phase1-test:\"",
    "\"phase1-bench:\"",
    "\"phase1:\"",
};

fn readFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(read_limit),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "phase1 closure validator keeps the current required file surface explicit" {
    const validator = try readFile("scripts/zigux/validate-phase1-closure.py");
    defer std.testing.allocator.free(validator);

    try expectContains(validator, "REQUIRED_FILES = (");
    for (required_validator_paths) |path_marker| {
        try expectContains(validator, path_marker);
    }
    for (expected_helpers) |helper| {
        const marker = try std.fmt.allocPrint(std.testing.allocator, "\"{s}\"", .{helper});
        defer std.testing.allocator.free(marker);
        try expectContains(validator, marker);
    }
}

test "phase1 closure validator delegates to the shipped helper and reminder guards" {
    const validator = try readFile("scripts/zigux/validate-phase1-closure.py");
    defer std.testing.allocator.free(validator);

    try expectContains(validator, "DELEGATED_CHECKERS = (");
    try expectContains(validator, "def run_checker(root: Path, script_rel: Path, label: str) -> list[str]:");
    try expectContains(validator, "[sys.executable, str(root / script_rel), \"--root\", str(root)]");
    try expectContains(validator, "for script_rel, label in DELEGATED_CHECKERS:");
    for (delegated_checkers) |checker_marker| {
        try expectContains(validator, checker_marker);
    }
}

test "phase1 closure validator preserves current route and manifest policy" {
    const validator = try readFile("scripts/zigux/validate-phase1-closure.py");
    defer std.testing.allocator.free(validator);

    try expectContains(validator, "EXPECTED_MAKEFILE_MARKERS = (");
    for (expected_makefile_markers) |route_marker| {
        try expectContains(validator, route_marker);
    }
    try expectContains(validator, "FORBIDDEN_MAKEFILE_MARKERS = (");
    for (forbidden_makefile_markers) |route_marker| {
        try expectContains(validator, route_marker);
    }
    try expectContains(validator, "collect_duplicate_json_key_paths(manifest)");
    try expectContains(validator, "lane_sequencing.shared_replay_parked_helpers");
    try expectContains(validator, "review_anchors.tools/lib/bitmap.zig");
    try expectContains(validator, "review_anchors.tools/lib/find_bit.zig");
    try expectContains(validator, "review_anchors.tools/lib/rbtree.zig");
    try expectContains(validator, "review_anchors.tools/lib/string.zig");
}

test "phase1 closure note and manifest expose the validator-surface next step" {
    const closure = try readFile("Documentation/zigux/phase1-closure.md");
    defer std.testing.allocator.free(closure);
    const lane_note = try readFile("Documentation/zigux/phase1-host-helper-lane-sequencing.md");
    defer std.testing.allocator.free(lane_note);
    const manifest = try readFile("zigux/tests/fixtures/phase1_helper_manifest.json");
    defer std.testing.allocator.free(manifest);

    try expectContains(closure, "PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py");
    try expectContains(closure, "PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py");
    try expectContains(closure, "PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker against the restored closure note, the closure validator, the shared tests-root smoke route, and the helper-specific next_safe_step_note entries in the committed manifest rather than widening back into the older validator-first or replay-side closure stack.");
    try expectContains(lane_note, "PHASE1_DIRECT_OWNER_SHARED_REMINDER_NEXT_STEP=leave the shared bench-checker wording and shared-reminder checker packet parked");
    try expectContains(manifest, "\"lane_sequencing\": {");
    try expectContains(manifest, "\"review_anchors\": {");
    try expectContains(manifest, "\"status\": \"closed\"");
    try expectNotContains(closure, "PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master");
}
