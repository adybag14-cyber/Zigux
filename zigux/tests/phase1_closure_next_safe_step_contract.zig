const std = @import("std");

fn loadGateFile(path: []const u8, limit: usize) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, std.testing.allocator, .limited(limit));
}

fn unloadGateFile(contents: []u8) void {
    std.testing.allocator.free(contents);
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

const old_closure_cues = [_][]const u8{
    "`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`",
    "`PHASE1_NEXT_SAFE_STEP=restore the missing phase1 closure note first`",
    "`PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface against the restored closure note and closure validator`",
    "make -C zigux phase1-validate",
    "make -C zigux phase1-test",
    "make -C zigux phase1-bench",
};

const validator_forbidden_phase1_routes = [_][]const u8{
    "phase1-validate:",
    "phase1-test:",
    "phase1-bench:",
    "phase1:",
};

test "closure note keeps next-safe-step scoped to live reminder surfaces" {
    const closure = try loadGateFile("Documentation/zigux/phase1-closure.md", 256 * 1024);
    defer unloadGateFile(closure);

    const current_next_step =
        "`PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker against the restored closure note, the closure validator, the shared tests-root smoke route, and the helper-specific next_safe_step_note entries in the committed manifest rather than widening back into the older validator-first or replay-side closure stack.`";
    try expectContains(closure, current_next_step);
    try expectContains(closure, "`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`");
    try expectContains(closure, "`PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`");
    try expectBefore(closure, "## Current Reminder Packet", "## Broader Closure Companions");
    try expectBefore(closure, "## Broader Closure Companions", current_next_step);

    inline for (old_closure_cues[0..3]) |stale_marker| {
        try expectNotContains(closure, stale_marker);
    }
}

test "lane sequencing names helper-specific next-step tie breakers" {
    const lane_note = try loadGateFile("Documentation/zigux/phase1-host-helper-lane-sequencing.md", 512 * 1024);
    defer unloadGateFile(lane_note);

    try expectContains(lane_note, "`PHASE1_DIRECT_OWNER_SHARED_REMINDER_NEXT_STEP=leave the shared bench-checker wording and shared-reminder checker packet parked unless a fresh reread finds drift across Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, zigux/tests/README.md, scripts/zigux/README.md, Documentation/zigux/phase1-closure.md, scripts/zigux/validate-phase1-closure.py, scripts/zigux/check-phase1-bench.py, or scripts/zigux/check-phase1-shared-reminder-packet.py; otherwise prefer the smaller helper-specific next-safe-step markers below before reopening any shared reminder surface`");
    try expectContains(lane_note, "`PHASE1_BITMAP_NEXT_SAFE_STEP=bitmap stays parked unless a fresh reread finds new direct-anchor drift or committed shared replay drift; do not reopen older closure-side or validator-route cue names by default`");
    try expectContains(lane_note, "`PHASE1_FIND_BIT_NEXT_SAFE_STEP=find_bit reopens only for direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), underscore-alias or Linux-style alias coverage including the shipped andnot scan entry points, or tail-word skip anchors, or for committed tail-clamped or tail-inclusive-boundary replay drift; do not reopen older saved validator cues or neighboring helper families`");
    try expectContains(lane_note, "`PHASE1_RBTREE_NEXT_SAFE_STEP=rbtree reopens only to keep the already-landed cached_leftmost_return_serials shared replay aligned across the manifest, direct-owner note, and any shared parity gates, or for drift inside the still-helper-local ordered Linux-style alias proof, dedicated low_level_alias_anchor, cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors; do not batch a second widening into the same run`");
    try expectContains(lane_note, "`PHASE1_STRING_NEXT_SAFE_STEP=string reopens only for direct-anchor drift inside strscpy()/strscpyPad() copy-and-pad semantics, memparse, matched-prefix-length or suffix boundary, sysfs newline-aware equality or lookup order, matchString()/match_string() C-string list lookup, counted-search and search-length anchors through strpbrk(), strspn(), strcspn(), strnchr(), strnchrNul() or strnchrnul(), strchr(), strrchr(), strlen(), and strnlen(), embedded-NUL trim, or moving-earliest-dirty-byte memchrInv coverage, or for committed replaceChar or current string fixture drift; keep the helper-local sysfs review anchors aligned across the string review packet and this lane note unless dedicated shared fixture keys land; do not reopen missing closure-side validator names by default`");
    try expectContains(lane_note, "`PHASE1_LIST_SORT_NEXT_SAFE_STEP=list_sort reopens only for shared replay or reminder-surface drift in the committed tri_sorted_* or bool_sorted_* fixture keys, or for drift in the helper-local comparator-context, repeat-sort, reverse-link, sorted-input, parity-bucket, modulo-bucket, all-ties, non-unit comparator, signed subtractive comparator, repeated reorder, or empty-or-singleton anchors; do not widen into neighboring shared-replay parked helpers by default.`");
}

test "manifest next-safe-step notes keep direct-anchor helpers parked" {
    const manifest = try loadGateFile("zigux/tests/fixtures/phase1_helper_manifest.json", 1024 * 1024);
    defer unloadGateFile(manifest);

    try expectContains(manifest, "\"next_safe_step_note\": \"If this helper lane reopens, keep bitmap parked unless a fresh reread finds new direct-anchor drift inside the current helper-local packet or committed shared replay drift in the bitmap copy, logical, range, allocation, formatting, or partial-window parity fields; current master still ships direct fill-tail clamp, raw copy alias, cross-word scnprintf, exact-word-boundary equality fast-path masking, caller-window xor and or clamp, weighted tail-count clamp, empty-buffer, allocator-reset, zero-bit logical short-circuit, and Linux-style alias mirror anchors here; do not reopen older closure-side or validator-route cue names by default.\"");
    try expectContains(manifest, "\"next_safe_step_note\": \"If this helper lane reopens, keep find_bit parked unless a fresh reread finds drift in the manifest-backed same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), underscore-alias, Linux-style alias coverage including the shipped andnot scan entry points, or tail-word skip anchors, or committed shared replay drift in the live `bits_per_long`, `first`, `next_after_6`, `next_after_word`, `first_zero`, `next_zero`, `first_and`, `next_and`, or `last` fixture keys; do not reopen older saved validator cues or neighboring helper families.\"");
    try expectContains(manifest, "\"next_safe_step_note\": \"If this helper lane reopens, keep the already-landed shared-replay promotion for `cached_leftmost_return_serials` aligned across the committed fixture, shared replay, and direct cached-root anchors; the ordered Linux-style alias proof, dedicated `low_level_alias_anchor`, and the remaining cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed behavior stay owned by direct helper-local anchors until another committed cached-root field lands.\"");
    try expectContains(manifest, "\"next_safe_step_note\": \"If this helper lane reopens, keep the helper-local strlcat, sysfs, case-insensitive compare, and match-or-terminator review anchors aligned across the string review packet and this lane note unless dedicated shared fixture keys land; do not reopen missing closure-side validator names by default.\"");
    try expectContains(manifest, "\"direct_anchor_followup_helpers\": [");
    try expectContains(manifest, "\"shared_replay_parked_helpers\": [");
}

test "closure validator preserves the next-step guard and forbidden old state" {
    const validator = try loadGateFile("scripts/zigux/validate-phase1-closure.py", 512 * 1024);
    defer unloadGateFile(validator);

    try expectContains(validator, "\"next_step\": \"`PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker against the restored closure note, the closure validator, the shared tests-root smoke route, and the helper-specific next_safe_step_note entries in the committed manifest rather than widening back into the older validator-first or replay-side closure stack.`\"");
    try expectContains(validator, "\"`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`\"");
    try expectContains(validator, "\"`PHASE1_NEXT_SAFE_STEP=restore the missing phase1 closure note first`\"");
    try expectContains(validator, "stale_string_next_safe_step_note");
    try expectContains(validator, "stale_bitmap_next_safe_step_note");
    try expectContains(validator, "stale_find_bit_next_safe_step_note");
    try expectContains(validator, "stale_rbtree_shared_replay_summary");
    try expectContains(validator, "forbidden_phase1_makefile_route");

    inline for (validator_forbidden_phase1_routes) |forbidden_route| {
        try expectContains(validator, forbidden_route);
    }
}
