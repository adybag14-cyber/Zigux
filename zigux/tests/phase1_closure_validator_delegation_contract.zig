const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectAbsent(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
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

fn expectOrderedMarkers(haystack: []const u8, markers: []const []const u8) !void {
    var previous_end: usize = 0;
    for (markers) |marker| {
        const relative_index = std.mem.indexOf(u8, haystack[previous_end..], marker) orelse return error.MissingOrderedMarker;
        previous_end += relative_index + marker.len;
    }
}

fn sliceBetween(haystack: []const u8, start_marker: []const u8, end_marker: []const u8) ![]const u8 {
    const start = std.mem.indexOf(u8, haystack, start_marker) orelse return error.MissingStartMarker;
    const body_start = start + start_marker.len;
    const relative_end = std.mem.indexOf(u8, haystack[body_start..], end_marker) orelse return error.MissingEndMarker;
    return haystack[body_start .. body_start + relative_end];
}

test "phase 1 closure validator keeps delegated checker roster explicit" {
    const validator = try readRepoFile("scripts/zigux/validate-phase1-closure.py", 512 * 1024);
    defer std.testing.allocator.free(validator);

    if (std.mem.indexOf(u8, validator, "DELEGATED_CHECKERS = (") != null) {
        try expectContains(validator, "DELEGATED_CHECKERS = (");
        try expectContains(validator, "run_checker(root, script_rel, label)");
        try expectContains(validator, "STRING_REVIEW_CHECKER_REL = Path(\"scripts/zigux/check-phase1-string-review-packet.py\")");
        try expectContains(validator, "FIND_BIT_REVIEW_CHECKER_REL = Path(\"scripts/zigux/check-phase1-find-bit-review-packet.py\")");
        try expectContains(validator, "RBTREE_REVIEW_CHECKER_REL = Path(\"scripts/zigux/check-phase1-rbtree-review-packet.py\")");
        try expectContains(validator, "DIRECT_OWNER_CHECKER_REL = Path(\"scripts/zigux/check-phase1-direct-owner-markers.py\")");
        try expectContains(validator, "DIRECT_ANCHOR_MANIFEST_GATE_REL = Path(\"scripts/zigux/check-phase1-direct-anchor-manifest-gate.py\")");
        try expectContains(validator, "BENCH_CHECKER_REL = Path(\"scripts/zigux/check-phase1-bench.py\")");
        try expectContains(validator, "FIND_BIT_BENCH_ANCHOR_CHECKER_REL = Path(\"scripts/zigux/check-phase1-find-bit-bench-anchors.py\")");
        try expectContains(validator, "BITMAP_DIRECT_ANCHOR_CHECKER_REL = Path(\"scripts/zigux/check-phase1-bitmap-direct-anchors.py\")");
        try expectBefore(validator, "STRING_REVIEW_CHECKER_REL", "DIRECT_ANCHOR_MANIFEST_GATE_REL");
        try expectBefore(validator, "FIND_BIT_REVIEW_CHECKER_REL", "DIRECT_ANCHOR_MANIFEST_GATE_REL");
        try expectBefore(validator, "RBTREE_REVIEW_CHECKER_REL", "DIRECT_ANCHOR_MANIFEST_GATE_REL");
        return;
    }

    try expectContains(validator, "\"scripts/zigux/validate-phase1-closure.py\"");
    try expectContains(validator, "\"scripts/zigux/check-phase1-bench.py\"");
    try expectContains(validator, "\"scripts/zigux/check-phase1-direct-owner-markers.py\"");
    try expectContains(validator, "PHASE1_CLOSURE_GATE=python3 scripts/zigux/validate-phase1-closure.py");
}

test "phase 1 closure validator delegation tuple is exact and ordered" {
    const validator = try readRepoFile("scripts/zigux/validate-phase1-closure.py", 512 * 1024);
    defer std.testing.allocator.free(validator);

    const delegated = try sliceBetween(
        validator,
        "DELEGATED_CHECKERS = (\n",
        ")\n\n\ndef repo_root",
    );

    const expected = [_][]const u8{
        "(STRING_REVIEW_CHECKER_REL, \"phase1-string-review-packet\"),",
        "(FIND_BIT_REVIEW_CHECKER_REL, \"phase1-find-bit-review-packet\"),",
        "(RBTREE_REVIEW_CHECKER_REL, \"phase1-rbtree-review-packet\"),",
        "(DIRECT_OWNER_CHECKER_REL, \"phase1-direct-owner-markers\"),",
        "(DIRECT_ANCHOR_MANIFEST_GATE_REL, \"phase1-direct-anchor-manifest-gate\"),",
        "(ROUTE_SUMMARY_CHECKER_REL, \"phase1-route-summary-counts\"),",
        "(FIND_BIT_BENCH_ANCHOR_CHECKER_REL, \"phase1-find-bit-bench-anchors\"),",
        "(BITMAP_DIRECT_ANCHOR_CHECKER_REL, \"phase1-bitmap-direct-anchors\"),",
        "(SHARED_REMINDER_CHECKER_REL, \"phase1-shared-reminder-packet\"),",
    };
    try expectOrderedMarkers(delegated, &expected);
    for (expected) |marker| {
        try expectOnce(delegated, marker);
    }

    try std.testing.expectEqual(@as(usize, expected.len), countOccurrences(delegated, "phase1-"));
    try expectAbsent(delegated, "BENCH_CHECKER_REL");
    try expectAbsent(delegated, "validate-phase1-closure.py");
}

test "phase 1 closure note stays tied to the narrow validator route" {
    const closure_note = try readRepoFile("Documentation/zigux/phase1-closure.md", 256 * 1024);
    defer std.testing.allocator.free(closure_note);

    if (std.mem.indexOf(u8, closure_note, "PHASE1_CLOSURE_RESTORE_STATE=docs_plus_validator") != null) {
        try expectOnce(closure_note, "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`");
        try expectOnce(closure_note, "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`");
        try expectContains(closure_note, "`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`");
        try expectContains(closure_note, "`PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py");
        try expectContains(closure_note, "`PHASE1_STRING_REVIEW_GUARD=python3 scripts/zigux/check-phase1-string-review-packet.py");
        try expectContains(closure_note, "`PHASE1_FIND_BIT_REVIEW_GUARD=python3 scripts/zigux/check-phase1-find-bit-review-packet.py");
        try expectContains(closure_note, "`PHASE1_RBTREE_REVIEW_GUARD=python3 scripts/zigux/check-phase1-rbtree-review-packet.py");
        try expectAbsent(closure_note, "`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`");
        try expectAbsent(closure_note, "`PHASE1_NEXT_SAFE_STEP=restore the missing phase1 closure note first`");
        return;
    }

    try expectContains(closure_note, "PHASE1_STATUS=closed");
    try expectContains(closure_note, "PHASE1_CLOSURE_GATE=python3 scripts/zigux/validate-phase1-closure.py");
    try expectContains(closure_note, "PHASE1_UNIT_GATE=zig build test --build-file zigux/tests/build.zig");
    try expectContains(closure_note, "PHASE1_BENCH_GATE=zig build bench --build-file zigux/tests/build.zig");
}

test "phase 1 workflow runs delegated checker packets before closure validation" {
    const workflow = try readRepoFile(".github/workflows/zigux-bootstrap.yml", 1024 * 1024);
    defer std.testing.allocator.free(workflow);

    const ordered = [_][]const u8{
        "python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
        "python3 scripts/zigux/check-phase1-direct-owner-markers.py",
        "python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test",
        "python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
        "python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
        "python3 scripts/zigux/check-phase1-string-review-packet.py",
        "python3 scripts/zigux/check-phase1-find-bit-review-packet.py --self-test",
        "python3 scripts/zigux/check-phase1-find-bit-review-packet.py",
        "python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py --self-test",
        "python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py",
        "python3 scripts/zigux/check-phase1-rbtree-review-packet.py --self-test",
        "python3 scripts/zigux/check-phase1-rbtree-review-packet.py",
        "python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
        "python3 scripts/zigux/check-phase1-route-summary-counts.py",
        "python3 scripts/zigux/check-phase1-bench.py --self-test",
        "python3 scripts/zigux/check-phase1-bench.py",
        "python3 scripts/zigux/check-phase1-bench-live-check-workflow.py --self-test",
        "python3 scripts/zigux/check-phase1-bench-live-check-workflow.py",
        "python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test",
        "python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py",
        "python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
        "python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
        "python3 scripts/zigux/validate-phase1-closure.py --self-test",
        "python3 scripts/zigux/validate-phase1-closure.py",
    };
    try expectOrderedMarkers(workflow, &ordered);
}

test "phase 1 tests root exposes the shared smoke route used by closure validation" {
    const build_file = try readRepoFile("zigux/tests/build.zig", 1024 * 1024);
    defer std.testing.allocator.free(build_file);

    if (std.mem.indexOf(u8, build_file, "phase1-host-tools-smoke") != null) {
        try expectContains(build_file, ".name = \"phase1-host-tools-smoke\"");
        try expectContains(build_file, "b.step(");
        try expectContains(build_file, "\"phase1-host-tools-smoke\"");
        try expectContains(build_file, "\"Run the shared Phase 1 host-tools smoke anchor from zigux/tests\"");
        try expectContains(build_file, "phase1_host_tools_smoke.step");
        return;
    }

    try expectContains(build_file, ".root_source_file = b.path(\"phase1_helpers.zig\")");
    try expectContains(build_file, ".root_source_file = b.path(\"phase1_bench.zig\")");
    try expectContains(build_file, "b.step(\"test\", \"Run Phase 1 helper tests\")");
    try expectContains(build_file, "b.step(\"bench\", \"Run Phase 1 helper benchmark smoke\")");
}
