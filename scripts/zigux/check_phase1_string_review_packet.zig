// Ported from check-phase1-string-review-packet.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_STRING_REVIEW_PACKET_SELF_TEST=pass";

const STRING_HELPER_REL = "tools/lib/string.zig";
const STRING_MANIFEST_REL = "zigux/tests/fixtures/phase1_helper_manifest.json";
const STRING_FIXTURE_REL = "zigux/tests/fixtures/phase1_helpers.json";
const STRING_LANE_NOTE_REL = "Documentation/zigux/phase1-host-helper-lane-sequencing.md";

const EXPECTED_STRING_SOURCE_SYMBOLS_JSON = "[\"pub fn memparse(text: []const u8) MemparseResult {\", \"pub fn strlcat(dest: []u8, src: []const u8) usize {\", \"pub fn strscpy(dest: []u8, src: []const u8) isize {\", \"pub fn strscpyPad(dest: []u8, src: []const u8) isize {\", \"pub fn strscpy_pad(dest: []u8, src: []const u8) isize {\", \"pub fn memcpyAndPad(dest: []u8, src: []const u8, count: usize, pad: u8) void {\", \"pub fn memcpy_and_pad(dest: []u8, src: []const u8, count: usize, pad: u8) void {\", \"pub fn strtomem(dest: []u8, src: []const u8) void {\", \"pub fn strtomem_pad(dest: []u8, src: []const u8, pad: u8) void {\", \"pub fn memtostr(dest: []u8, src: []const u8) void {\", \"pub fn memtostrPad(dest: []u8, src: []const u8) void {\", \"pub fn memtostr_pad(dest: []u8, src: []const u8) void {\", \"pub fn strEq(lhs: []const u8, rhs: []const u8) bool {\", \"pub fn streq(lhs: []const u8, rhs: []const u8) bool {\", \"pub fn trimSpaces(buf: []u8) []u8 {\", \"pub fn strim(buf: []u8) []u8 {\", \"pub fn strstrip(buf: []u8) []u8 {\", \"pub fn strHasPrefix(buf: []const u8, prefix: []const u8) usize {\", \"pub fn str_has_prefix(buf: []const u8, prefix: []const u8) usize {\", \"pub fn strstarts(buf: []const u8, prefix: []const u8) bool {\", \"pub fn strHasSuffix(buf: []const u8, suffix: []const u8) usize {\", \"pub fn str_has_suffix(buf: []const u8, suffix: []const u8) usize {\", \"pub fn strEndsWith(buf: []const u8, suffix: []const u8) bool {\", \"pub fn str_ends_with(buf: []const u8, suffix: []const u8) bool {\", \"pub fn strends(buf: []const u8, suffix: []const u8) bool {\", \"pub fn kbasename(path: []const u8) []const u8 {\", \"pub fn memchrInv(buf: []const u8, value: u8) ?usize {\", \"pub fn memchr_inv(buf: []const u8, value: u8) ?usize {\", \"pub fn sysfsStreq(lhs: []const u8, rhs: []const u8) bool {\", \"pub fn sysfs_streq(lhs: []const u8, rhs: []const u8) bool {\", \"pub fn __sysfs_match_string(haystack: []const []const u8, count: usize, needle: []const u8) ?usize {\", \"pub fn sysfsMatchString(haystack: []const []const u8, needle: []const u8) ?usize {\", \"pub fn sysfs_match_string(haystack: []const []const u8, needle: []const u8) ?usize {\", \"pub fn matchString(haystack: []const []const u8, needle: []const u8) ?usize {\", \"pub fn match_string(haystack: []const []const u8, needle: []const u8) ?usize {\", \"pub fn strcmp(lhs: []const u8, rhs: []const u8) i32 {\", \"pub fn strncmp(lhs: []const u8, rhs: []const u8, count: usize) i32 {\", \"pub fn strcasecmp(lhs: []const u8, rhs: []const u8) i32 {\", \"pub fn strncasecmp(lhs: []const u8, rhs: []const u8, count: usize) i32 {\", \"pub fn strchr(buf: []const u8, needle: u8) ?usize {\", \"pub fn strrchr(buf: []const u8, needle: u8) ?usize {\", \"pub fn strpbrk(buf: []const u8, accept: []const u8) ?usize {\", \"pub fn strspn(buf: []const u8, accept: []const u8) usize {\", \"pub fn strcspn(buf: []const u8, reject: []const u8) usize {\", \"pub fn strstr(buf: []const u8, needle: []const u8) ?usize {\", \"pub fn strnstr(buf: []const u8, needle: []const u8, count: usize) ?usize {\", \"pub fn strnchr(buf: []const u8, count: usize, needle: u8) ?usize {\", \"pub fn strlen(buf: []const u8) usize {\", \"pub fn strnlen(buf: []const u8, count: usize) usize {\", \"pub fn strnchrNul(buf: []const u8, count: usize, needle: u8) usize {\", \"pub fn strnchrnul(buf: []const u8, count: usize, needle: u8) usize {\", \"pub fn strchrNul(buf: []const u8, needle: u8) usize {\", \"pub fn strchrnul(buf: []const u8, needle: u8) usize {\"]";
const EXPECTED_HELPER_TEST_ANCHORS_JSON = "[\"test \\\"strtobool accepts common Linux forms\\\"\", \"test \\\"strlcpy copies and returns the source length\\\"\", \"test \\\"strlcat appends within the destination size and reports the attempted length\\\"\", \"test \\\"strlcat truncates with a terminator and keeps the full attempted length\\\"\", \"test \\\"strlcat treats an unterminated destination as full\\\"\", \"test \\\"strlcat handles a zero-length destination buffer\\\"\", \"test \\\"strscpy keeps NUL termination and reports truncation with -E2BIG\\\"\", \"test \\\"strscpyPad zero-pads the tail after a short source\\\"\", \"test \\\"strscpyPad stops at embedded NUL and pads the remaining tail\\\"\", \"test \\\"strscpyPad preserves strscpy truncation semantics\\\"\", \"test \\\"strscpy_pad mirrors strscpyPad padding semantics\\\"\", \"test \\\"strscpy and strscpyPad keep one-byte destinations terminated\\\"\", \"test \\\"memcpyAndPad copies the requested prefix and pads the destination tail\\\"\", \"test \\\"memcpy_and_pad mirrors memcpyAndPad padding semantics\\\"\", \"test \\\"strtomem copies a C-string prefix without adding a terminator or padding\\\"\", \"test \\\"strtomem_pad copies through the first NUL and pads the remaining tail\\\"\", \"test \\\"memtostr copies a bounded non-NUL source and adds one terminator\\\"\", \"test \\\"memtostr stops at embedded NUL without padding the tail\\\"\", \"test \\\"memtostrPad zero-pads the remaining tail after copying\\\"\", \"test \\\"memtostr helpers keep one-byte destinations terminated\\\"\", \"test \\\"streq matches C-string equality semantics\\\"\", \"test \\\"skip trim remove and replace spaces work in place\\\"\", \"test \\\"phase 1 string trim helpers stop at embedded NUL after trailing whitespace\\\"\", \"test \\\"strreplace mirrors replaceChar C-string semantics\\\"\", \"test \\\"strHasPrefix returns the matched prefix length with C-string semantics\\\"\", \"test \\\"strHasSuffix returns the matched suffix length with C-string semantics\\\"\", \"test \\\"strstarts mirrors the header-level prefix helper\\\"\", \"test \\\"strEndsWith honors C-string boundaries\\\"\", \"test \\\"prefix and suffix Linux-style aliases mirror the primary helpers\\\"\", \"test \\\"kbasename returns the final path component with C-string semantics\\\"\", \"test \\\"sysfsStreq treats trailing newline and NUL as equivalent\\\"\", \"test \\\"sysfs_streq mirrors sysfsStreq newline and NUL equivalence\\\"\", \"test \\\"sysfsMatchString finds newline-aware matches and preserves first-match order\\\"\", \"test \\\"sysfs_match_string mirrors sysfsMatchString for empty and matched lists\\\"\", \"test \\\"matchString finds C-string matches and preserves first-match order\\\"\", \"test \\\"match_string mirrors matchString for empty and matched lists\\\"\", \"test \\\"strcmp mirrors C-string lexical ordering\\\"\", \"test \\\"strcmp stops at embedded NULs and length mismatches\\\"\", \"test \\\"strncmp honors the count limit before later mismatches\\\"\", \"test \\\"strncmp stops at embedded NULs and shorter prefixes\\\"\", \"test \\\"strcasecmp ignores ASCII case and preserves lexical ordering\\\"\", \"test \\\"strcasecmp stops at embedded NULs and length mismatches\\\"\", \"test \\\"strncasecmp honors the count limit before later mismatches\\\"\", \"test \\\"strncasecmp stops at embedded NULs and shorter prefixes\\\"\", \"test \\\"strstr mirrors full-length C-string substring searches\\\"\", \"test \\\"strnstr honors count and C-string boundaries\\\"\", \"test \\\"memdup and memchrInv preserve byte content\\\"\", \"test \\\"memchr_inv mirrors memchrInv byte-search semantics\\\"\", \"test \\\"memchrInv keeps long-buffer first-dirty-byte results stable\\\"\", \"test \\\"memchrInv follows the earliest dirty byte as long buffers change\\\"\", \"test \\\"memchrInv dirty-word shortcut handles zero-value scans at word boundaries\\\"\", \"test \\\"memchrInv zero-value scans keep the earliest dirty byte across every prefix alignment\\\"\", \"test \\\"memchrInv keeps the earliest dirty byte for long non-zero scans across alignments\\\"\", \"test \\\"memchrInv keeps the earliest dirty byte for long zero-value scans across alignments\\\"\", \"test \\\"memchrInv short zero-value scans stay byte-accurate\\\"\", \"test \\\"memchrInv keeps the earliest dirty byte across the fast-path cutoff\\\"\", \"test \\\"memparse handles decimal hexadecimal octal and suffixes\\\"\", \"test \\\"memparse keeps original rest when sign is not followed by digits\\\"\", \"test \\\"memparse saturates signed overflow instead of trapping\\\"\", \"test \\\"memparse clamps explicit positive signed overflow\\\"\", \"test \\\"memparse keeps signed values and their trailing rest aligned\\\"\", \"test \\\"memparse consumes suffix after saturation\\\"\", \"test \\\"memparse applies suffixes before signed clamping\\\"\", \"test \\\"strchr mirrors full-length C-string searches\\\"\", \"test \\\"strrchr finds the last in-range match with C-string semantics\\\"\", \"test \\\"strchr and strrchr return the terminator index when searching for NUL\\\"\", \"test \\\"strpbrk finds the first accepted byte with C-string semantics\\\"\", \"test \\\"strspn counts the accepted prefix with C-string semantics\\\"\", \"test \\\"strcspn counts until the first rejected byte with C-string semantics\\\"\", \"test \\\"strnchr honors count and C-string boundaries\\\"\", \"test \\\"strlen honors C-string boundaries\\\"\", \"test \\\"strnlen honors count and C-string boundaries\\\"\", \"test \\\"strnchrNul returns the first match, NUL, or count boundary\\\"\", \"test \\\"strchrNul and strchrnul return the first match or terminator boundary\\\"\"]";
const EXPECTED_HELPER_LOCAL_ONLY_ANCHORS_JSON = "[\"test \\\"memchrInv keeps non-zero scans stable across the fast-path cutoff\\\"\", \"test \\\"memchrInv finds a dirty byte in the unaligned prefix before the word fast path\\\"\", \"test \\\"memchrInv keeps aligned word hits stable after consuming an unaligned prefix\\\"\"]";
const EXPECTED_HELPER_SOURCE_EQUIVALENT_ANCHORS_JSON = "{\"test \\\"strlcat appends within the destination size and reports the attempted length\\\"\": \"test \\\"strlcat appends only the C-string prefix from embedded-NUL sources\\\"\"}";
const EXPECTED_STRING_PACKET_JSON = "{\"helper_test_anchors\": [\"test \\\"strtobool accepts common Linux forms\\\"\", \"test \\\"strlcpy copies and returns the source length\\\"\", \"test \\\"strlcat appends within the destination size and reports the attempted length\\\"\", \"test \\\"strlcat truncates with a terminator and keeps the full attempted length\\\"\", \"test \\\"strlcat treats an unterminated destination as full\\\"\", \"test \\\"strlcat handles a zero-length destination buffer\\\"\", \"test \\\"strscpy keeps NUL termination and reports truncation with -E2BIG\\\"\", \"test \\\"strscpyPad zero-pads the tail after a short source\\\"\", \"test \\\"strscpyPad stops at embedded NUL and pads the remaining tail\\\"\", \"test \\\"strscpyPad preserves strscpy truncation semantics\\\"\", \"test \\\"strscpy_pad mirrors strscpyPad padding semantics\\\"\", \"test \\\"strscpy and strscpyPad keep one-byte destinations terminated\\\"\", \"test \\\"memcpyAndPad copies the requested prefix and pads the destination tail\\\"\", \"test \\\"memcpy_and_pad mirrors memcpyAndPad padding semantics\\\"\", \"test \\\"strtomem copies a C-string prefix without adding a terminator or padding\\\"\", \"test \\\"strtomem_pad copies through the first NUL and pads the remaining tail\\\"\", \"test \\\"memtostr copies a bounded non-NUL source and adds one terminator\\\"\", \"test \\\"memtostr stops at embedded NUL without padding the tail\\\"\", \"test \\\"memtostrPad zero-pads the remaining tail after copying\\\"\", \"test \\\"memtostr helpers keep one-byte destinations terminated\\\"\", \"test \\\"streq matches C-string equality semantics\\\"\", \"test \\\"skip trim remove and replace spaces work in place\\\"\", \"test \\\"phase 1 string trim helpers stop at embedded NUL after trailing whitespace\\\"\", \"test \\\"strreplace mirrors replaceChar C-string semantics\\\"\", \"test \\\"strHasPrefix returns the matched prefix length with C-string semantics\\\"\", \"test \\\"strHasSuffix returns the matched suffix length with C-string semantics\\\"\", \"test \\\"strstarts mirrors the header-level prefix helper\\\"\", \"test \\\"strEndsWith honors C-string boundaries\\\"\", \"test \\\"prefix and suffix Linux-style aliases mirror the primary helpers\\\"\", \"test \\\"kbasename returns the final path component with C-string semantics\\\"\", \"test \\\"sysfsStreq treats trailing newline and NUL as equivalent\\\"\", \"test \\\"sysfs_streq mirrors sysfsStreq newline and NUL equivalence\\\"\", \"test \\\"sysfsMatchString finds newline-aware matches and preserves first-match order\\\"\", \"test \\\"sysfs_match_string mirrors sysfsMatchString for empty and matched lists\\\"\", \"test \\\"matchString finds C-string matches and preserves first-match order\\\"\", \"test \\\"match_string mirrors matchString for empty and matched lists\\\"\", \"test \\\"strcmp mirrors C-string lexical ordering\\\"\", \"test \\\"strcmp stops at embedded NULs and length mismatches\\\"\", \"test \\\"strncmp honors the count limit before later mismatches\\\"\", \"test \\\"strncmp stops at embedded NULs and shorter prefixes\\\"\", \"test \\\"strcasecmp ignores ASCII case and preserves lexical ordering\\\"\", \"test \\\"strcasecmp stops at embedded NULs and length mismatches\\\"\", \"test \\\"strncasecmp honors the count limit before later mismatches\\\"\", \"test \\\"strncasecmp stops at embedded NULs and shorter prefixes\\\"\", \"test \\\"strstr mirrors full-length C-string substring searches\\\"\", \"test \\\"strnstr honors count and C-string boundaries\\\"\", \"test \\\"memdup and memchrInv preserve byte content\\\"\", \"test \\\"memchr_inv mirrors memchrInv byte-search semantics\\\"\", \"test \\\"memchrInv keeps long-buffer first-dirty-byte results stable\\\"\", \"test \\\"memchrInv follows the earliest dirty byte as long buffers change\\\"\", \"test \\\"memchrInv dirty-word shortcut handles zero-value scans at word boundaries\\\"\", \"test \\\"memchrInv zero-value scans keep the earliest dirty byte across every prefix alignment\\\"\", \"test \\\"memchrInv keeps the earliest dirty byte for long non-zero scans across alignments\\\"\", \"test \\\"memchrInv keeps the earliest dirty byte for long zero-value scans across alignments\\\"\", \"test \\\"memchrInv short zero-value scans stay byte-accurate\\\"\", \"test \\\"memchrInv keeps the earliest dirty byte across the fast-path cutoff\\\"\", \"test \\\"memparse handles decimal hexadecimal octal and suffixes\\\"\", \"test \\\"memparse keeps original rest when sign is not followed by digits\\\"\", \"test \\\"memparse saturates signed overflow instead of trapping\\\"\", \"test \\\"memparse clamps explicit positive signed overflow\\\"\", \"test \\\"memparse keeps signed values and their trailing rest aligned\\\"\", \"test \\\"memparse consumes suffix after saturation\\\"\", \"test \\\"memparse applies suffixes before signed clamping\\\"\", \"test \\\"strchr mirrors full-length C-string searches\\\"\", \"test \\\"strrchr finds the last in-range match with C-string semantics\\\"\", \"test \\\"strchr and strrchr return the terminator index when searching for NUL\\\"\", \"test \\\"strpbrk finds the first accepted byte with C-string semantics\\\"\", \"test \\\"strspn counts the accepted prefix with C-string semantics\\\"\", \"test \\\"strcspn counts until the first rejected byte with C-string semantics\\\"\", \"test \\\"strnchr honors count and C-string boundaries\\\"\", \"test \\\"strlen honors C-string boundaries\\\"\", \"test \\\"strnlen honors count and C-string boundaries\\\"\", \"test \\\"strnchrNul returns the first match, NUL, or count boundary\\\"\", \"test \\\"strchrNul and strchrnul return the first match or terminator boundary\\\"\"], \"memparse_review_anchors\": [\"test \\\"memparse handles decimal hexadecimal octal and suffixes\\\"\", \"test \\\"memparse keeps original rest when sign is not followed by digits\\\"\", \"test \\\"memparse saturates signed overflow instead of trapping\\\"\", \"test \\\"memparse clamps explicit positive signed overflow\\\"\", \"test \\\"memparse keeps signed values and their trailing rest aligned\\\"\", \"test \\\"memparse consumes suffix after saturation\\\"\", \"test \\\"memparse applies suffixes before signed clamping\\\"\"], \"memparse_review_summary\": \"helper-local memparse safety anchors stay explicit through the direct string tests so sign-prefixed invalid input preserves rest, signed inputs keep their trailing-rest split aligned with unsigned parsing, implicit and explicit signed overflow clamp instead of trapping, and suffixes are still consumed after saturation\", \"strlcat_review_anchors\": [\"test \\\"strlcat appends within the destination size and reports the attempted length\\\"\", \"test \\\"strlcat truncates with a terminator and keeps the full attempted length\\\"\", \"test \\\"strlcat treats an unterminated destination as full\\\"\", \"test \\\"strlcat handles a zero-length destination buffer\\\"\"], \"strlcat_review_summary\": \"helper-local strlcat truncation and destination-boundary anchors stay explicit through the direct string tests because the shared Phase 1 replay still does not carry dedicated strlcat() fixture keys, so append length reporting, truncation with a preserved terminator slot, unterminated-destination handling, and zero-length destination behavior remain review-visible at the helper surface\", \"copy_fill_review_anchors\": [\"test \\\"memcpyAndPad copies the requested prefix and pads the destination tail\\\"\", \"test \\\"memcpy_and_pad mirrors memcpyAndPad padding semantics\\\"\", \"test \\\"strtomem copies a C-string prefix without adding a terminator or padding\\\"\", \"test \\\"strtomem_pad copies through the first NUL and pads the remaining tail\\\"\"], \"copy_fill_review_summary\": \"helper-local raw-copy and pad anchors stay explicit through the direct string tests because the shared Phase 1 replay still does not carry dedicated memcpyAndPad(), memcpy_and_pad(), strtomem(), or strtomem_pad() fixture keys, so prefix-copy, first-NUL stop, alias parity, and caller-selected pad behavior remain review-visible at the helper surface\", \"memtostr_review_anchors\": [\"test \\\"memtostr copies a bounded non-NUL source and adds one terminator\\\"\", \"test \\\"memtostr stops at embedded NUL without padding the tail\\\"\", \"test \\\"memtostrPad zero-pads the remaining tail after copying\\\"\", \"test \\\"memtostr helpers keep one-byte destinations terminated\\\"\"], \"memtostr_review_summary\": \"helper-local memtostr boundary and tail-padding anchors stay explicit through the direct string tests because the shared Phase 1 replay still does not carry dedicated memtostr(), memtostrPad(), or memtostr_pad() fixture keys, so bounded source copies, embedded-NUL stops, terminator insertion, and zero-padded destination tails remain review-visible at the helper surface\", \"prefix_suffix_review_anchors\": [\"test \\\"strHasPrefix returns the matched prefix length with C-string semantics\\\"\", \"test \\\"strHasSuffix returns the matched suffix length with C-string semantics\\\"\", \"test \\\"strstarts mirrors the header-level prefix helper\\\"\", \"test \\\"strEndsWith honors C-string boundaries\\\"\", \"test \\\"prefix and suffix Linux-style aliases mirror the primary helpers\\\"\"], \"prefix_suffix_review_summary\": \"helper-local prefix and suffix boundary anchors stay explicit through the direct string tests because the shared Phase 1 replay still focuses on replaceChar and memchrInv parity rather than dedicated prefix or suffix fixture fields, so strHasPrefix and str_has_prefix plus strHasSuffix and str_has_suffix plus strstarts plus strEndsWith and str_ends_with plus strends remain review-visible at the helper surface\", \"lookup_review_anchors\": [\"test \\\"matchString finds C-string matches and preserves first-match order\\\"\", \"test \\\"match_string mirrors matchString for empty and matched lists\\\"\"], \"lookup_review_summary\": \"helper-local string lookup anchors stay explicit through the direct string tests because the shared Phase 1 replay still does not carry dedicated matchString() or match_string() fixture keys, so C-string list lookup order and the Linux-style alias remain review-visible at the helper surface\", \"sysfs_review_anchors\": [\"test \\\"sysfsStreq treats trailing newline and NUL as equivalent\\\"\", \"test \\\"sysfs_streq mirrors sysfsStreq newline and NUL equivalence\\\"\", \"test \\\"sysfsMatchString finds newline-aware matches and preserves first-match order\\\"\", \"test \\\"sysfs_match_string mirrors sysfsMatchString for empty and matched lists\\\"\"], \"sysfs_review_summary\": \"helper-local string sysfs newline-aware equality and lookup-order anchors stay explicit through the direct string tests because the shared Phase 1 replay still carries no dedicated sysfs fixture keys, so sysfsStreq and sysfs_streq plus sysfsMatchString and sysfs_match_string remain review-visible at the helper surface\", \"strscpy_review_anchors\": [\"test \\\"strscpy keeps NUL termination and reports truncation with -E2BIG\\\"\", \"test \\\"strscpyPad zero-pads the tail after a short source\\\"\", \"test \\\"strscpyPad stops at embedded NUL and pads the remaining tail\\\"\", \"test \\\"strscpyPad preserves strscpy truncation semantics\\\"\", \"test \\\"strscpy_pad mirrors strscpyPad padding semantics\\\"\", \"test \\\"strscpy and strscpyPad keep one-byte destinations terminated\\\"\"], \"strscpy_review_summary\": \"helper-local string copy-and-pad anchors stay explicit through the direct string tests because the shared Phase 1 replay still does not carry dedicated strscpy() or strscpyPad() fixture keys\", \"strcmp_review_anchors\": [\"test \\\"strcmp mirrors C-string lexical ordering\\\"\", \"test \\\"strcmp stops at embedded NULs and length mismatches\\\"\"], \"strcmp_review_summary\": \"helper-local lexical-compare anchors stay explicit through the direct string tests because the shared Phase 1 replay still does not carry dedicated strcmp() fixture keys, so lexical ordering and embedded-NUL length-mismatch behavior remain review-visible at the helper surface\", \"casecmp_review_anchors\": [\"test \\\"strcasecmp ignores ASCII case and preserves lexical ordering\\\"\", \"test \\\"strcasecmp stops at embedded NULs and length mismatches\\\"\", \"test \\\"strncasecmp honors the count limit before later mismatches\\\"\", \"test \\\"strncasecmp stops at embedded NULs and shorter prefixes\\\"\"], \"casecmp_review_summary\": \"helper-local ASCII case-folded compare anchors stay explicit through the direct string tests because the shared Phase 1 replay still does not carry dedicated strcasecmp() or strncasecmp() fixture keys, so case-insensitive lexical ordering, embedded-NUL boundaries, and counted-prefix behavior remain review-visible at the helper surface\", \"substring_search_review_anchors\": [\"test \\\"strstr mirrors full-length C-string substring searches\\\"\", \"test \\\"strnstr honors count and C-string boundaries\\\"\"], \"substring_search_review_summary\": \"helper-local substring-search anchors stay explicit through the direct string tests because the shared Phase 1 replay still does not carry dedicated strstr() or strnstr() fixture keys, so full-length and count-clamped substring boundaries remain review-visible at the helper surface\", \"search_length_review_anchors\": [\"test \\\"strchr mirrors full-length C-string searches\\\"\", \"test \\\"strrchr finds the last in-range match with C-string semantics\\\"\", \"test \\\"strchr and strrchr return the terminator index when searching for NUL\\\"\", \"test \\\"strlen honors C-string boundaries\\\"\", \"test \\\"strnlen honors count and C-string boundaries\\\"\", \"test \\\"strchrNul and strchrnul return the first match or terminator boundary\\\"\"], \"search_length_review_summary\": \"helper-local search-and-length boundary anchors stay explicit through the direct string tests because the shared Phase 1 replay still does not carry dedicated search-length fixture keys, so strchr() or strrchr() boundary scans, terminator-index searches, strchrNul() or strchrnul() match-or-terminator boundaries, and strlen() or strnlen() length boundaries remain review-visible at the helper surface\", \"strnchr_review_anchor\": \"test \\\"strnchr honors count and C-string boundaries\\\"\", \"counted_search_review_anchors\": [\"test \\\"strchr mirrors full-length C-string searches\\\"\", \"test \\\"strrchr finds the last in-range match with C-string semantics\\\"\", \"test \\\"strpbrk finds the first accepted byte with C-string semantics\\\"\", \"test \\\"strspn counts the accepted prefix with C-string semantics\\\"\", \"test \\\"strcspn counts until the first rejected byte with C-string semantics\\\"\", \"test \\\"strnchr honors count and C-string boundaries\\\"\", \"test \\\"strnlen honors count and C-string boundaries\\\"\", \"test \\\"strnchrNul returns the first match, NUL, or count boundary\\\"\", \"test \\\"strchrNul and strchrnul return the first match or terminator boundary\\\"\"], \"strnchrnul_review_anchor\": \"test \\\"strnchrNul returns the first match, NUL, or count boundary\\\"\", \"strchrnul_review_anchor\": \"test \\\"strchrNul and strchrnul return the first match or terminator boundary\\\"\", \"strnchr_review_summary\": \"the direct counted-search and C-string search-length follow-up stays explicit because the shared Phase 1 replay still does not carry dedicated counted-search or search-length fixture keys, so strchr() or strrchr() full-length C-string searches, strpbrk() first-accepted-byte scanning, strspn() accepted-prefix scanning, strcspn() rejected-byte scanning, strnchr() count-limited scanning, strnlen() count-clamped length, strnchrNul() or strnchrnul() match-or-NUL boundary behavior, and strchrNul() or strchrnul() match-or-terminator boundaries remain owned by the helper-local anchors\", \"basename_review_anchor\": \"test \\\"kbasename returns the final path component with C-string semantics\\\"\", \"basename_review_summary\": \"helper-local basename path-tail anchor stays explicit through the direct string tests because the shared Phase 1 replay still does not carry dedicated kbasename fixture keys, so final path-component extraction at the first C-string terminator remains review-visible at the helper surface\", \"trim_nul_review_anchor\": \"test \\\"phase 1 string trim helpers stop at embedded NUL after trailing whitespace\\\"\", \"trim_nul_review_summary\": \"the direct trim follow-up stays explicit because the shared Phase 1 string fixture records the trimmed bytes but not the preserved tail bytes beyond the first embedded terminator\", \"phase1_trim_cstr_replay_anchor\": \"test \\\"phase 1 string trim helpers stop at embedded NUL after trailing whitespace\\\"\", \"phase1_trim_cstr_replay_summary\": \"the shared Phase 1 string replay still only locks the plain trailing-whitespace trimSpaces bytes from the committed fixture, while the direct helper-local trim follow-up keeps embedded-NUL trimming for trimSpaces and strim plus strstrip and preserved tail-byte review explicit because the shared packet still does not exercise every trim alias or every post-NUL byte position\", \"memchr_moving_dirty_anchor\": \"test \\\"memchrInv follows the earliest dirty byte as long buffers change\\\"\", \"memchr_moving_dirty_review_summary\": \"the direct memchrInv follow-up stays explicit because the shared Phase 1 fixture pins one fixed dirty index and the clean case, but not the moving earliest-mismatch ownership as later dirty bytes become the next live divergence\", \"phase1_helper_replay_anchor\": \"test \\\"strreplace mirrors replaceChar C-string semantics\\\"\", \"shared_replace_char_cstr_review_summary\": \"the shared Phase 1 string replay now exercises strtobool, strlcpy, skipSpaces, trimSpaces, removeSpaces, replaceChar, and memchrInv fixture parity, while the dedicated embedded-NUL replaceChar follow-up keeps the first-terminator stop rule explicit without widening helper-local memparse ownership\", \"parity_fixture_keys\": [\"strtobool_y\", \"strtobool_on\", \"strtobool_zero\", \"strtobool_off\", \"strtobool_invalid\", \"strlcpy_len\", \"strlcpy_buffer\", \"skip_spaces\", \"trim_spaces\", \"remove_spaces\", \"replace_char\", \"replace_char_end\", \"replace_char_cstr_end\", \"replace_char_cstr_bytes\", \"memchr_inv_index\", \"memchr_inv_none\"], \"next_safe_step_note\": \"If this helper lane reopens, keep the helper-local strlcat, sysfs, case-insensitive compare, and match-or-terminator review anchors aligned across the string review packet and this lane note unless dedicated shared fixture keys land; do not reopen missing closure-side validator names by default.\"}";
const EXPECTED_STRING_FIXTURE_VALUES_JSON = "{\"strtobool_y\": true, \"strtobool_on\": true, \"strtobool_zero\": false, \"strtobool_off\": false, \"strtobool_invalid\": 184, \"strlcpy_len\": 5, \"strlcpy_buffer\": \"hel\", \"skip_spaces\": \"hello\", \"trim_spaces\": \"hi\", \"remove_spaces\": \"abc\", \"replace_char\": \"a_b\", \"replace_char_end\": 3, \"replace_char_cstr_end\": 2, \"replace_char_cstr_bytes\": [97, 95, 0, 45, 122], \"memchr_inv_index\": 4, \"memchr_inv_none\": true}";
const EXPECTED_STRING_LANE_MARKERS_JSON = "[[\"lane_direct_owner\", \"`PHASE1_STRING_DIRECT_OWNER=string keeps strscpy()/strscpyPad() copy-and-pad semantics, memparse safety, matched-prefix-length and suffix boundary, sysfs newline-aware equality and lookup order through sysfsStreq(), sysfs_streq(), sysfsMatchString(), and sysfs_match_string(), C-string list lookup through matchString() and match_string(), counted-search and search-length anchors through strpbrk(), strspn(), strcspn(), strnchr(), strnchrNul() or strnchrnul(), strchr(), strrchr(), strlen(), and strnlen(), embedded-NUL trim preservation, and moving-earliest-dirty-byte memchrInv coverage helper-local while the committed shared replay owns embedded-NUL replaceChar parity bytes and the current string fixture keys`\"], [\"lane_next_safe_step\", \"`PHASE1_STRING_NEXT_SAFE_STEP=string reopens only for direct-anchor drift inside strscpy()/strscpyPad() copy-and-pad semantics, memparse, matched-prefix-length or suffix boundary, sysfs newline-aware equality or lookup order, matchString()/match_string() C-string list lookup, counted-search and search-length anchors through strpbrk(), strspn(), strcspn(), strnchr(), strnchrNul() or strnchrnul(), strchr(), strrchr(), strlen(), and strnlen(), embedded-NUL trim, or moving-earliest-dirty-byte memchrInv coverage, or for committed replaceChar or current string fixture drift; keep the helper-local sysfs review anchors aligned across the string review packet and this lane note unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator names by default`\"], [\"lane_counted_search_match_or_nul\", \"- The counted-search owner term here also covers the current `strnchrNul()` and `strnchrnul()` match-or-NUL boundary anchor already cataloged in `zigux/tests/fixtures/phase1_helper_manifest.json`, so future string-only rereads should keep that helper-local boundary proof inside the same counted-search packet instead of treating it as an unowned follow-up beside `strnchr()`.\"], [\"lane_counted_search_strspn\", \"- the same counted-search packet now also keeps the direct `strspn()` accepted-prefix anchor review-visible on current `master`, so future string-only rereads should treat accepted-byte-prefix scanning as part of that helper-local search family instead of leaving it implicit beside `strpbrk()` and `strnchr()`.\"]]";

