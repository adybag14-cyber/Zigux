const std = @import("std");

const read_limit = 256 * 1024;

const shared_replay_helpers = "tools/lib/argv_split.zig,tools/lib/cmdline.zig,tools/lib/ctype.zig,tools/lib/hweight.zig,tools/lib/list_sort.zig,tools/lib/slab.zig,tools/lib/str_error_r.zig,tools/lib/vsprintf.zig,tools/lib/zalloc.zig";
const direct_anchor_helpers = "tools/lib/bitmap.zig,tools/lib/find_bit.zig,tools/lib/rbtree.zig,tools/lib/string.zig";

const lane_rule_summary = "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local follow-up anchors on current master.";
const anti_overlap_rule = "Do not reopen Phase 1 by batching helpers across those two sets in one lane; shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers reopen only for their existing helper-local anchors or already-committed shared fixture keys.";

const reminder_packet = "PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,scripts/zigux/README.md,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-direct-anchor-manifest-gate.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py,scripts/zigux/validate-phase1-closure.py,zigux/tests/README.md,zigux/tests/build.zig,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_helpers_build.zig,zigux/tests/phase1_host_tools_smoke.zig,.github/workflows/zigux-bootstrap.yml,zigux/tests/fixtures/phase1_helper_manifest.json";

const shared_reminder_route_split = "PHASE1_DIRECT_OWNER_SHARED_REMINDER_ROUTE_SPLIT=Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, zigux/tests/README.md, and scripts/zigux/README.md now all carry the shipped bench-checker wording, while Documentation/zigux/phase1-closure.md plus scripts/zigux/validate-phase1-closure.py keep the restored closure-side packet explicit and the broader installer-backed, validator-first, bench-route, and replay names remain historical packet members until direct current-master rereads restore them";

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

test "phase1 closure note keeps current reminder and lane split markers" {
    const closure = try readFile("Documentation/zigux/phase1-closure.md");
    defer std.testing.allocator.free(closure);

    try expectContains(closure, reminder_packet);
    try expectContains(closure, "PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker against the restored closure note, the closure validator, the shared tests-root smoke route, and the helper-specific next_safe_step_note entries in the committed manifest rather than widening back into the older validator-first or replay-side closure stack.");
    try expectContains(closure, "PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py");
    try expectContains(closure, "PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig");
}

test "phase1 lane note preserves the shared replay versus direct anchor owner map" {
    const lane_note = try readFile("Documentation/zigux/phase1-host-helper-lane-sequencing.md");
    defer std.testing.allocator.free(lane_note);

    try expectContains(lane_note, "PHASE1_SHARED_REPLAY_PARKED_HELPERS=" ++ shared_replay_helpers);
    try expectContains(lane_note, "PHASE1_DIRECT_ANCHOR_FOLLOWUP_HELPERS=" ++ direct_anchor_helpers);
    try expectContains(lane_note, "PHASE1_LANE_RULE_SUMMARY=" ++ lane_rule_summary);
    try expectContains(lane_note, "PHASE1_LANE_ANTI_OVERLAP_RULE=" ++ anti_overlap_rule);
    try expectContains(lane_note, shared_reminder_route_split);
}

test "phase1 closure validator pins the lane sequencing split" {
    const validator = try readFile("scripts/zigux/validate-phase1-closure.py");
    defer std.testing.allocator.free(validator);

    try expectContains(validator, "\"tools/lib/argv_split.zig\"");
    try expectContains(validator, "\"tools/lib/zalloc.zig\"");
    try expectContains(validator, "\"tools/lib/bitmap.zig\"");
    try expectContains(validator, "\"tools/lib/string.zig\"");
    try expectContains(validator, "EXPECTED_SHARED_REPLAY_PARKED_HELPERS = [");
    try expectContains(validator, "EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [");
    try expectContains(validator, "EXPECTED_LANE_RULE_SUMMARY = (");
    try expectContains(validator, "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, ");
    try expectContains(validator, "while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local ");
    try expectContains(validator, "EXPECTED_ANTI_OVERLAP_RULE = (");
    try expectContains(validator, "Do not reopen Phase 1 by batching helpers across those two sets in one lane; ");
    try expectContains(validator, "reopen only for their existing helper-local anchors or already-committed shared fixture keys.");
    try expectContains(validator, "\"stale_lane_rule_summary\"");
    try expectContains(validator, "\"stale_anti_overlap_rule\"");
    try expectContains(validator, "lane_sequencing.shared_replay_parked_helpers");
    try expectContains(validator, "lane_sequencing.direct_anchor_followup_helpers");
}

test "phase1 shared reminder surfaces keep lane sequencing routed through closure validation" {
    const docs_root = try readFile("Documentation/zigux/README.md");
    defer std.testing.allocator.free(docs_root);
    const review_checklist = try readFile("Documentation/zigux/review-checklist.md");
    defer std.testing.allocator.free(review_checklist);

    try expectContains(docs_root, "keep the live owner map, the restored closure note and closure validator");
    try expectContains(docs_root, "keep the helper-family split explicit here too: the nine shared-replay parked helpers reopen only for packet drift, while bitmap, find_bit, rbtree, and string keep the only bounded direct-anchor follow-up anchors on current master.");
    try expectContains(docs_root, "python3 scripts/zigux/validate-phase1-closure.py");
    try expectContains(review_checklist, "if the change touches the shared Phase 1 host-tools closure packet");
    try expectContains(review_checklist, "zigux/tests/fixtures/phase1_helper_manifest.json");
    try expectContains(review_checklist, "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig");
}

test "phase1 helper manifest matches the lane sequencing split exactly" {
    const manifest = try readFile("zigux/tests/fixtures/phase1_helper_manifest.json");
    defer std.testing.allocator.free(manifest);

    try expectContains(manifest, "\"shared_replay_parked_helpers\": [");
    try expectContains(manifest, "\"direct_anchor_followup_helpers\": [");
    try expectContains(manifest, "\"rule_summary\": \"" ++ lane_rule_summary ++ "\"");
    try expectContains(manifest, "\"anti_overlap_rule\": \"" ++ anti_overlap_rule ++ "\"");

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

    for (shared_helpers) |helper| {
        const marker = try std.fmt.allocPrint(std.testing.allocator, "\"{s}\"", .{helper});
        defer std.testing.allocator.free(marker);
        try expectContains(manifest, marker);
    }
    for (direct_helpers) |helper| {
        const marker = try std.fmt.allocPrint(std.testing.allocator, "\"{s}\"", .{helper});
        defer std.testing.allocator.free(marker);
        try expectContains(manifest, marker);
    }
}
