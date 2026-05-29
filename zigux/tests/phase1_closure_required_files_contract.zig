const std = @import("std");

const ValidatorFile = struct {
    const_name: []const u8,
    path: []const u8,
};

const required_validator_files = [_]ValidatorFile{
    .{ .const_name = "PHASE1_CLOSURE_REL", .path = "Documentation/zigux/phase1-closure.md" },
    .{ .const_name = "PHASE1_LANE_NOTE_REL", .path = "Documentation/zigux/phase1-host-helper-lane-sequencing.md" },
    .{ .const_name = "DOCS_ROOT_REL", .path = "Documentation/zigux/README.md" },
    .{ .const_name = "REVIEW_CHECKLIST_REL", .path = "Documentation/zigux/review-checklist.md" },
    .{ .const_name = "SCRIPTS_README_REL", .path = "scripts/zigux/README.md" },
    .{ .const_name = "STRING_REVIEW_CHECKER_REL", .path = "scripts/zigux/check-phase1-string-review-packet.py" },
    .{ .const_name = "FIND_BIT_REVIEW_CHECKER_REL", .path = "scripts/zigux/check-phase1-find-bit-review-packet.py" },
    .{ .const_name = "RBTREE_REVIEW_CHECKER_REL", .path = "scripts/zigux/check-phase1-rbtree-review-packet.py" },
    .{ .const_name = "DIRECT_OWNER_CHECKER_REL", .path = "scripts/zigux/check-phase1-direct-owner-markers.py" },
    .{ .const_name = "DIRECT_ANCHOR_MANIFEST_GATE_REL", .path = "scripts/zigux/check-phase1-direct-anchor-manifest-gate.py" },
    .{ .const_name = "ROUTE_SUMMARY_CHECKER_REL", .path = "scripts/zigux/check-phase1-route-summary-counts.py" },
    .{ .const_name = "BENCH_CHECKER_REL", .path = "scripts/zigux/check-phase1-bench.py" },
    .{ .const_name = "FIND_BIT_BENCH_ANCHOR_CHECKER_REL", .path = "scripts/zigux/check-phase1-find-bit-bench-anchors.py" },
    .{ .const_name = "BITMAP_DIRECT_ANCHOR_CHECKER_REL", .path = "scripts/zigux/check-phase1-bitmap-direct-anchors.py" },
    .{ .const_name = "SHARED_REMINDER_CHECKER_REL", .path = "scripts/zigux/check-phase1-shared-reminder-packet.py" },
    .{ .const_name = "TESTS_README_REL", .path = "zigux/tests/README.md" },
    .{ .const_name = "TESTS_BUILD_REL", .path = "zigux/tests/build.zig" },
    .{ .const_name = "PHASE1_HELPERS_REPLAY_REL", .path = "zigux/tests/phase1_helpers.zig" },
    .{ .const_name = "PHASE1_HELPERS_BUILD_REL", .path = "zigux/tests/phase1_helpers_build.zig" },
    .{ .const_name = "PHASE1_SMOKE_REL", .path = "zigux/tests/phase1_host_tools_smoke.zig" },
    .{ .const_name = "WORKFLOW_REL", .path = ".github/workflows/zigux-bootstrap.yml" },
    .{ .const_name = "MANIFEST_REL", .path = "zigux/tests/fixtures/phase1_helper_manifest.json" },
    .{ .const_name = "ZIGUX_MAKEFILE_REL", .path = "zigux/Makefile" },
    .{ .const_name = "BITMAP_HELPER_REL", .path = "tools/lib/bitmap.zig" },
    .{ .const_name = "FIND_BIT_HELPER_REL", .path = "tools/lib/find_bit.zig" },
    .{ .const_name = "RBTREE_HELPER_REL", .path = "tools/lib/rbtree.zig" },
    .{ .const_name = "STRING_HELPER_REL", .path = "tools/lib/string.zig" },
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        allocator,
        .limited(256 * 1024),
    );
}

test "phase1 closure validator keeps the full required-file inventory explicit" {
    const closure_validator = try readRepoFile(std.testing.allocator, "scripts/zigux/validate-phase1-closure.py");
    defer std.testing.allocator.free(closure_validator);

    try expectContains(closure_validator, "REQUIRED_FILES = (");

    inline for (required_validator_files) |file| {
        const declaration = file.const_name ++ " = Path(\"" ++ file.path ++ "\")";
        try expectContains(closure_validator, declaration);
        try expectContains(closure_validator, "    " ++ file.const_name ++ ",");
    }
}

test "phase1 closure note keeps the user-facing authority routes visible" {
    const closure_note = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase1-closure.md");
    defer std.testing.allocator.free(closure_note);

    const markers = [_][]const u8{
        "`PHASE1_STATUS=parked`",
        "`PHASE1_CLOSURE_RESTORE_STATE=docs_plus_validator`",
        "`PHASE1_HELPER_COUNT=13`",
        "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
        "`PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",
        "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        "`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`",
        "`PHASE1_STRING_REVIEW_GUARD=python3 scripts/zigux/check-phase1-string-review-packet.py exact-checks",
        "`PHASE1_FIND_BIT_BENCH_ANCHOR_GUARD=python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py",
        "`PHASE1_FIND_BIT_REVIEW_GUARD=python3 scripts/zigux/check-phase1-find-bit-review-packet.py exact-checks",
        "`PHASE1_RBTREE_REVIEW_GUARD=python3 scripts/zigux/check-phase1-rbtree-review-packet.py exact-checks",
        "`PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py exact-checks",
        "`PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker",
    };

    for (markers) |marker| {
        try expectContains(closure_note, marker);
    }
}

test "phase1 closure inventory keeps direct helpers separate from shared replay" {
    const closure_note = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase1-closure.md");
    defer std.testing.allocator.free(closure_note);
    const closure_validator = try readRepoFile(std.testing.allocator, "scripts/zigux/validate-phase1-closure.py");
    defer std.testing.allocator.free(closure_validator);

    try expectBefore(
        closure_validator,
        "EXPECTED_SHARED_REPLAY_PARKED_HELPERS = [",
        "EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [",
    );

    const shared_helpers = [_][]const u8{
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
    const direct_helpers = [_][]const u8{
        "tools/lib/bitmap.zig",
        "tools/lib/find_bit.zig",
        "tools/lib/rbtree.zig",
        "tools/lib/string.zig",
    };

    inline for (shared_helpers) |helper| {
        try expectContains(closure_validator, "EXPECTED_SHARED_REPLAY_PARKED_HELPERS = [");
        try expectContains(closure_validator, "    \"" ++ helper ++ "\",");
    }
    inline for (direct_helpers) |helper| {
        try expectContains(closure_validator, "EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [");
        try expectContains(closure_validator, "    \"" ++ helper ++ "\",");
    }

    try expectContains(closure_validator, "Do not reopen Phase 1 by batching helpers across those two sets in one lane");
    try expectContains(closure_note, "do not widen this helper-local reminder into older closure-side validator names by default");
}
