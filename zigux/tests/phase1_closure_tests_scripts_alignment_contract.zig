const std = @import("std");
const contract_options = @import("contract_options");

const shared_smoke_route =
    "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig";

const focused_replay_route =
    "zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig";

const closure_validator_marker =
    "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`";

const shared_tests_marker =
    "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`";

const next_safe_step_marker =
    "`PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker against the restored closure note, the closure validator, the shared tests-root smoke route, and the helper-specific next_safe_step_note entries in the committed manifest rather than widening back into the older validator-first or replay-side closure stack.`";

const scripts_direct_anchor_split =
    "the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, and string reopen only inside their existing helper-local anchors or already-committed shared fixture keys, while the other nine closed helpers stay parked unless the shared replay or reminder packet drifts";

const tests_direct_anchor_split =
    "keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`";

const broader_gap_tests_marker =
    "broader Phase 1 closure companions stay outside the narrow direct-readback packet";

const historical_scripts_marker =
    "historical packet members that need fresh re-materialization before they are reused here as direct current-`master` reminder evidence";

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        allocator,
        .limited(2 * 1024 * 1024),
    );
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOf(u8, haystack[cursor..], needle)) |relative_index| {
        count += 1;
        cursor += relative_index + needle.len;
    }
    return count;
}

fn expectOnce(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(haystack, needle));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.BeforeMarkerMissing;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.AfterMarkerMissing;
    try std.testing.expect(before_index < after_index);
}

test "scripts and tests reminders keep the shared Phase 1 smoke route aligned with closure" {
    const allocator = std.testing.allocator;
    const closure_text = try readFile(allocator, contract_options.closure_path);
    defer allocator.free(closure_text);
    const scripts_text = try readFile(allocator, contract_options.scripts_readme_path);
    defer allocator.free(scripts_text);
    const tests_text = try readFile(allocator, contract_options.tests_readme_path);
    defer allocator.free(tests_text);

    try expectOnce(closure_text, closure_validator_marker);
    try expectOnce(closure_text, shared_tests_marker);
    try expectContains(scripts_text, "python3 scripts/zigux/validate-phase1-closure.py");
    try expectContains(scripts_text, shared_smoke_route);
    try expectContains(tests_text, "current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`");
    try expectOrdered(tests_text, "current direct-readback Phase 1 reminder packet:", "current shared Phase 1 smoke route:");
}

test "scripts and tests reminders keep focused replay separate from closure smoke" {
    const allocator = std.testing.allocator;
    const closure_text = try readFile(allocator, contract_options.closure_path);
    defer allocator.free(closure_text);
    const scripts_text = try readFile(allocator, contract_options.scripts_readme_path);
    defer allocator.free(scripts_text);
    const tests_text = try readFile(allocator, contract_options.tests_readme_path);
    defer allocator.free(tests_text);

    try expectContains(closure_text, focused_replay_route);
    try expectContains(scripts_text, focused_replay_route);
    try expectContains(tests_text, "current focused Phase 1 helper replay route: `zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig`");
    try expectContains(closure_text, "The current shared tests-root closure route is narrow on purpose");
    try expectContains(scripts_text, "focused fixture-backed helper parity replay anchor");
    try expectContains(tests_text, broader_gap_tests_marker);
}

test "direct-anchor helper split stays aligned across closure, scripts, and tests reminders" {
    const allocator = std.testing.allocator;
    const closure_text = try readFile(allocator, contract_options.closure_path);
    defer allocator.free(closure_text);
    const scripts_text = try readFile(allocator, contract_options.scripts_readme_path);
    defer allocator.free(scripts_text);
    const tests_text = try readFile(allocator, contract_options.tests_readme_path);
    defer allocator.free(tests_text);

    try expectOnce(closure_text, next_safe_step_marker);
    try expectContains(scripts_text, scripts_direct_anchor_split);
    try expectContains(tests_text, tests_direct_anchor_split);
    try expectContains(scripts_text, historical_scripts_marker);
    try expectContains(tests_text, "older Phase 1 wrapper names remain historical packet members rather than active tests-root proof");
}
