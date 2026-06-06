const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOf(u8, haystack[offset..], needle)) |relative_index| {
        count += 1;
        offset += relative_index + needle.len;
    }
    return count;
}

fn expectOnce(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(haystack, needle));
}

test "phase 1 closure validator preserves delegated failure propagation" {
    const validator = try readRepoFile("scripts/zigux/validate-phase1-closure.py", 1024 * 1024);
    defer std.testing.allocator.free(validator);

    try expectContains(validator, "def run_checker(root: Path, script_rel: Path, label: str) -> list[str]:");
    try expectContains(validator, "proc = subprocess.run(");
    try expectContains(validator, "[sys.executable, str(root / script_rel), \"--root\", str(root)]");
    try expectContains(validator, "check=False");
    try expectContains(validator, "capture_output=True");
    try expectContains(validator, "text=True");
    try expectContains(validator, "if proc.returncode == 0:");
    try expectContains(validator, "return []");
    try expectContains(validator, "output = (proc.stdout + proc.stderr).splitlines() or [f\"{label}:checker_failed:returncode={proc.returncode}\"]");
    try expectContains(validator, "return [f\"delegated:{label}:{line}\" for line in output]");
}

test "phase 1 closure validator runs delegated checkers after packet-local checks" {
    const validator = try readRepoFile("scripts/zigux/validate-phase1-closure.py", 1024 * 1024);
    defer std.testing.allocator.free(validator);

    try expectContains(validator, "DELEGATED_CHECKERS = (");
    try expectContains(validator, "(STRING_REVIEW_CHECKER_REL, \"phase1-string-review-packet\")");
    try expectContains(validator, "(FIND_BIT_REVIEW_CHECKER_REL, \"phase1-find-bit-review-packet\")");
    try expectContains(validator, "(RBTREE_REVIEW_CHECKER_REL, \"phase1-rbtree-review-packet\")");
    try expectContains(validator, "(DIRECT_OWNER_CHECKER_REL, \"phase1-direct-owner-markers\")");
    try expectContains(validator, "(DIRECT_ANCHOR_MANIFEST_GATE_REL, \"phase1-direct-anchor-manifest-gate\")");
    try expectContains(validator, "(ROUTE_SUMMARY_CHECKER_REL, \"phase1-route-summary-counts\")");
    try expectContains(validator, "(FIND_BIT_BENCH_ANCHOR_CHECKER_REL, \"phase1-find-bit-bench-anchors\")");
    try expectContains(validator, "(BITMAP_DIRECT_ANCHOR_CHECKER_REL, \"phase1-bitmap-direct-anchors\")");
    try expectContains(validator, "(SHARED_REMINDER_CHECKER_REL, \"phase1-shared-reminder-packet\")");
    try expectContains(validator, "for script_rel, label in DELEGATED_CHECKERS:");
    try expectContains(validator, "failures.extend(run_checker(root, script_rel, label))");
    try expectBefore(validator, "failures.extend(require_expected_mapping", "for script_rel, label in DELEGATED_CHECKERS:");
}

test "phase 1 closure validator self-test matrix keeps delegated failure cases explicit" {
    const validator = try readRepoFile("scripts/zigux/validate-phase1-closure.py", 1024 * 1024);
    defer std.testing.allocator.free(validator);

    try expectOnce(validator, "(\"missing_string_checker\", lambda root: (root / STRING_REVIEW_CHECKER_REL).unlink())");
    try expectOnce(validator, "(\"failing_string_checker\", lambda root: make_checker_stub(root / STRING_REVIEW_CHECKER_REL, ok=False))");
    try expectOnce(validator, "(\"missing_find_bit_review_checker\", lambda root: (root / FIND_BIT_REVIEW_CHECKER_REL).unlink())");
    try expectOnce(validator, "(\"missing_rbtree_review_checker\", lambda root: (root / RBTREE_REVIEW_CHECKER_REL).unlink())");
    try expectOnce(validator, "(\"missing_find_bit_bench_anchor_checker\", lambda root: (root / FIND_BIT_BENCH_ANCHOR_CHECKER_REL).unlink())");
    try expectOnce(validator, "(\"failing_find_bit_bench_anchor_checker\", lambda root: make_checker_stub(root / FIND_BIT_BENCH_ANCHOR_CHECKER_REL, ok=False))");
    try expectOnce(validator, "(\"missing_bitmap_direct_anchor_checker\", lambda root: (root / BITMAP_DIRECT_ANCHOR_CHECKER_REL).unlink())");
    try expectOnce(validator, "(\"failing_bitmap_direct_anchor_checker\", lambda root: make_checker_stub(root / BITMAP_DIRECT_ANCHOR_CHECKER_REL, ok=False))");
    try expectOnce(validator, "(\"missing_direct_anchor_manifest_gate_checker\", lambda root: (root / DIRECT_ANCHOR_MANIFEST_GATE_REL).unlink())");
    try expectOnce(validator, "(\"failing_direct_anchor_manifest_gate_checker\", lambda root: make_checker_stub(root / DIRECT_ANCHOR_MANIFEST_GATE_REL, ok=False))");
    try expectContains(validator, "elif not failures:");
    try expectContains(validator, "print(f\"phase1-closure-self-test:{name}:expected_failure\")");
}
