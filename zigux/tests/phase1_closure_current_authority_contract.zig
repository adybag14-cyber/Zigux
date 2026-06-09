const std = @import("std");
const testing = std.testing;

const max_file_size = 512 * 1024;

fn readFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        testing.io,
        path,
        testing.allocator,
        .limited(max_file_size),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try testing.expect(first_index < second_index);
}

test "phase1 closure names the current authority sources explicitly" {
    const closure = try readFile("Documentation/zigux/phase1-closure.md");
    defer testing.allocator.free(closure);

    try expectContains(closure, "- `PHASE1_STATUS=parked`");
    try expectContains(closure, "- `PHASE1_CLOSURE_RESTORE_STATE=docs_plus_validator`");
    try expectContains(closure, "- `PHASE1_HELPER_COUNT=13`");
    try expectContains(closure, "current authority: the committed helper manifest, this closure note, the narrow closure validator, the direct-anchor manifest gate, the shipped bench checker, the shipped shared reminder checker, the live owner-map reminders, and the shared tests-root smoke route remain the trustworthy current-master sources");
    try expectContains(closure, "the route-summary checker stays an adjacent workflow and Makefile guard");

    try expectContains(closure, "manifest: `zigux/tests/fixtures/phase1_helper_manifest.json`");
    try expectContains(closure, "The bounded Phase 1 helper tranche is still the same thirteen helper ports named in the committed manifest");
    try expectNotContains(closure, "`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`");
}

test "current reminder packet stays narrow and ordered before broader companions" {
    const closure = try readFile("Documentation/zigux/phase1-closure.md");
    defer testing.allocator.free(closure);

    const reminder = "`PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,scripts/zigux/README.md,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-direct-anchor-manifest-gate.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py,scripts/zigux/validate-phase1-closure.py,zigux/tests/README.md,zigux/tests/build.zig,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_helpers_build.zig,zigux/tests/phase1_host_tools_smoke.zig,.github/workflows/zigux-bootstrap.yml,zigux/tests/fixtures/phase1_helper_manifest.json`";
    const gap = "`PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`";

    try expectContains(closure, reminder);
    try expectContains(closure, gap);
    try expectBefore(closure, "## Current Reminder Packet", "## Broader Closure Companions");
    try expectBefore(closure, reminder, gap);
    try expectContains(closure, "The older validator-first and replay-side closure companions remain broader closure-stack references rather than active current reminder-packet proof.");
    try expectContains(closure, "historical closure-stack vocabulary until direct current-master rereads restore them");
}

test "closure validator keeps the authority packet in its required surface" {
    const validator = try readFile("scripts/zigux/validate-phase1-closure.py");
    defer testing.allocator.free(validator);

    const required_paths = [_][]const u8{
        "PHASE1_CLOSURE_REL",
        "PHASE1_LANE_NOTE_REL",
        "DOCS_ROOT_REL",
        "REVIEW_CHECKLIST_REL",
        "SCRIPTS_README_REL",
        "STRING_REVIEW_CHECKER_REL",
        "DIRECT_OWNER_CHECKER_REL",
        "DIRECT_ANCHOR_MANIFEST_GATE_REL",
        "BENCH_CHECKER_REL",
        "SHARED_REMINDER_CHECKER_REL",
        "TESTS_BUILD_REL",
        "PHASE1_HELPERS_REPLAY_REL",
        "PHASE1_SMOKE_REL",
        "WORKFLOW_REL",
        "MANIFEST_REL",
    };

    try expectContains(validator, "REQUIRED_FILES = (");
    for (required_paths) |path_marker| {
        try expectContains(validator, path_marker);
    }

    try expectContains(validator, "\"status\": \"`PHASE1_STATUS=parked`\"");
    try expectContains(validator, "\"restore_state\": \"`PHASE1_CLOSURE_RESTORE_STATE=docs_plus_validator`\"");
    try expectContains(validator, "\"helper_count\": \"`PHASE1_HELPER_COUNT=13`\"");
    try expectContains(validator, "\"reminder_packet\": \"`PHASE1_CURRENT_REMINDER_PACKET=");
    try expectContains(validator, "\"gap_packet\": \"`PHASE1_CURRENT_GAP_PACKET=");
    try expectContains(validator, "\"validator_state\": \"`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`\"");
    try expectContains(validator, "FORBIDDEN_CLOSURE_MARKERS = {");
    try expectContains(validator, "`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`");
    try expectContains(validator, "`PHASE1_NEXT_SAFE_STEP=restore the missing phase1 closure note first`");
}
