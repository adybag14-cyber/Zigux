const std = @import("std");

const max_file_size = 512 * 1024;

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        allocator,
        .limited(max_file_size),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectMissing(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "closure validator keeps the helper review checker roster explicit" {
    const allocator = std.testing.allocator;
    const validator = try readRepoFile(allocator, "scripts/zigux/validate-phase1-closure.py");
    defer allocator.free(validator);

    const required_constants = [_][]const u8{
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
    };

    for (required_constants) |marker| {
        try expectContains(validator, marker);
    }

    const required_file_roster = std.mem.sliceTo(validator[std.mem.indexOf(u8, validator, "REQUIRED_FILES = (").?..], ')');
    const required_file_markers = [_][]const u8{
        "STRING_REVIEW_CHECKER_REL",
        "FIND_BIT_REVIEW_CHECKER_REL",
        "RBTREE_REVIEW_CHECKER_REL",
        "DIRECT_OWNER_CHECKER_REL",
        "DIRECT_ANCHOR_MANIFEST_GATE_REL",
        "ROUTE_SUMMARY_CHECKER_REL",
        "BENCH_CHECKER_REL",
        "FIND_BIT_BENCH_ANCHOR_CHECKER_REL",
        "BITMAP_DIRECT_ANCHOR_CHECKER_REL",
        "SHARED_REMINDER_CHECKER_REL",
    };

    for (required_file_markers) |marker| {
        try expectContains(required_file_roster, marker);
    }
}

test "closure note mirrors validator checker commands instead of stale phase1 routes" {
    const allocator = std.testing.allocator;
    const closure = try readRepoFile(allocator, "Documentation/zigux/phase1-closure.md");
    defer allocator.free(closure);
    const validator = try readRepoFile(allocator, "scripts/zigux/validate-phase1-closure.py");
    defer allocator.free(validator);

    const closure_command_markers = [_][]const u8{
        "PHASE1_STRING_REVIEW_GUARD=python3 scripts/zigux/check-phase1-string-review-packet.py",
        "PHASE1_FIND_BIT_REVIEW_GUARD=python3 scripts/zigux/check-phase1-find-bit-review-packet.py",
        "PHASE1_RBTREE_REVIEW_GUARD=python3 scripts/zigux/check-phase1-rbtree-review-packet.py",
        "PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
        "PHASE1_FIND_BIT_BENCH_ANCHOR_GUARD=python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py",
        "PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py",
        "PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py",
        "PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    };

    for (closure_command_markers) |marker| {
        try expectContains(closure, marker);
    }

    const validator_path_markers = [_][]const u8{
        "scripts/zigux/check-phase1-string-review-packet.py",
        "scripts/zigux/check-phase1-find-bit-review-packet.py",
        "scripts/zigux/check-phase1-rbtree-review-packet.py",
        "scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
        "scripts/zigux/check-phase1-find-bit-bench-anchors.py",
        "scripts/zigux/check-phase1-route-summary-counts.py",
        "zigux/tests/build.zig",
    };

    for (validator_path_markers) |marker| {
        try expectContains(validator, marker);
    }
}

test "validator helper-family split matches the Phase 1 closure posture" {
    const allocator = std.testing.allocator;
    const closure = try readRepoFile(allocator, "Documentation/zigux/phase1-closure.md");
    defer allocator.free(closure);
    const validator = try readRepoFile(allocator, "scripts/zigux/validate-phase1-closure.py");
    defer allocator.free(validator);

    const shared_replay_helpers = [_][]const u8{
        "tools/lib/argv_split.zig",
        "tools/lib/cmdline.zig",
        "tools/lib/ctype.zig",
        "tools/lib/hweight.zig",
        "tools/lib/list_sort.zig",
        "tools/lib/slab.zig",
        "tools/lib/str_error_r.zig",
        "tools/lib/vsprintf.zig",
        "tools/lib/zalloc.zig",
    };
    const direct_anchor_helpers = [_][]const u8{
        "tools/lib/bitmap.zig",
        "tools/lib/find_bit.zig",
        "tools/lib/rbtree.zig",
        "tools/lib/string.zig",
    };

    try expectContains(validator, "EXPECTED_SHARED_REPLAY_PARKED_HELPERS = [");
    for (shared_replay_helpers) |helper| {
        try expectContains(validator, helper);
    }

    try expectContains(validator, "EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [");
    for (direct_anchor_helpers) |helper| {
        try expectContains(validator, helper);
    }

    try expectContains(closure, "`PHASE1_HELPER_COUNT=13`");
    try expectContains(closure, "bitmap, find_bit, rbtree, and string");
    try expectContains(closure, "sync one shared reminder surface or one helper-family tie-breaker");
}

test "stale closure states and old Phase 1 Makefile routes stay forbidden" {
    const allocator = std.testing.allocator;
    const closure = try readRepoFile(allocator, "Documentation/zigux/phase1-closure.md");
    defer allocator.free(closure);
    const validator = try readRepoFile(allocator, "scripts/zigux/validate-phase1-closure.py");
    defer allocator.free(validator);

    try expectContains(validator, "FORBIDDEN_CLOSURE_MARKERS = {");
    try expectContains(validator, "`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`");
    try expectContains(validator, "`PHASE1_NEXT_SAFE_STEP=restore the missing phase1 closure note first`");
    try expectContains(validator, "FORBIDDEN_MAKEFILE_MARKERS = (");
    try expectContains(validator, "\"phase1-validate:\"");
    try expectContains(validator, "\"phase1-test:\"");
    try expectContains(validator, "\"phase1-bench:\"");
    try expectContains(validator, "\"phase1:\"");

    try expectMissing(closure, "`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`");
    try expectMissing(closure, "`PHASE1_NEXT_SAFE_STEP=restore the missing phase1 closure note first`");
    try expectContains(closure, "`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`");
}