fn iterAnchorStrings(expected: std.json.Value, anchors: *std.ArrayList([]const u8), allocator: std.mem.Allocator) !void {
    switch (expected) {
        .string => |text| {
            if (std.mem.startsWith(u8, text, "test \"")) {
                try anchors.append(allocator, text);
            }
        },
        .array => |array| {
            for (array.items) |item| {
                if (item == .string and std.mem.startsWith(u8, item.string, "test \"")) {
                    try anchors.append(allocator, item.string);
                }
            }
        },
        else => {},
    }
}

fn requireAnchorOccurrence(
    allocator: std.mem.Allocator,
    failures: *std.ArrayList([]const u8),
    text: []const u8,
    label: []const u8,
    marker: []const u8,
    equivalents_json: []const u8,
) !void {
    const count = guard.countOccurrences(text, marker);
    if (count == 1) return;
    if (count == 0) {
        const equiv_parsed = guard.parseJsonValue(allocator, equivalents_json) catch {
            const issue = try std.fmt.allocPrint(allocator, "{s}:expected=1:actual=0", .{label});
            try failures.append(allocator, issue);
            return;
        };
        defer equiv_parsed.deinit();
        if (equiv_parsed.value == .object) {
            const equivalent = equiv_parsed.value.object.get(marker);
            if (equivalent) |eq| {
                if (eq == .string) {
                    const eq_count = guard.countOccurrences(text, eq.string);
                    if (eq_count == 1) return;
                    const issue = try std.fmt.allocPrint(allocator, "{s}:expected=1:actual=0:equivalent_actual={d}", .{ label, eq_count });
                    try failures.append(allocator, issue);
                    return;
                }
            }
        }
    }
    const issue = try std.fmt.allocPrint(allocator, "{s}:expected=1:actual={d}", .{ label, count });
    try failures.append(allocator, issue);
}

