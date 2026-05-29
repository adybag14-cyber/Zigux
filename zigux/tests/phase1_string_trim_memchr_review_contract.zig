const std = @import("std");
const testing = std.testing;

const closure_string_packet =
    \\PHASE1_STRING_REVIEW_GUARD=python3 scripts/zigux/check-phase1-string-review-packet.py exact-checks helper-local string anchors plus the committed replaceChar and current string fixture packet across the helper, closure note, lane note, manifest, and fixture
    \\PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py exact-checks the current direct-anchor helper manifest packet for bitmap, find_bit, rbtree, and string and then reruns the dedicated rbtree direct-anchor checker
    \\PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker against the restored closure note, the closure validator, the shared tests-root smoke route, and the helper-specific next_safe_step_note entries in the committed manifest rather than widening back into the older validator-first or replay-side closure stack.
;

const string_review_packet =
    \\trim_nul_review_anchor: test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"
    \\trim_nul_review_summary: the direct trim follow-up stays explicit because the shared Phase 1 string fixture records the trimmed bytes but not the preserved tail bytes beyond the first embedded terminator
    \\phase1_trim_cstr_replay_anchor: test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"
    \\phase1_trim_cstr_replay_summary: the shared Phase 1 string replay still only locks the plain trailing-whitespace trimSpaces bytes from the committed fixture, while the direct helper-local trim follow-up keeps embedded-NUL trimming for trimSpaces and strim plus strstrip and preserved tail-byte review explicit because the shared packet still does not exercise every trim alias or every post-NUL byte position
    \\memchr_moving_dirty_anchor: test "memchrInv follows the earliest dirty byte as long buffers change"
    \\memchr_moving_dirty_review_summary: the direct memchrInv follow-up stays explicit because the shared Phase 1 fixture pins one fixed dirty index and the clean case, but not the moving earliest-mismatch ownership as later dirty bytes become the next live divergence
    \\next_safe_step_note: If this helper lane reopens, keep the helper-local strlcat, sysfs, case-insensitive compare, and match-or-terminator review anchors aligned across the string review packet and this lane note unless dedicated shared fixture keys land; do not reopen missing closure-side validator names by default.
;

const lane_note_string_owner =
    \\PHASE1_STRING_NEXT_SAFE_STEP=string reopens only for direct-anchor drift inside strscpy()/strscpyPad() copy-and-pad semantics, memparse, matched-prefix-length or suffix boundary, sysfs newline-aware equality or lookup order, matchString()/match_string() C-string list lookup, counted-search and search-length anchors through strpbrk(), strspn(), strcspn(), strnchr(), strnchrNul() or strnchrnul(), strchr(), strrchr(), strlen(), and strnlen(), embedded-NUL trim, or moving-earliest-dirty-byte memchrInv coverage, or for committed replaceChar or current string fixture drift; keep the helper-local sysfs review anchors aligned across the string review packet and this lane note unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator names by default
;

const trim_packet_markers = [_][]const u8{
    "trim_nul_review_anchor",
    "phase1_trim_cstr_replay_anchor",
    "trimSpaces and strim plus strstrip",
    "preserved tail-byte review explicit",
    "every trim alias or every post-NUL byte position",
};

const memchr_packet_markers = [_][]const u8{
    "memchr_moving_dirty_anchor",
    "memchrInv follows the earliest dirty byte as long buffers change",
    "moving earliest-mismatch ownership",
    "later dirty bytes become the next live divergence",
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "closure packet keeps string review anchored to the manifest-backed guard" {
    try expectContains(closure_string_packet, "PHASE1_STRING_REVIEW_GUARD=python3 scripts/zigux/check-phase1-string-review-packet.py");
    try expectContains(closure_string_packet, "across the helper, closure note, lane note, manifest, and fixture");
    try expectContains(closure_string_packet, "PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py");
    try expectContains(closure_string_packet, "helper-specific next_safe_step_note entries");
}

test "string trim review stays helper-local until dedicated fixture keys land" {
    for (trim_packet_markers) |marker| {
        try expectContains(string_review_packet, marker);
    }

    try expectContains(lane_note_string_owner, "embedded-NUL trim");
    try expectContains(lane_note_string_owner, "do not reopen missing closure-side validator names by default");
}

test "moving dirty memchrInv ownership remains a direct string review follow-up" {
    for (memchr_packet_markers) |marker| {
        try expectContains(string_review_packet, marker);
    }

    try expectContains(lane_note_string_owner, "moving-earliest-dirty-byte memchrInv coverage");
    try expectContains(lane_note_string_owner, "committed replaceChar or current string fixture drift");
}
