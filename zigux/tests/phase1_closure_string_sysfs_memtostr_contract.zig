const std = @import("std");

const sysfs_closure_marker =
    \\PHASE1_STRING_SYSFS_REVIEW=helper-local string sysfs newline-aware equality and lookup-order anchors stay explicit through the direct string tests and the Phase 1 helper manifest because the shared Phase 1 replay still carries no dedicated sysfs fixture keys
;

const memtostr_closure_paragraph =
    \\Current `master` now also spells the helper-local `memtostr()`, `memtostrPad()`, and `memtostr_pad()` anchors directly in the shipped manifest-backed string review packet beside the `memcpyAndPad()`, `memcpy_and_pad()`, `strtomem()`, and `strtomem_pad()` byte-copy anchors. Keep those byte-copy and pad tests helper-local review evidence rather than shared-fixture or validator-owned requirements until dedicated fixture keys land.
;

const helper_string_anchors =
    \\test "sysfsStreq treats trailing newline and NUL as equivalent"
    \\test "sysfs_streq mirrors sysfsStreq newline and NUL equivalence"
    \\test "sysfsMatchString finds newline-aware matches and preserves first-match order"
    \\test "sysfs_match_string mirrors sysfsMatchString for empty and matched lists"
    \\test "memtostr copies a bounded non-NUL source and adds one terminator"
    \\test "memtostr stops at embedded NUL without padding the tail"
    \\test "memtostrPad zero-pads the remaining tail after copying"
    \\test "memtostr helpers keep one-byte destinations terminated"
;

const manifest_sysfs_packet =
    \\"sysfs_review_anchors": [
    \\"test \"sysfsStreq treats trailing newline and NUL as equivalent\"",
    \\"test \"sysfs_streq mirrors sysfsStreq newline and NUL equivalence\"",
    \\"test \"sysfsMatchString finds newline-aware matches and preserves first-match order\"",
    \\"test \"sysfs_match_string mirrors sysfsMatchString for empty and matched lists\""
    \\]
    \\"sysfs_review_summary": "helper-local string sysfs newline-aware equality and lookup-order anchors stay explicit through the direct string tests because the shared Phase 1 replay still carries no dedicated sysfs fixture keys, so sysfsStreq and sysfs_streq plus sysfsMatchString and sysfs_match_string remain review-visible at the helper surface"
;

const manifest_memtostr_packet =
    \\"memtostr_review_anchors": [
    \\"test \"memtostr copies a bounded non-NUL source and adds one terminator\"",
    \\"test \"memtostr stops at embedded NUL without padding the tail\"",
    \\"test \"memtostrPad zero-pads the remaining tail after copying\"",
    \\"test \"memtostr helpers keep one-byte destinations terminated\""
    \\]
    \\"memtostr_review_summary": "helper-local memtostr boundary and tail-padding anchors stay explicit through the direct string tests because the shared Phase 1 replay still does not carry dedicated memtostr(), memtostrPad(), or memtostr_pad() fixture keys, so bounded source copies, embedded-NUL stops, terminator insertion, and zero-padded destination tails remain review-visible at the helper surface"
;

const shared_string_fixture_packet =
    \\"strtobool_y"
    \\"strlcpy_len"
    \\"skip_spaces"
    \\"trim_spaces"
    \\"remove_spaces"
    \\"replace_char"
    \\"replace_char_cstr_bytes"
    \\"memchr_inv_index"
    \\"memchr_inv_none"
;

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "closure note keeps string sysfs review helper-local" {
    try expectContains(
        sysfs_closure_marker,
        "PHASE1_STRING_SYSFS_REVIEW=helper-local string sysfs newline-aware equality",
    );
    try expectContains(sysfs_closure_marker, "direct string tests and the Phase 1 helper manifest");
    try expectContains(sysfs_closure_marker, "shared Phase 1 replay still carries no dedicated sysfs fixture keys");
    try expectNotContains(sysfs_closure_marker, "validator-owned");
    try expectNotContains(sysfs_closure_marker, "broader closure-stack");
}

test "closure note keeps memtostr and byte-copy anchors out of shared fixture ownership" {
    try expectContains(memtostr_closure_paragraph, "memtostr()");
    try expectContains(memtostr_closure_paragraph, "memtostrPad()");
    try expectContains(memtostr_closure_paragraph, "memtostr_pad()");
    try expectContains(memtostr_closure_paragraph, "memcpyAndPad()");
    try expectContains(memtostr_closure_paragraph, "strtomem_pad()");
    try expectContains(memtostr_closure_paragraph, "helper-local review evidence");
    try expectContains(memtostr_closure_paragraph, "rather than shared-fixture or validator-owned requirements");
    try expectContains(memtostr_closure_paragraph, "until dedicated fixture keys land");
}

test "direct string anchors cover sysfs and memtostr helper families" {
    try expectContains(helper_string_anchors, "test \"sysfsStreq treats trailing newline and NUL as equivalent\"");
    try expectContains(helper_string_anchors, "test \"sysfs_streq mirrors sysfsStreq newline and NUL equivalence\"");
    try expectContains(helper_string_anchors, "test \"sysfsMatchString finds newline-aware matches and preserves first-match order\"");
    try expectContains(helper_string_anchors, "test \"sysfs_match_string mirrors sysfsMatchString for empty and matched lists\"");
    try expectContains(helper_string_anchors, "test \"memtostr copies a bounded non-NUL source and adds one terminator\"");
    try expectContains(helper_string_anchors, "test \"memtostr stops at embedded NUL without padding the tail\"");
    try expectContains(helper_string_anchors, "test \"memtostrPad zero-pads the remaining tail after copying\"");
    try expectContains(helper_string_anchors, "test \"memtostr helpers keep one-byte destinations terminated\"");
}

test "manifest packets preserve string sysfs and memtostr review boundaries" {
    try expectContains(manifest_sysfs_packet, "\"sysfs_review_anchors\"");
    try expectContains(manifest_sysfs_packet, "sysfsStreq and sysfs_streq");
    try expectContains(manifest_sysfs_packet, "sysfsMatchString and sysfs_match_string");
    try expectContains(manifest_sysfs_packet, "no dedicated sysfs fixture keys");
    try expectContains(manifest_memtostr_packet, "\"memtostr_review_anchors\"");
    try expectContains(manifest_memtostr_packet, "bounded source copies");
    try expectContains(manifest_memtostr_packet, "embedded-NUL stops");
    try expectContains(manifest_memtostr_packet, "terminator insertion");
    try expectContains(manifest_memtostr_packet, "zero-padded destination tails");
}

test "shared string fixture packet omits sysfs and memtostr ownership keys" {
    try expectContains(shared_string_fixture_packet, "\"replace_char_cstr_bytes\"");
    try expectContains(shared_string_fixture_packet, "\"memchr_inv_index\"");
    try expectNotContains(shared_string_fixture_packet, "sysfs_review_anchors");
    try expectNotContains(shared_string_fixture_packet, "sysfsStreq");
    try expectNotContains(shared_string_fixture_packet, "memtostr_review_anchors");
    try expectNotContains(shared_string_fixture_packet, "memtostrPad");
}
