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

test "phase 1 closure validator keeps delegated checker roster explicit" {
    const validator = try readRepoFile("scripts\zigux/validate_phase1_closure.zig", 512 * 1024);
    defer std.testing.allocator.free(validator);

    if (std.mem.indexOf(u8, validator, "DELEGATED_CHECKERS = (") != null) {
        try expectContains(validator, "DELEGATED_CHECKERS = (");
        try expectContains(validator, "run_checker(root, script_rel, label)");
        try expectContains(validator, "STRING_REVIEW_CHECKER_REL = Path(\"scripts\zigux/check_phase1_string_review_packet.zig\")");
        try expectContains(validator, "FIND_BIT_REVIEW_CHECKER_REL = Path(\"scripts\zigux/check_phase1_find_bit_review_packet.zig\")");
        try expectContains(validator, "RBTREE_REVIEW_CHECKER_REL = Path(\"scripts\zigux/check_phase1_rbtree_review_packet.zig\")");
        try expectContains(validator, "DIRECT_OWNER_CHECKER_REL = Path(\"scripts\zigux/check_phase1_direct_owner_markers.zig\")");
        try expectContains(validator, "DIRECT_ANCHOR_MANIFEST_GATE_REL = Path(\"scripts\zigux/check_phase1_direct_anchor_manifest_gate.zig\")");
        try expectContains(validator, "BENCH_CHECKER_REL = Path(\"scripts\zigux/check_phase1_bench.zig\")");
        try expectContains(validator, "FIND_BIT_BENCH_ANCHOR_CHECKER_REL = Path(\"scripts\zigux/check_phase1_find_bit_bench_anchors.zig\")");
        try expectContains(validator, "BITMAP_DIRECT_ANCHOR_CHECKER_REL = Path(\"scripts\zigux/check_phase1_bitmap_direct_anchors.zig\")");
        try expectBefore(validator, "STRING_REVIEW_CHECKER_REL", "DIRECT_ANCHOR_MANIFEST_GATE_REL");
        try expectBefore(validator, "FIND_BIT_REVIEW_CHECKER_REL", "DIRECT_ANCHOR_MANIFEST_GATE_REL");
        try expectBefore(validator, "RBTREE_REVIEW_CHECKER_REL", "DIRECT_ANCHOR_MANIFEST_GATE_REL");
        return;
    }

    try expectContains(validator, "\"scripts\zigux/validate_phase1_closure.zig\"");
    try expectContains(validator, "\"scripts\zigux/check_phase1_bench.zig\"");
    try expectContains(validator, "\"scripts\zigux/check_phase1_direct_owner_markers.zig\"");
    try expectContains(validator, "PHASE1_CLOSURE_GATE=zig run scripts/zigux/validate_phase1_closure.zig");
}

test "phase 1 closure note stays tied to the narrow validator route" {
    const closure_note = try readRepoFile("Documentation/zigux/phase1-closure.md", 256 * 1024);
    defer std.testing.allocator.free(closure_note);

    if (std.mem.indexOf(u8, closure_note, "PHASE1_CLOSURE_RESTORE_STATE=docs_plus_validator") != null) {
        try expectOnce(closure_note, "`PHASE1_CLOSURE_VALIDATOR=zig run scripts/zigux/validate_phase1_closure.zig`");
        try expectOnce(closure_note, "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`");
        try expectContains(closure_note, "`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`");
        try expectContains(closure_note, "`PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=zig run scripts/zigux/check_phase1_direct_anchor_manifest_gate.zig");
        try expectContains(closure_note, "`PHASE1_STRING_REVIEW_GUARD=zig run scripts/zigux/check_phase1_string_review_packet.zig");
        try expectContains(closure_note, "`PHASE1_FIND_BIT_REVIEW_GUARD=zig run scripts/zigux/check_phase1_find_bit_review_packet.zig");
        try expectContains(closure_note, "`PHASE1_RBTREE_REVIEW_GUARD=zig run scripts/zigux/check_phase1_rbtree_review_packet.zig");
        try expectAbsent(closure_note, "`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`");
        try expectAbsent(closure_note, "`PHASE1_NEXT_SAFE_STEP=restore the missing phase1 closure note first`");
        return;
    }

    try expectContains(closure_note, "PHASE1_STATUS=closed");
    try expectContains(closure_note, "PHASE1_CLOSURE_GATE=zig run scripts/zigux/validate_phase1_closure.zig");
    try expectContains(closure_note, "PHASE1_UNIT_GATE=zig build test --build-file zigux/tests/build.zig");
    try expectContains(closure_note, "PHASE1_BENCH_GATE=zig build bench --build-file zigux/tests/build.zig");
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
