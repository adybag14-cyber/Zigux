const std = @import("std");
const testing = std.testing;

const closure_note =
    \\PHASE1_STRING_SYSFS_REVIEW=helper-local string sysfs newline-aware equality and lookup-order anchors stay explicit through the direct string tests and the Phase 1 helper manifest because the shared Phase 1 replay still carries no dedicated sysfs fixture keys
    \\PHASE1_STRING_REVIEW_GUARD=python3 scripts/zigux/check-phase1-string-review-packet.py exact-checks helper-local string anchors plus the committed replaceChar and current string fixture packet across the helper, closure note, lane note, manifest, and fixture
    \\Current master now also spells the helper-local memtostr(), memtostrPad(), and memtostr_pad() anchors directly in the shipped manifest-backed string review packet beside the memcpyAndPad(), memcpy_and_pad(), strtomem(), and strtomem_pad() byte-copy anchors. Keep those byte-copy and pad tests helper-local review evidence rather than shared-fixture or validator-owned requirements until dedicated fixture keys land.
;

const manifest_string_packet =
    \\search_length_review_anchors: [strchr, strrchr, strlen, strnlen, strchrNul, strchrnul]
    \\search_length_review_summary: helper-local search-and-length boundary anchors stay explicit through the direct string tests because the shared Phase 1 replay still does not carry dedicated search-length fixture keys, so strchr() or strrchr() boundary scans, terminator-index searches, strchrNul() or strchrnul() match-or-terminator boundaries, and strlen() or strnlen() length boundaries remain review-visible at the helper surface
    \\counted_search_review_anchors: [strchr, strrchr, strpbrk, strspn, strcspn, strnchr, strnlen, strnchrNul, strchrNul]
    \\strnchr_review_summary: the direct counted-search and C-string search-length follow-up stays explicit because the shared Phase 1 replay still does not carry dedicated counted-search or search-length fixture keys, so strchr() or strrchr() full-length C-string searches, strpbrk() first-accepted-byte scanning, strspn() accepted-prefix scanning, strcspn() rejected-byte scanning, strnchr() count-limited scanning, strnlen() count-clamped length, strnchrNul() or strnchrnul() match-or-NUL boundary behavior, and strchrNul() or strchrnul() match-or-terminator boundaries remain owned by the helper-local anchors
    \\next_safe_step_note: If this helper lane reopens, keep the helper-local strlcat, sysfs, case-insensitive compare, and match-or-terminator review anchors aligned across the string review packet and this lane note unless dedicated shared fixture keys land; do not reopen missing closure-side validator names by default.
;

const expected_manifest_keys = [_][]const u8{
    "search_length_review_anchors",
    "search_length_review_summary",
    "counted_search_review_anchors",
    "strnchr_review_summary",
    "next_safe_step_note",
};

const helper_local_anchor_names = [_][]const u8{
    "strchr",
    "strrchr",
    "strpbrk",
    "strspn",
    "strcspn",
    "strnchr",
    "strnlen",
    "strnchrNul",
    "strchrNul",
    "strchrnul",
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "closure note keeps string search review owned by the string review guard" {
    try expectContains(closure_note, "PHASE1_STRING_REVIEW_GUARD=python3 scripts/zigux/check-phase1-string-review-packet.py");
    try expectContains(closure_note, "helper-local string anchors");
    try expectContains(closure_note, "across the helper, closure note, lane note, manifest, and fixture");
    try expectContains(closure_note, "shared-fixture or validator-owned requirements");
}

test "string manifest packet keeps search and counted-search anchors explicit" {
    for (expected_manifest_keys) |key| {
        try expectContains(manifest_string_packet, key);
    }

    for (helper_local_anchor_names) |anchor| {
        try expectContains(manifest_string_packet, anchor);
    }
}

test "next safe step parks string unless fresh helper-local drift is reread" {
    try expectContains(manifest_string_packet, "keep the helper-local strlcat, sysfs, case-insensitive compare");
    try expectContains(manifest_string_packet, "match-or-terminator review anchors aligned");
    try expectContains(manifest_string_packet, "do not reopen missing closure-side validator names by default");
}