fn collectFailures(
    io: Io,
    allocator: std.mem.Allocator,
    root: []const u8,
) !std.ArrayList([]const u8) {
    var failures: std.ArrayList([]const u8) = .empty;
    errdefer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }

    for (&[_][]const u8{ STRING_HELPER_REL, STRING_MANIFEST_REL, STRING_FIXTURE_REL, STRING_LANE_NOTE_REL }) |relative_path| {
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    if (failures.items.len > 0) return failures;

    const helper_full_path = try guard.joinPath(allocator, root, STRING_HELPER_REL);
    defer allocator.free(helper_full_path);
    const helper_text = try guard.readUtf8File(io, allocator, helper_full_path);
    defer allocator.free(helper_text);
    const lane_full_path = try guard.joinPath(allocator, root, STRING_LANE_NOTE_REL);
    defer allocator.free(lane_full_path);
    const lane_text = try guard.readUtf8File(io, allocator, lane_full_path);
    defer allocator.free(lane_text);

    const manifest_full_path = try guard.joinPath(allocator, root, STRING_MANIFEST_REL);
    defer allocator.free(manifest_full_path);
    const manifest_text = try guard.readUtf8File(io, allocator, manifest_full_path);
    defer allocator.free(manifest_text);
    const manifest_parsed = guard.parseJsonValue(allocator, manifest_text) catch {
        const issue = try std.fmt.allocPrint(allocator, "manifest:invalid_json", .{});
        try failures.append(allocator, issue);
        return failures;
    };
    defer manifest_parsed.deinit();

    const fixture_full_path = try guard.joinPath(allocator, root, STRING_FIXTURE_REL);
    defer allocator.free(fixture_full_path);
    const fixture_text = try guard.readUtf8File(io, allocator, fixture_full_path);
    defer allocator.free(fixture_text);
    const fixture_parsed = guard.parseJsonValue(allocator, fixture_text) catch {
        const issue = try std.fmt.allocPrint(allocator, "fixture:invalid_json", .{});
        try failures.append(allocator, issue);
        return failures;
    };
    defer fixture_parsed.deinit();

    if (manifest_parsed.value != .object) {
        const issue = try std.fmt.allocPrint(allocator, "manifest:expected=dict:actual=non_object", .{});
        try failures.append(allocator, issue);
        return failures;
    }
    var manifest_dupes: std.ArrayList([]const u8) = .empty;
    defer {
        for (manifest_dupes.items) |item| allocator.free(item);
        manifest_dupes.deinit(allocator);
    }
    try guard.collectDuplicateJsonKeyPaths(allocator, manifest_parsed.value, "", &manifest_dupes);
    for (manifest_dupes.items) |path| {
        const issue = try std.fmt.allocPrint(allocator, "manifest:duplicate_json_key:{s}", .{path});
        try failures.append(allocator, issue);
    }
    if (manifest_dupes.items.len > 0) return failures;

    if (fixture_parsed.value != .object) {
        const issue = try std.fmt.allocPrint(allocator, "fixture:expected=dict:actual=non_object", .{});
        try failures.append(allocator, issue);
        return failures;
    }
    var fixture_dupes: std.ArrayList([]const u8) = .empty;
    defer {
        for (fixture_dupes.items) |item| allocator.free(item);
        fixture_dupes.deinit(allocator);
    }
    try guard.collectDuplicateJsonKeyPaths(allocator, fixture_parsed.value, "", &fixture_dupes);
    for (fixture_dupes.items) |path| {
        const issue = try std.fmt.allocPrint(allocator, "fixture:duplicate_json_key:{s}", .{path});
        try failures.append(allocator, issue);
    }
    if (fixture_dupes.items.len > 0) return failures;

    const symbols_parsed = try guard.parseJsonValue(allocator, EXPECTED_STRING_SOURCE_SYMBOLS_JSON);
    defer symbols_parsed.deinit();
    for (symbols_parsed.value.array.items) |symbol| {
        if (symbol != .string) continue;
        try guard.appendExactOccurrenceIssue(allocator, &failures, helper_text, try std.fmt.allocPrint(allocator, "string_source:{s}", .{symbol.string}), symbol.string);
    }

    const anchors_parsed = try guard.parseJsonValue(allocator, EXPECTED_HELPER_TEST_ANCHORS_JSON);
    defer anchors_parsed.deinit();
    var seen_anchors = std.StringHashMap(void).init(allocator);
    defer seen_anchors.deinit();
    for (anchors_parsed.value.array.items) |anchor| {
        if (anchor != .string) continue;
        const label = try std.fmt.allocPrint(allocator, "string_helper:{s}", .{anchor.string});
        defer allocator.free(label);
        try requireAnchorOccurrence(allocator, &failures, helper_text, label, anchor.string, EXPECTED_HELPER_SOURCE_EQUIVALENT_ANCHORS_JSON);
        _ = try seen_anchors.getOrPut(anchor.string);
    }

    const local_parsed = try guard.parseJsonValue(allocator, EXPECTED_HELPER_LOCAL_ONLY_ANCHORS_JSON);
    defer local_parsed.deinit();
    for (local_parsed.value.array.items) |anchor| {
        if (anchor != .string) continue;
        const label = try std.fmt.allocPrint(allocator, "string_helper_local:{s}", .{anchor.string});
        defer allocator.free(label);
        try guard.appendExactOccurrenceIssue(allocator, &failures, helper_text, label, anchor.string);
        _ = try seen_anchors.getOrPut(anchor.string);
    }

    const packet_parsed = try guard.parseJsonValue(allocator, EXPECTED_STRING_PACKET_JSON);
    defer packet_parsed.deinit();
    if (packet_parsed.value == .object) {
        var packet_it = packet_parsed.value.object.iterator();
        while (packet_it.next()) |entry| {
            if (std.mem.eql(u8, entry.key_ptr.*, "helper_test_anchors")) continue;
            var extra_anchors: std.ArrayList([]const u8) = .empty;
            defer extra_anchors.deinit(allocator);
            try iterAnchorStrings(entry.value_ptr.*, &extra_anchors, allocator);
            for (extra_anchors.items) |anchor| {
                if (seen_anchors.contains(anchor)) continue;
                const label = try std.fmt.allocPrint(allocator, "string_helper_packet:{s}", .{entry.key_ptr.*});
                defer allocator.free(label);
                try guard.appendExactOccurrenceIssue(allocator, &failures, helper_text, label, anchor);
                _ = try seen_anchors.getOrPut(anchor);
            }
        }
    }

    const lane_parsed = try guard.parseJsonValue(allocator, EXPECTED_STRING_LANE_MARKERS_JSON);
    defer lane_parsed.deinit();
    for (lane_parsed.value.array.items) |entry| {
        if (entry != .array or entry.array.items.len != 2) continue;
        const label_item = entry.array.items[0];
        const marker_item = entry.array.items[1];
        if (label_item != .string or marker_item != .string) continue;
        const label = try std.fmt.allocPrint(allocator, "string_lane:{s}", .{label_item.string});
        defer allocator.free(label);
        try guard.appendExactOccurrenceIssue(allocator, &failures, lane_text, label, marker_item.string);
    }

    const helper_test_expected = anchors_parsed.value;
    const helper_test_actual = guard.nestedJsonValue(manifest_parsed.value, &[_][]const u8{ "review_anchors", "tools/lib/string.zig", "helper_test_anchors" });
    if (helper_test_actual == null or !guard.jsonValuesEqual(helper_test_actual.?, helper_test_expected)) {
        try guard.appendJsonValueMismatch(allocator, &failures, "string_manifest:review_anchors.tools/lib/string.zig.helper_test_anchors", helper_test_actual, "{any}", .{helper_test_expected});
    }

    if (packet_parsed.value == .object) {
        var packet_it2 = packet_parsed.value.object.iterator();
        while (packet_it2.next()) |entry| {
            if (std.mem.eql(u8, entry.key_ptr.*, "helper_test_anchors")) continue;
            const label = try std.fmt.allocPrint(allocator, "string_manifest:review_anchors.tools/lib/string.zig.{s}", .{entry.key_ptr.*});
            defer allocator.free(label);
            const actual = guard.nestedJsonValue(manifest_parsed.value, &[_][]const u8{ "review_anchors", "tools/lib/string.zig", entry.key_ptr.* });
            if (actual == null or !guard.jsonValuesEqual(actual.?, entry.value_ptr.*)) {
                try guard.appendJsonValueMismatch(allocator, &failures, label, actual, "{any}", .{entry.value_ptr.*});
            }
        }
    }

    const string_fixture = fixture_parsed.value.object.get("string");
    if (string_fixture == null or string_fixture.? != .object) {
        const issue = try std.fmt.allocPrint(allocator, "string_fixture:expected=dict:actual=missing", .{});
        try failures.append(allocator, issue);
        return failures;
    }
    const fixture_expected_parsed = try guard.parseJsonValue(allocator, EXPECTED_STRING_FIXTURE_VALUES_JSON);
    defer fixture_expected_parsed.deinit();
    if (fixture_expected_parsed.value == .object) {
        var fit = fixture_expected_parsed.value.object.iterator();
        while (fit.next()) |entry| {
            const actual = string_fixture.?.object.get(entry.key_ptr.*);
            if (actual == null or !guard.jsonValuesEqual(actual.?, entry.value_ptr.*)) {
                const label = try std.fmt.allocPrint(allocator, "string_fixture:{s}", .{entry.key_ptr.*});
                defer allocator.free(label);
                try guard.appendJsonValueMismatch(allocator, &failures, label, actual, "{any}", .{entry.value_ptr.*});
            }
        }
    }

    return failures;
}

pub fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    _ = .{ io, allocator };
    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_STRING_REVIEW_PACKET_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var explicit_root: ?[]const u8 = null;
    var self_test = false;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    const root = if (explicit_root) |value| value else try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);

    var failures = try collectFailures(io, allocator, root);
    defer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }

    if (failures.items.len > 0) {
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "phase1-string-review-packet:ok", .{});
    std.process.exit(0);
}
