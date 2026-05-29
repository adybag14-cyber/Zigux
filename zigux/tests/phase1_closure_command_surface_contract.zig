const std = @import("std");
const testing = std.testing;

const ClosureCommand = struct {
    marker: []const u8,
    command: []const u8,
};

const closure_commands = [_]ClosureCommand{
    .{
        .marker = "PHASE1_CLOSURE_VALIDATOR=",
        .command = "python3 scripts/zigux/validate-phase1-closure.py",
    },
    .{
        .marker = "PHASE1_ROUTE_SUMMARY_GUARD=",
        .command = "python3 scripts/zigux/check-phase1-route-summary-counts.py",
    },
    .{
        .marker = "PHASE1_SHARED_TESTS_ROUTE=",
        .command = "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    },
    .{
        .marker = "PHASE1_FIND_BIT_REVIEW_GUARD=",
        .command = "python3 scripts/zigux/check-phase1-find-bit-review-packet.py",
    },
    .{
        .marker = "PHASE1_RBTREE_REVIEW_GUARD=",
        .command = "python3 scripts/zigux/check-phase1-rbtree-review-packet.py",
    },
    .{
        .marker = "PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=",
        .command = "python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
    },
};

const validator_required_files = [_][]const u8{
    "ROUTE_SUMMARY_CHECKER_REL = Path(\"scripts/zigux/check-phase1-route-summary-counts.py\")",
    "FIND_BIT_REVIEW_CHECKER_REL = Path(\"scripts/zigux/check-phase1-find-bit-review-packet.py\")",
    "RBTREE_REVIEW_CHECKER_REL = Path(\"scripts/zigux/check-phase1-rbtree-review-packet.py\")",
    "DIRECT_ANCHOR_MANIFEST_GATE_REL = Path(\"scripts/zigux/check-phase1-direct-anchor-manifest-gate.py\")",
    "TESTS_BUILD_REL = Path(\"zigux/tests/build.zig\")",
    "PHASE1_SMOKE_REL = Path(\"zigux/tests/phase1_host_tools_smoke.zig\")",
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(testing.allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        testing.allocator,
        .limited(limit),
    );
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try testing.expect(first_index < second_index);
}

test "phase1 closure note keeps executable command markers review-visible" {
    const closure_note = try readRepoFile("Documentation/zigux/phase1-closure.md", 128 * 1024);
    defer testing.allocator.free(closure_note);

    for (closure_commands) |entry| {
        try expectContains(closure_note, entry.marker);
        try expectContains(closure_note, entry.command);
    }

    try expectContains(closure_note, "PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master");
    try expectContains(closure_note, "PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker");

    try expectBefore(closure_note, "PHASE1_CLOSURE_VALIDATOR=", "PHASE1_ROUTE_SUMMARY_GUARD=");
    try expectBefore(closure_note, "PHASE1_ROUTE_SUMMARY_GUARD=", "PHASE1_SHARED_TESTS_ROUTE=");
    try expectBefore(closure_note, "PHASE1_FIND_BIT_REVIEW_GUARD=", "PHASE1_RBTREE_REVIEW_GUARD=");
    try expectBefore(closure_note, "PHASE1_RBTREE_REVIEW_GUARD=", "PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=");
}

test "closure validator requires the checker files named by the command surface" {
    const closure_validator = try readRepoFile("scripts/zigux/validate-phase1-closure.py", 512 * 1024);
    defer testing.allocator.free(closure_validator);

    for (validator_required_files) |required_file_marker| {
        try expectContains(closure_validator, required_file_marker);
    }

    try expectContains(closure_validator, "ROUTE_SUMMARY_CHECKER_REL,");
    try expectContains(closure_validator, "FIND_BIT_REVIEW_CHECKER_REL,");
    try expectContains(closure_validator, "RBTREE_REVIEW_CHECKER_REL,");
    try expectContains(closure_validator, "DIRECT_ANCHOR_MANIFEST_GATE_REL,");
}

test "closure validator self-test output remains a stable CLI contract" {
    const closure_validator = try readRepoFile("scripts/zigux/validate-phase1-closure.py", 512 * 1024);
    defer testing.allocator.free(closure_validator);

    try expectContains(closure_validator, "PHASE1_CLOSURE_VALIDATOR_SELF_TEST=pass");
    try expectContains(closure_validator, "PHASE1_CLOSURE_VALIDATOR_SELF_TEST_CASE_COUNT=");
    try expectContains(closure_validator, "PHASE1_CLOSURE_VALIDATION=pass");
    try expectContains(closure_validator, "PHASE1_CLOSURE_REQUIRED_FILE_COUNT=");
}
