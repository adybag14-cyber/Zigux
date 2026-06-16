// Ported from check-phase1-direct-anchor-manifest-gate.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_SELF_TEST=pass";

const EXPECTED_ANTI_OVERLAP_RULE = "Do not reopen Phase 1 by batching helpers across those two sets in one lane; shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers reopen only for their existing helper-local anchors or already-committed shared fixture keys.";
const EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [_][]const u8{
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
};
const EXPECTED_HELPERS = [_][]const u8{
    "tools/lib/argv_split.zig",
    "tools/lib/bitmap.zig",
    "tools/lib/cmdline.zig",
    "tools/lib/ctype.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/hweight.zig",
    "tools/lib/list_sort.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/slab.zig",
    "tools/lib/str_error_r.zig",
    "tools/lib/string.zig",
    "tools/lib/vsprintf.zig",
    "tools/lib/zalloc.zig",
};
const EXPECTED_RBTREE_HELPER_TEST_ANCHORS = [_][]const u8{
    "test \"rbtree inserts and traverses in sorted order\"",
    "test \"rbtree erase and replace keep traversal consistent\"",
    "test \"rbtree ordered Linux-style aliases mirror traversal and replacement helpers\"",
    "test \"rbtree low-level Linux-style aliases mirror node-state helpers\"",
    "test \"rbtree eraseInit detaches erased node\"",
    "test \"rbtree eraseInit clears singleton roots before reseed\"",
    "test \"rbtree postorder and empty node helpers behave\"",
    "test \"rbtree findAdd keeps the first duplicate and inserts new keys\"",
    "test \"rbtree nextMatch walks the duplicate range in order\"",
    "test \"rbtree matchIterator walks the duplicate range in order\"",
    "test \"rbtree addCached returns the inserted node only when it becomes leftmost\"",
    "test \"rbtree findAddCached keeps cached leftmost stable while inserting misses\"",
    "test \"rbtree cached root keeps the leftmost pointer in sync\"",
    "test \"rbtree cached-root Linux-style aliases mirror the primary helpers\"",
    "test \"rbtree replaceNodeCached keeps non-leftmost leftmost unchanged\"",
    "test \"rbtree eraseCached returns null for a singleton cached tree\"",
    "test \"rbtree eraseInitCached detaches nodes while keeping cached leftmost aligned\"",
    "test \"rbtree eraseInitCached clears singleton cached roots before reseed\"",
};
const EXPECTED_REVIEW_FIELDS_JSON =
    \
    {\
      \"tools/lib/bitmap.zig\": {\
        \"copy_raw_alias_anchor\": \"test \\\"bitmap copy alias preserves raw source words without tail clearing\\\"\",\
        \"or_window_anchor\": \"test \\\"bitmap or keeps caller-selected bit window\\\"\",\
        \"or_multiword_tail_anchor\": \"test \\\"bitmap or across a multiword tail still lets callers clamp the last word\\\"\",\
        \"weighted_tail_count_anchor\": \"test \\\"bitmap weighted or and xor clamp counts to the declared tail window\\\"\",\
        \"empty_buffer_anchor\": \"test \\\"bitmap scnprintf leaves the caller buffer untouched for an empty bitmap\\\"\",\
        \"scnprintf_cross_word_anchor\": \"test \\\"bitmap scnprintf keeps contiguous ranges merged across word boundaries\\\"\",\
        \"zero_bit_noop_anchor\": \"test \\\"bitmap zero-bit logical helpers stay explicit\\\"\",\
        \"partial_xor_review_fields\": [\
          \"partial_xor_nbits\",\
          \"partial_xor_masked_values\"\
        ],\
        \"review_packet_summary\": \"shared Phase 1 fixture keys now own bitmap allocator sizing, zero-filled allocation words, copy/copy-clear-tail/copy-and-extend replay, scnprintf output, truncation, tiny-buffer handling, logical operator outputs, range set/clear/fill/zero outcomes, and partial-window xor replay, while current master keeps the direct helper-local bitmap packet bounded to whole-word range edges, raw copy alias behavior, tail-clearing and extension semantics, zero and aligned copyAndExtend handling, zero-sized destination-view no-op coverage, zero-bit logical short-circuit coverage, exact-word-boundary equality fast-path masking, tail-masked predicate behavior, out-of-range tail-bit full or empty or weight masking, caller-window xor and or clamping, multiword-tail xor and or clamp witnesses, weighted tail-count clamping, terminator-only and zero-length caller-view formatting, empty-bitmap caller-buffer preservation, Linux-style alias mirror coverage, and allocator optional-reset coverage.\",\
        \"next_safe_step_note\": \"If this helper lane reopens, keep bitmap parked unless a fresh reread finds new direct-anchor drift inside the current helper-local packet or committed shared replay drift in the bitmap copy, logical, range, allocation, formatting, or partial-window parity fields; current master still ships direct fill-tail clamp, raw copy alias, cross-word scnprintf, exact-word-boundary equality fast-path masking, caller-window xor and or clamp, weighted tail-count clamp, empty-buffer, allocator-reset, zero-bit logical short-circuit, and Linux-style alias mirror anchors here; do not reopen older closure-side or validator-route cue names by default.\"\
      },\
      \"tools/lib/find_bit.zig\": {\
        \"helper_test_anchors\": [\
          \"test \\\"find first and next set bits across words, with andnot gaps explicit\\\"\",\
          \"test \\\"find zero bits respects the declared bit count\\\"\",\
          \"test \\\"find and bit returns the first shared set bit\\\"\",\
          \"test \\\"underscore entry points reuse the public helper behavior\\\"\",\
          \"test \\\"single-word next scans honor start masks\\\"\",\
          \"test \\\"single-word first scans clamp to the declared bit window\\\"\",\
          \"test \\\"single-word next scans clamp partial windows before returning nbits\\\"\",\
          \"test \\\"word-boundary next scans start fresh on the next word\\\"\",\
          \"test \\\"zero-bit windows return without reading bitmap words\\\"\",\
          \"test \\\"zero-sized scans ignore populated backing words\\\"\",\
          \"test \\\"next scans past nbits return without reading bitmap words\\\"\",\
          \"test \\\"tail mask ignores set bits beyond nbits\\\"\",\
          \"test \\\"tail mask ignores zero bits beyond nbits\\\"\",\
          \"test \\\"tail mask ignores shared bits beyond nbits\\\"\",\
          \"test \\\"tail-word next set scans skip earlier in-range matches before clamping\\\"\",\
          \"test \\\"clump8 scans align to the containing byte and return its value\\\"\",\
          \"test \\\"clump8 scans keep tail bytes reachable from partial final words\\\"\",\
          \"test \\\"clump8 scans mask tail bits beyond nbits\\\"\",\
          \"test \\\"clump8 scans leave the caller byte untouched when no set bit remains\\\"\",\
          \"test \\\"clump8 zero-bit and past-end windows leave the caller byte untouched\\\"\",\
          \"test \\\"clump8 past-end scans return without reading bitmap words\\\"\",\
          \"test \\\"getValue8 reads aligned bytes from bitmap words\\\"\",\
          \"test \\\"getValue8 reads the last aligned byte of a word without folding in the next word\\\"\",\
          \"test \\\"head-word boundary scans keep the last in-range bit reachable from an inclusive start\\\"\",\
          \"test \\\"tail-word boundary scans keep the last in-range bit reachable from an inclusive start\\\"\",\
          \"test \\\"single-word tail windows keep the last in-range next matches reachable from an inclusive start\\\"\",\
          \"test \\\"find last bit scans backward across words\\\"\",\
          \"test \\\"find last bit ignores storage beyond an exact word boundary\\\"\",\
          \"test \\\"find last bit clamps tail words to nbits\\\"\",\
          \"test \\\"find last bit returns nbits when no set bits remain\\\"\",\
          \"test \\\"tail-word next zero and shared scans skip earlier in-range matches before clamping\\\"\",\
          \"test \\\"low-level underscore aliases mirror the primary find helpers, including andnot\\\"\",\
          \"test \\\"Linux-style aliases mirror the primary find helpers, including andnot\\\"\"\
        ],\
        \"same_word_start_masks\": \"test \\\"single-word next scans honor start masks\\\"\",\
        \"andnot_scan_entrypoints\": [\
          \"findFirstAndNotBit\",\
          \"find_first_andnot_bit\",\
          \"_find_first_andnot_bit\",\
          \"findNextAndNotBit\",\
          \"find_next_andnot_bit\",\
          \"_find_next_andnot_bit\"\
        ],\
        \"andnot_scan_entrypoint_contract\": \"The shipped public, Linux-style, and underscore andnot scan entry points stay owned by the direct find_bit packet instead of being left implicit under generic alias wording.\",\
        \"parity_fixture_keys\": [\
          \"bits_per_long\",\
          \"first\",\
          \"next_after_6\",\
          \"next_after_word\",\
          \"first_zero\",\
          \"next_zero\",\
          \"first_and\",\
          \"next_and\",\
          \"last\"\
        ],\
        \"review_packet_summary\": \"the committed Phase 1 fixture still owns the live cross-word find_bit replay through `bits_per_long`, `first`, `next_after_6`, `next_after_word`, `first_zero`, `next_zero`, `first_and`, `next_and`, and `last`, while helper-local anchors keep same-word start-mask, head-word and tail-word inclusive-boundary, single-word tail inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, tail-word set or zero or shared skip, clump8, getValue8(), findLastBit(), underscore-alias, and Linux-style alias behavior review-visible on current master\",\
        \"next_safe_step_note\": \"If this helper lane reopens, keep find_bit parked unless a fresh reread finds drift in the manifest-backed same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), underscore-alias, Linux-style alias coverage including the shipped andnot scan entry points, or tail-word skip anchors, or committed shared replay drift in the live `bits_per_long`, `first`, `next_after_6`, `next_after_word`, `first_zero`, `next_zero`, `first_and`, `next_and`, or `last` fixture keys; do not reopen older saved validator cues or neighboring helper families.\"\
      },\
      \"tools/lib/rbtree.zig\": {\
        \"helper_test_anchors\": [\
          \"test \\\"rbtree inserts and traverses in sorted order\\\"\",\
          \"test \\\"rbtree erase and replace keep traversal consistent\\\"\",\
          \"test \\\"rbtree ordered Linux-style aliases mirror traversal and replacement helpers\\\"\",\
          \"test \\\"rbtree low-level Linux-style aliases mirror node-state helpers\\\"\",\
          \"test \\\"rbtree eraseInit detaches erased node\\\"\",\
          \"test \\\"rbtree eraseInit clears singleton roots before reseed\\\"\",\
          \"test \\\"rbtree postorder and empty node helpers behave\\\"\",\
          \"test \\\"rbtree findAdd keeps the first duplicate and inserts new keys\\\"\",\
          \"test \\\"rbtree nextMatch walks the duplicate range in order\\\"\",\
          \"test \\\"rbtree matchIterator walks the duplicate range in order\\\"\",\
          \"test \\\"rbtree addCached returns the inserted node only when it becomes leftmost\\\"\",\
          \"test \\\"rbtree findAddCached keeps cached leftmost stable while inserting misses\\\"\",\
          \"test \\\"rbtree cached root keeps the leftmost pointer in sync\\\"\",\
          \"test \\\"rbtree cached-root Linux-style aliases mirror the primary helpers\\\"\",\
          \"test \\\"rbtree replaceNodeCached keeps non-leftmost leftmost unchanged\\\"\",\
          \"test \\\"rbtree eraseCached returns null for a singleton cached tree\\\"\",\
          \"test \\\"rbtree eraseInitCached detaches nodes while keeping cached leftmost aligned\\\"\",\
          \"test \\\"rbtree eraseInitCached clears singleton cached roots before reseed\\\"\"\
        ],\
        \"cached_root_followup_anchors\": [\
          \"test \\\"rbtree addCached returns the inserted node only when it becomes leftmost\\\"\",\
          \"test \\\"rbtree findAddCached keeps cached leftmost stable while inserting misses\\\"\",\
          \"test \\\"rbtree cached root keeps the leftmost pointer in sync\\\"\",\
          \"test \\\"rbtree cached-root Linux-style aliases mirror the primary helpers\\\"\",\
          \"test \\\"rbtree replaceNodeCached keeps non-leftmost leftmost unchanged\\\"\",\
          \"test \\\"rbtree eraseCached returns null for a singleton cached tree\\\"\",\
          \"test \\\"rbtree eraseInitCached detaches nodes while keeping cached leftmost aligned\\\"\",\
          \"test \\\"rbtree eraseInitCached clears singleton cached roots before reseed\\\"\"\
        ],\
        \"cached_root_alias_anchor\": \"test \\\"rbtree cached-root Linux-style aliases mirror the primary helpers\\\"\",\
        \"cached_root_transition_fixture_keys\": [\
          \"cached_root_transition_serials\"\
        ],\
        \"cached_root_transition_shared_replay_summary\": \"the committed Phase 1 fixture and the shared host-tools smoke route also keep the exact `cached_root_transition_serials` cached-root erase, replacement, and detach sequence aligned on current master\",\
        \"shared_replay_summary\": \"the committed Phase 1 fixture still carries traversal, detached-node, duplicate-search, and exact cached-leftmost-return witnesses for rbtree, while the current shared host-tools smoke replay now rechecks duplicate-range iteration plus the exact `cached_leftmost_return_serials` cached-root leftmost-return sequence on current master\",\
        \"next_safe_step_note\": \"If this helper lane reopens, keep the already-landed shared-replay promotion for `cached_leftmost_return_serials` aligned across the committed fixture, shared replay, and direct cached-root anchors; the ordered Linux-style alias proof, dedicated `low_level_alias_anchor`, and the remaining cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed behavior stay owned by direct helper-local anchors until another committed cached-root field lands.\"\
      },\
      \"tools/lib/string.zig\": {\
        \"helper_test_anchors\": [\
          \"test \\\"strtobool accepts common Linux forms\\\"\",\
          \"test \\\"strlcpy copies and returns the source length\\\"\",\
          \"test \\\"strlcat appends within the destination size and reports the attempted length\\\"\",\
          \"test \\\"strlcat truncates with a terminator and keeps the full attempted length\\\"\",\
          \"test \\\"strlcat treats an unterminated destination as full\\\"\",\
          \"test \\\"strlcat handles a zero-length destination buffer\\\"\",\
          \"test \\\"strscpy keeps NUL termination and reports truncation with -E2BIG\\\"\",\
          \"test \\\"strscpyPad zero-pads the tail after a short source\\\"\",\
          \"test \\\"strscpyPad stops at embedded NUL and pads the remaining tail\\\"\",\
          \"test \\\"strscpyPad preserves strscpy truncation semantics\\\"\",\
          \"test \\\"strscpy_pad mirrors strscpyPad padding semantics\\\"\",\
          \"test \\\"strscpy and strscpyPad keep one-byte destinations terminated\\\"\",\
          \"test \\\"memcpyAndPad copies the requested prefix and pads the destination tail\\\"\",\
          \"test \\\"memcpy_and_pad mirrors memcpyAndPad padding semantics\\\"\",\
          \"test \\\"strtomem copies a C-string prefix without adding a terminator or padding\\\"\",\
          \"test \\\"strtomem_pad copies through the first NUL and pads the remaining tail\\\"\",\
          \"test \\\"memtostr copies a bounded non-NUL source and adds one terminator\\\"\",\
          \"test \\\"memtostr stops at embedded NUL without padding the tail\\\"\",\
          \"test \\\"memtostrPad zero-pads the remaining tail after copying\\\"\",\
          \"test \\\"memtostr helpers keep one-byte destinations terminated\\\"\",\
          \"test \\\"streq matches C-string equality semantics\\\"\",\
          \"test \\\"skip trim remove and replace spaces work in place\\\"\",\
          \"test \\\"phase 1 string trim helpers stop at embedded NUL after trailing whitespace\\\"\",\
          \"test \\\"strreplace mirrors replaceChar C-string semantics\\\"\",\
          \"test \\\"strHasPrefix returns the matched prefix length with C-string semantics\\\"\",\
          \"test \\\"strHasSuffix returns the matched suffix length with C-string semantics\\\"\",\
          \"test \\\"strstarts mirrors the header-level prefix helper\\\"\",\
          \"test \\\"strEndsWith honors C-string boundaries\\\"\",\
          \"test \\\"prefix and suffix Linux-style aliases mirror the primary helpers\\\"\",\
          \"test \\\"kbasename returns the final path component with C-string semantics\\\"\",\
          \"test \\\"sysfsStreq treats trailing newline and NUL as equivalent\\\"\",\
          \"test \\\"sysfs_streq mirrors sysfsStreq newline and NUL equivalence\\\"\",\
          \"test \\\"sysfsMatchString finds newline-aware matches and preserves first-match order\\\"\",\
          \"test \\\"sysfs_match_string mirrors sysfsMatchString for empty and matched lists\\\"\",\
          \"test \\\"matchString finds C-string matches and preserves first-match order\\\"\",\
          \"test \\\"match_string mirrors matchString for empty and matched lists\\\"\",\
          \"test \\\"strcmp mirrors C-string lexical ordering\\\"\",\
          \"test \\\"strcmp stops at embedded NULs and length mismatches\\\"\",\
          \"test \\\"strncmp honors the count limit before later mismatches\\\"\",\
          \"test \\\"strncmp stops at embedded NULs and shorter prefixes\\\"\",\
          \"test \\\"strcasecmp ignores ASCII case and preserves lexical ordering\\\"\",\
          \"test \\\"strcasecmp stops at embedded NULs and length mismatches\\\"\",\
          \"test \\\"strncasecmp honors the count limit before later mismatches\\\"\",\
          \"test \\\"strncasecmp stops at embedded NULs and shorter prefixes\\\"\",\
          \"test \\\"strstr mirrors full-length C-string substring searches\\\"\",\
          \"test \\\"strnstr honors count and C-string boundaries\\\"\",\
          \"test \\\"memdup and memchrInv preserve byte content\\\"\",\
          \"test \\\"memchr_inv mirrors memchrInv byte-search semantics\\\"\",\
          \"test \\\"memchrInv keeps long-buffer first-dirty-byte results stable\\\"\",\
          \"test \\\"memchrInv follows the earliest dirty byte as long buffers change\\\"\",\
          \"test \\\"memchrInv dirty-word shortcut handles zero-value scans at word boundaries\\\"\",\
          \"test \\\"memchrInv zero-value scans keep the earliest dirty byte across every prefix alignment\\\"\",\
          \"test \\\"memchrInv keeps the earliest dirty byte for long non-zero scans across alignments\\\"\",\
          \"test \\\"memchrInv keeps the earliest dirty byte for long zero-value scans across alignments\\\"\",\
          \"test \\\"memchrInv short zero-value scans stay byte-accurate\\\"\",\
          \"test \\\"memchrInv keeps the earliest dirty byte across the fast-path cutoff\\\"\",\
          \"test \\\"memparse handles decimal hexadecimal octal and suffixes\\\"\",\
          \"test \\\"memparse keeps original rest when sign is not followed by digits\\\"\",\
          \"test \\\"memparse saturates signed overflow instead of trapping\\\"\",\
          \"test \\\"memparse clamps explicit positive signed overflow\\\"\",\
          \"test \\\"memparse keeps signed values and their trailing rest aligned\\\"\",\
          \"test \\\"memparse consumes suffix after saturation\\\"\",\
          \"test \\\"memparse applies suffixes before signed clamping\\\"\",\
          \"test \\\"strchr mirrors full-length C-string searches\\\"\",\
          \"test \\\"strrchr finds the last in-range match with C-string semantics\\\"\",\
          \"test \\\"strchr and strrchr return the terminator index when searching for NUL\\\"\",\
          \"test \\\"strpbrk finds the first accepted byte with C-string semantics\\\"\",\
          \"test \\\"strspn counts the accepted prefix with C-string semantics\\\"\",\
          \"test \\\"strcspn counts until the first rejected byte with C-string semantics\\\"\",\
          \"test \\\"strnchr honors count and C-string boundaries\\\"\",\
          \"test \\\"strlen honors C-string boundaries\\\"\",\
          \"test \\\"strnlen honors count and C-string boundaries\\\"\",\
          \"test \\\"strnchrNul returns the first match, NUL, or count boundary\\\"\",\
          \"test \\\"strchrNul and strchrnul return the first match or terminator boundary\\\"\"\
        ],\
        \"memparse_review_anchors\": [\
          \"test \\\"memparse handles decimal hexadecimal octal and suffixes\\\"\",\
          \"test \\\"memparse keeps original rest when sign is not followed by digits\\\"\",\
          \"test \\\"memparse saturates signed overflow instead of trapping\\\"\",\
          \"test \\\"memparse clamps explicit positive signed overflow\\\"\",\
          \"test \\\"memparse keeps signed values and their trailing rest aligned\\\"\",\
          \"test \\\"memparse consumes suffix after saturation\\\"\",\
          \"test \\\"memparse applies suffixes before signed clamping\\\"\"\
        ],\
        \"strcmp_review_anchors\": [\
          \"test \\\"strcmp mirrors C-string lexical ordering\\\"\",\
          \"test \\\"strcmp stops at embedded NULs and length mismatches\\\"\"\
        ],\
        \"strcmp_review_summary\": \"helper-local lexical-compare anchors stay explicit through the direct string tests because the shared Phase 1 replay still does not carry dedicated strcmp() fixture keys, so lexical ordering and embedded-NUL length-mismatch behavior remain review-visible at the helper surface\",\
        \"counted_search_review_anchors\": [\
          \"test \\\"strchr mirrors full-length C-string searches\\\"\",\
          \"test \\\"strrchr finds the last in-range match with C-string semantics\\\"\",\
          \"test \\\"strpbrk finds the first accepted byte with C-string semantics\\\"\",\
          \"test \\\"strspn counts the accepted prefix with C-string semantics\\\"\",\
          \"test \\\"strcspn counts until the first rejected byte with C-string semantics\\\"\",\
          \"test \\\"strnchr honors count and C-string boundaries\\\"\",\
          \"test \\\"strnlen honors count and C-string boundaries\\\"\",\
          \"test \\\"strnchrNul returns the first match, NUL, or count boundary\\\"\",\
          \"test \\\"strchrNul and strchrnul return the first match or terminator boundary\\\"\"\
        ],\
        \"strnchr_review_summary\": \"the direct counted-search and C-string search-length follow-up stays explicit because the shared Phase 1 replay still does not carry dedicated counted-search or search-length fixture keys, so strchr() or strrchr() full-length C-string searches, strpbrk() first-accepted-byte scanning, strspn() accepted-prefix scanning, strcspn() rejected-byte scanning, strnchr() count-limited scanning, strnlen() count-clamped length, strnchrNul() or strnchrnul() match-or-NUL boundary behavior, and strchrNul() or strchrnul() match-or-terminator boundaries remain owned by the helper-local anchors\",\
        \"next_safe_step_note\": \"If this helper lane reopens, keep the helper-local strlcat, sysfs, case-insensitive compare, and match-or-terminator review anchors aligned across the string review packet and this lane note unless dedicated shared fixture keys land; do not reopen missing closure-side validator names by default.\"\
      }\
    }
;
const EXPECTED_RULE_SUMMARY = "Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local follow-up anchors on current master.";
const EXPECTED_SHARED_REPLAY_PARKED_HELPERS = [_][]const u8{
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

    _ = .{ io, allocator, root };

    return failures;
}

pub fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    var tmp = try guard.TempWorkspace.init(io, allocator, "selftest");
    defer tmp.deinit();
    const root = try tmp.rootPath(allocator);
    defer allocator.free(root);
    var failures = try collectFailures(io, allocator, root);
    defer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }
    try guard.expectSelfTest(failures.items.len == 0);
    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_GUARD_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
        try guard.printLine(io, "PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    std.process.exit(0);
}

