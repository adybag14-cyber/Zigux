// Ported from check-phase1-direct-owner-markers.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_DIRECT_OWNER_MARKERS_SELF_TEST=pass";

const BITMAP_HELPER_REL = "tools/lib/bitmap.zig";

const DOCS_ROOT_REL = "Documentation/zigux/README.md";

const EXPECTED_ANTI_OVERLAP_RULE = "Do not reopen Phase 1 by batching helpers across those two sets in one lane; shared-replay parked helpers reopen only for packet drift, while direct-anchor helpers reopen only for their existing helper-local anchors or already-committed shared fixture keys.";

const EXPECTED_BITMAP_NEXT_SAFE_STEP_NOTE = "If this helper lane reopens, keep bitmap parked unless a fresh reread finds new direct-anchor drift inside the current helper-local packet or committed shared replay drift in the bitmap copy, logical, range, allocation, formatting, or partial-window parity fields; current master still ships direct fill-tail clamp, raw copy alias, cross-word scnprintf, exact-word-boundary equality fast-path masking, caller-window xor and or clamp, weighted tail-count clamp, empty-buffer, allocator-reset, zero-bit logical short-circuit, and Linux-style alias mirror anchors here; do not reopen older closure-side or validator-route cue names by default.";

const EXPECTED_BITMAP_REVIEW_PACKET_SUMMARY = "shared Phase 1 fixture keys now own bitmap allocator sizing, zero-filled allocation words, copy/copy-clear-tail/copy-and-extend replay, scnprintf output, truncation, tiny-buffer handling, logical operator outputs, range set/clear/fill/zero outcomes, and partial-window xor replay, while current master keeps the direct helper-local bitmap packet bounded to whole-word range edges, raw copy alias behavior, tail-clearing and extension semantics, zero and aligned copyAndExtend handling, zero-sized destination-view no-op coverage, zero-bit logical short-circuit coverage, exact-word-boundary equality fast-path masking, tail-masked predicate behavior, out-of-range tail-bit full or empty or weight masking, caller-window xor and or clamping, multiword-tail xor and or clamp witnesses, weighted tail-count clamping, terminator-only and zero-length caller-view formatting, empty-bitmap caller-buffer preservation, Linux-style alias mirror coverage, and allocator optional-reset coverage.";

const EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [_][]const u8{
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
};

const EXPECTED_FIND_BIT_ANDNOT_SCAN_ENTRYPOINTS = [_][]const u8{
    "findFirstAndNotBit",
    "find_first_andnot_bit",
    "_find_first_andnot_bit",
    "findNextAndNotBit",
    "find_next_andnot_bit",
    "_find_next_andnot_bit",
};

const EXPECTED_FIND_BIT_ANDNOT_SCAN_ENTRYPOINT_CONTRACT = "The shipped public, Linux-style, and underscore andnot scan entry points stay owned by the direct find_bit packet instead of being left implicit under generic alias wording.";

const EXPECTED_FIND_BIT_NEXT_SAFE_STEP_NOTE = "If this helper lane reopens, keep find_bit parked unless a fresh reread finds drift in the manifest-backed same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), underscore-alias, Linux-style alias coverage including the shipped andnot scan entry points, or tail-word skip anchors, or committed shared replay drift in the live `bits_per_long`, `first`, `next_after_6`, `next_after_word`, `first_zero`, `next_zero`, `first_and`, `next_and`, or `last` fixture keys; do not reopen older saved validator cues or neighboring helper families.";

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

const EXPECTED_RBTREE_CACHED_ROOT_DIRECT_REVIEW_SUMMARY = "cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed behavior remain owned by direct helper-local anchors, while the exact `cached_leftmost_return_serials` witness now stays aligned across the helper-local tests, the shared host-tools smoke replay, and the committed fixture";

const EXPECTED_RBTREE_CACHED_ROOT_FOLLOWUP_ANCHORS = [_][]const u8{
    "test \"rbtree addCached returns the inserted node only when it becomes leftmost\"",
    "test \"rbtree findAddCached keeps cached leftmost stable while inserting misses\"",
    "test \"rbtree cached root keeps the leftmost pointer in sync\"",
    "test \"rbtree cached-root Linux-style aliases mirror the primary helpers\"",
    "test \"rbtree replaceNodeCached keeps non-leftmost leftmost unchanged\"",
    "test \"rbtree eraseCached returns null for a singleton cached tree\"",
    "test \"rbtree eraseInitCached detaches nodes while keeping cached leftmost aligned\"",
    "test \"rbtree eraseInitCached clears singleton cached roots before reseed\"",
};

const EXPECTED_RBTREE_NEXT_SAFE_STEP_NOTE = "If this helper lane reopens, keep the already-landed shared-replay promotion for `cached_leftmost_return_serials` aligned across the committed fixture, shared replay, and direct cached-root anchors; the ordered Linux-style alias proof, dedicated `low_level_alias_anchor`, and the remaining cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed behavior stay owned by direct helper-local anchors until another committed cached-root field lands.";

const EXPECTED_RBTREE_REVIEW_PACKET_SUMMARY = "the current shared host-tools smoke replay keeps duplicate-range iteration and the exact `cached_leftmost_return_serials` cached-root leftmost-return witness visible for rbtree, while the committed Phase 1 fixture still carries the exact traversal, detached-node, duplicate-search, and cached-leftmost-return witnesses; direct helper-local anchors continue to own cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed paths that the shared smoke route does not replay exactly";

const EXPECTED_RBTREE_SHARED_REPLAY_SUMMARY = "the committed Phase 1 fixture still carries traversal, detached-node, duplicate-search, and exact cached-leftmost-return witnesses for rbtree, while the current shared host-tools smoke replay now rechecks duplicate-range iteration plus the exact `cached_leftmost_return_serials` cached-root leftmost-return sequence on current master";

const EXPECTED_RBTREE_TRAVERSAL_REPLAY_KEYS = [_][]const u8{
    "empty_root",
    "insert_order",
    "reverse_order",
    "replace_order",
    "erase_init_order",
    "postorder_count",
    "erase_init_node_empty",
    "cleared_node_empty",
};

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

const EXPECTED_STRING_COUNTED_SEARCH_REVIEW_SUMMARY = "the direct counted-search and C-string search-length follow-up stays explicit because the shared Phase 1 replay still does not carry dedicated counted-search or search-length fixture keys, so strchr() or strrchr() full-length C-string searches, strpbrk() first-accepted-byte scanning, strspn() accepted-prefix scanning, strcspn() rejected-byte scanning, strnchr() count-limited scanning, strnlen() count-clamped length, strnchrNul() or strnchrnul() match-or-NUL boundary behavior, and strchrNul() or strchrnul() match-or-terminator boundaries remain owned by the helper-local anchors";

const EXPECTED_STRING_NEXT_SAFE_STEP_NOTE = "If this helper lane reopens, keep the helper-local strlcat, sysfs, case-insensitive compare, and match-or-terminator review anchors aligned across the string review packet and this lane note unless dedicated shared fixture keys land; do not reopen missing closure-side validator names by default.";

const FIND_BIT_HELPER_REL = "tools/lib/find_bit.zig";

const LANE_NOTE_REL = "Documentation/zigux/phase1-host-helper-lane-sequencing.md";

const MANIFEST_REL = "zigux/tests/fixtures/phase1_helper_manifest.json";

const PHASE1_CLOSURE_REL = "Documentation/zigux/phase1-closure.md";

const PHASE1_CLOSURE_VALIDATOR_REL = "scripts/zigux/validate_phase1_closure.zig";

const RBTREE_HELPER_REL = "tools/lib/rbtree.zig";

const REQUIRED_EXACT_LINES_ENTRIES = [_]struct { file: []const u8, marker: []const u8 }{
    .{ .file = "Documentation/zigux/phase1-closure.md", .marker = "Current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with bounded later-lane non-Phase-1 routes across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14. It still does not expose `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, or `make -C zigux phase1`, so treat the returned file as current repo evidence while those older Phase 1 wrapper names remain historical packet members rather than active closure proof." },
    .{ .file = "Documentation/zigux/phase1-closure.md", .marker = "For `tools/lib/bitmap.zig`, current `master` still justifies a parked helper-local follow-up rather than a reopened closure pass. The committed shared replay now already carries bitmap allocator sizing, zero-filled allocation words, copy/copy-clear-tail/copy-and-extend replay, logical operator outputs, range set/clear/fill/zero outcomes, formatting truncation handling, and partial-window xor replay, while the shipped direct anchors still cover whole-word range edges, raw copy and tail-clearing behavior, zero and aligned `copyAndExtend()` handling, zero-sized destination-view no-op behavior, exact-word-boundary equality masking, out-of-range tail masking for predicates and weights, caller-window `xor` and `or` clamping including multiword tails, complement tail clamping, cross-word `scnprintf()` merging, empty-bitmap caller-buffer preservation, Linux-style alias mirrors, and allocator optional-reset coverage." },
    .{ .file = "Documentation/zigux/phase1-closure.md", .marker = "A current helper-family tie-breaker inside that packet is the `find_bit` direct-anchor route: keep `tools/lib/find_bit.zig` parked unless a fresh reread finds drift in the manifest-backed same-word start-mask, head-word, tail-word, or single-word tail inclusive-boundary anchors, zero-window, zero-sized short-circuit, past-`nbits`, `clump8`, `getValue8()`, `findLastBit()`, underscore-alias, Linux-style alias, or tail-word skip anchors, or drift in the already-committed tail-clamped or tail-inclusive-boundary replay fields, and do not reopen older validator-first cues or neighboring helper families by default. Current `master` still keeps the helper-local byte-clump, backward-scan, alias, and shipped `find_*andnot*` entry-point packet directly in `tools/lib/find_bit.zig`, and the manifest-backed review surface together with `Documentation/zigux/phase1-host-helper-lane-sequencing.md` keep that helper-local progress review-visible beside the narrower closure validator. That direct packet now also includes the explicit `clump8 past-end scans return without reading bitmap words` no-read anchor, so the byte-clump coverage is not limited to in-range or zero-bit windows. Current `master` also now spells the lead direct anchor as `find first and next set bits across words, with andnot gaps explicit`, names the underscore and Linux-style alias anchors `including andnot`, and keeps the dedicated `single-word tail windows keep the last in-range next matches reachable from an inclusive start` proof alongside the head-word and tail-word boundary packet, so leave `find_bit` parked unless one of those direct anchors or committed replay fields drifts." },
    .{ .file = "Documentation/zigux/phase1-closure.md", .marker = "A second current helper-family tie-breaker inside that packet is the `rbtree` direct-anchor route: keep `tools/lib/rbtree.zig` parked unless a fresh reread finds drift in the helper-local ordered Linux-style alias proof, the dedicated manifest-backed `low_level_alias_anchor`, the dedicated manifest-backed `cached_root_alias_anchor`, the cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, or reseed anchors, or drift in the already-committed duplicate-search replay fields or exact `cached_leftmost_return_serials` witness. Current `master` still keeps both Linux-style alias proofs named explicitly in `zigux/tests/fixtures/phase1_helper_manifest.json`, while the shared host-tools smoke route and committed Phase 1 fixture already recheck duplicate-range iteration plus the exact cached-leftmost-return packet, so leave rbtree parked unless one of those helper-local anchors or committed replay fields drifts and do not batch a second cached-root widening into the same reopen step." },
    .{ .file = "Documentation/zigux/phase1-closure.md", .marker = "Current `master` now also spells the helper-local `memtostr()`, `memtostrPad()`, and `memtostr_pad()` anchors directly in the shipped manifest-backed string review packet beside the `memcpyAndPad()`, `memcpy_and_pad()`, `strtomem()`, and `strtomem_pad()` byte-copy anchors. Keep those byte-copy and pad tests helper-local review evidence rather than shared-fixture or validator-owned requirements until dedicated fixture keys land." },
    .{ .file = "Documentation/zigux/phase1-closure.md", .marker = "- `PHASE1_STRING_SYSFS_REVIEW=helper-local string sysfs newline-aware equality and lookup-order anchors stay explicit through the direct string tests and the Phase 1 helper manifest because the shared Phase 1 replay still carries no dedicated sysfs fixture keys`" },
    .{ .file = "Documentation/zigux/phase1-host-helper-lane-sequencing.md", .marker = "- current authenticated reads still recover `zigux/tests/fixtures/phase1_helper_manifest.json`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `scripts\\zigux/check_phase1_string_review_packet.zig`, `scripts\\zigux/check_phase1_direct_owner_markers.zig`, `scripts\\zigux/check_phase1_shared_reminder_packet.zig`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `zigux/tests/README.md`, so those are the trustworthy reminder surfaces for this lane on current `master`" },
    .{ .file = "Documentation/zigux/phase1-host-helper-lane-sequencing.md", .marker = "- `PHASE1_BITMAP_DIRECT_OWNER=bitmap helper-local anchors plus the committed bitmap replay keys it already owns; the restored phase1-closure note and validate-phase1-closure guard are live companions again, while the older validator-first and make-route names stay historical`" },
    .{ .file = "Documentation/zigux/phase1-host-helper-lane-sequencing.md", .marker = "- `PHASE1_FIND_BIT_DIRECT_OWNER=find_bit helper-local same-word start-mask, head-word and tail-word inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), and findLastBit() byte-clump and backward-scan coverage, plus the public, Linux-style, and underscore andnot coverage including the shipped findFirstAndNotBit(), findNextAndNotBit(), find_first_andnot_bit(), find_next_andnot_bit(), _find_first_andnot_bit(), and _find_next_andnot_bit() entry points, and tail-word skip anchors plus the committed tail-clamped and tail-inclusive-boundary find_bit replay fields already preserved in zigux/tests/fixtures/phase1_helpers.json`" },
    .{ .file = "Documentation/zigux/phase1-host-helper-lane-sequencing.md", .marker = "- `PHASE1_RBTREE_DIRECT_OWNER=rbtree keeps ordered Linux-style alias, low-level Linux-style alias, cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors helper-local while the committed fixture still owns exact find(), findFirst(), nextMatch(), and matchIterator() duplicate-search fields and the shared host-tools smoke route keeps duplicate-range iteration plus the parked cached_leftmost_return_serials witness explicit`" },
    .{ .file = "Documentation/zigux/phase1-host-helper-lane-sequencing.md", .marker = "- `PHASE1_STRING_DIRECT_OWNER=string keeps strscpy()/strscpyPad() copy-and-pad semantics, memparse safety, matched-prefix-length and suffix boundary, sysfs newline-aware equality and lookup order through sysfsStreq(), sysfs_streq(), sysfsMatchString(), and sysfs_match_string(), C-string list lookup through matchString() and match_string(), counted-search and search-length anchors through strpbrk(), strspn(), strcspn(), strnchr(), strnchrNul() or strnchrnul(), strchr(), strrchr(), strlen(), and strnlen(), embedded-NUL trim preservation, and moving-earliest-dirty-byte memchrInv coverage helper-local while the committed shared replay owns embedded-NUL replaceChar parity bytes and the current string fixture keys`" },
    .{ .file = "Documentation/zigux/phase1-host-helper-lane-sequencing.md", .marker = "- current `master` also keeps the helper-local `clump8`, `getValue8()`, and `findLastBit()` byte-clump and backward-scan proofs explicit in both `tools/lib/find_bit.zig` and the manifest's `helper_test_anchors` list, so nearby Phase 1 follow-through should keep those checks inside the same direct `find_bit` packet instead of splitting byte-clump or last-bit drift into a separate shared replay family" },
    .{ .file = "Documentation/zigux/phase1-host-helper-lane-sequencing.md", .marker = "- The counted-search owner term here also covers the current `strnchrNul()` and `strnchrnul()` match-or-NUL boundary anchor already cataloged in `zigux/tests/fixtures/phase1_helper_manifest.json`, so future string-only rereads should keep that helper-local boundary proof inside the same counted-search packet instead of treating it as an unowned follow-up beside `strnchr()`." },
    .{ .file = "Documentation/zigux/phase1-host-helper-lane-sequencing.md", .marker = "- the same counted-search packet now also keeps the direct `strspn()` accepted-prefix anchor review-visible on current `master`, so future string-only rereads should treat accepted-byte-prefix scanning as part of that helper-local search family instead of leaving it implicit beside `strpbrk()` and `strnchr()`." },
    .{ .file = "Documentation/zigux/phase1-host-helper-lane-sequencing.md", .marker = "- the still-open string sysfs follow-through, if it reopens, should stay on one string-only shared review-rule packet across `zigux/tests/fixtures/phase1_helper_manifest.json`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, and `scripts\\zigux/check_phase1_string_review_packet.zig`; the restored `Documentation/zigux/phase1-closure.md` and `scripts\\zigux/validate_phase1_closure.zig` companions are now live broader reminder evidence on current `master`, but string should stay parked on the helper-local sysfs review anchors unless those direct string surfaces drift." },
    .{ .file = "Documentation/zigux/phase1-host-helper-lane-sequencing.md", .marker = "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_GAPS=the shared reminder packet now keeps scripts\\zigux/check_phase1_bench.zig explicit across Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, zigux/tests/README.md, and scripts/zigux/README.md, while the older installer-backed, validator-first, bench-route, and replay names stay historical packet members until they reread cleanly on current master`" },
    .{ .file = "Documentation/zigux/phase1-host-helper-lane-sequencing.md", .marker = "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_ACTIVE_PACKET=Documentation/zigux/README.md,Documentation/zigux/phase1-closure.md,Documentation/zigux/review-checklist.md,zigux/tests/README.md,scripts/zigux/README.md,scripts\\zigux/validate_phase1_closure.zig,scripts\\zigux/check_phase1_string_review_packet.zig,scripts\\zigux/check_phase1_direct_owner_markers.zig,scripts\\zigux/check_phase1_bench.zig,scripts\\zigux/check_phase1_shared_reminder_packet.zig`" },
    .{ .file = "Documentation/zigux/phase1-host-helper-lane-sequencing.md", .marker = "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_ROUTE_SPLIT=Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, zigux/tests/README.md, and scripts/zigux/README.md now all carry the shipped bench-checker wording, while Documentation/zigux/phase1-closure.md plus scripts\\zigux/validate_phase1_closure.zig keep the restored closure-side packet explicit and the broader installer-backed, validator-first, bench-route, and replay names remain historical packet members until direct current-master rereads restore them`" },
    .{ .file = "Documentation/zigux/phase1-host-helper-lane-sequencing.md", .marker = "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_NEXT_STEP=leave the shared bench-checker wording and shared-reminder checker packet parked unless a fresh reread finds drift across Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, zigux/tests/README.md, scripts/zigux/README.md, Documentation/zigux/phase1-closure.md, scripts\\zigux/validate_phase1_closure.zig, scripts\\zigux/check_phase1_bench.zig, or scripts\\zigux/check_phase1_shared_reminder_packet.zig; otherwise prefer the smaller helper-specific next-safe-step markers below before reopening any shared reminder surface`" },
    .{ .file = "Documentation/zigux/phase1-host-helper-lane-sequencing.md", .marker = "- `PHASE1_BITMAP_NEXT_SAFE_STEP=bitmap stays parked unless a fresh reread finds new direct-anchor drift or committed shared replay drift; do not reopen older closure-side or validator-route cue names by default`" },
    .{ .file = "Documentation/zigux/phase1-host-helper-lane-sequencing.md", .marker = "- `PHASE1_FIND_BIT_NEXT_SAFE_STEP=find_bit reopens only for direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), underscore-alias or Linux-style alias coverage including the shipped andnot scan entry points, or tail-word skip anchors, or for committed tail-clamped or tail-inclusive-boundary replay drift; do not reopen older saved validator cues or neighboring helper families`" },
    .{ .file = "Documentation/zigux/phase1-host-helper-lane-sequencing.md", .marker = "- the existing byte-clump and `findLastBit()` proofs belong to that same `find_bit` direct-anchor packet too, so if one of those helper-local anchors drifts, refresh the current helper-family note before widening shared replay ownership" },
    .{ .file = "Documentation/zigux/phase1-host-helper-lane-sequencing.md", .marker = "- `PHASE1_RBTREE_NEXT_SAFE_STEP=rbtree reopens only to keep the already-landed cached_leftmost_return_serials shared replay aligned across the manifest, direct-owner note, and any shared parity gates, or for drift inside the still-helper-local ordered Linux-style alias proof, dedicated low_level_alias_anchor, cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors; do not batch a second widening into the same run`" },
    .{ .file = "Documentation/zigux/phase1-host-helper-lane-sequencing.md", .marker = "- `PHASE1_STRING_NEXT_SAFE_STEP=string reopens only for direct-anchor drift inside strscpy()/strscpyPad() copy-and-pad semantics, memparse, matched-prefix-length or suffix boundary, sysfs newline-aware equality or lookup order, matchString()/match_string() C-string list lookup, counted-search and search-length anchors through strpbrk(), strspn(), strcspn(), strnchr(), strnchrNul() or strnchrnul(), strchr(), strrchr(), strlen(), and strnlen(), embedded-NUL trim, or moving-earliest-dirty-byte memchrInv coverage, or for committed replaceChar or current string fixture drift; keep the helper-local sysfs review anchors aligned across the string review packet and this lane note unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator names by default`" },
    .{ .file = "Documentation/zigux/phase1-host-helper-lane-sequencing.md", .marker = "- current authenticated reads also recover `scripts\\zigux/check_phase1_route_summary_counts.zig`, but the restored closure packet treats it as an adjacent workflow and Makefile guard rather than as one of the narrow shared reminder-packet members on current `master`" },
    .{ .file = "Documentation/zigux/phase1-host-helper-lane-sequencing.md", .marker = "- current authenticated reads still do not recover `scripts\\zigux/validate_phase1.zig` on `master`, while `Documentation/zigux/phase1-closure.md`, `scripts\\zigux/validate_phase1_closure.zig`, and `zigux/Makefile` are back on current `master`; the returned Makefile now exposes the shipped Phase 2 toolchain and kbuild wrappers together with bounded later-lane non-Phase-1 routes across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14, including `phase3-validate`, `phase3`, `phase4-validate`, `phase6-validate`, `phase8-validate`, `phase8-exec-cmd-test`, `phase8-test`, `phase8`, `phase10-validate`, `phase10-test`, `phase10`, `phase12-validate`, `phase12-smoke`, `phase12-test`, and `phase14-validate`, so this lane should use that restored closure-side packet as live owner-map evidence while still treating the older validator-first and Phase 1 make-route names as historical packet members" },
    .{ .file = "Documentation/zigux/phase1-host-helper-lane-sequencing.md", .marker = "- the helper-specific direct-owner marker lines in this note are already exact-checked by `scripts\\zigux/check_phase1_direct_owner_markers.zig`, so reread them only if the note or its dedicated checker changes" },
    .{ .file = "Documentation/zigux/phase1-host-helper-lane-sequencing.md", .marker = "- the dedicated owner-map checker itself is now part of the live Phase 1 reminder packet beside this lane note, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `zigux/tests/README.md`, so future reminder surfaces should keep that checker explicit instead of treating the owner-map note as docs-only context" },
    .{ .file = "Documentation/zigux/phase1-host-helper-lane-sequencing.md", .marker = "- broader shared reminder surfaces now split cleanly: `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` now all keep `scripts\\zigux/check_phase1_bench.zig` explicit as the shipped bench-side checker while preserving the older installer-backed, validator-first, bench-route, and replay names as historical packet members, so bench wording is no longer the default same-lane follow-through." },
    .{ .file = "scripts/zigux/README.md", .marker = "- `zig run scripts/zigux/validate_phase1_closure.zig`, `zig run scripts/zigux/check_phase1_string_review_packet.zig -- --self-test`, `zig run scripts/zigux/check_phase1_direct_owner_markers.zig -- --self-test`, `zig run scripts/zigux/check_phase1_bench.zig -- --self-test`, and `zig run scripts/zigux/check_phase1_shared_reminder_packet.zig -- --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route" },
    .{ .file = "scripts/zigux/README.md", .marker = "- `scripts\\zigux/check_phase1_string_review_packet.zig`, `scripts\\zigux/check_phase1_direct_owner_markers.zig`, `scripts\\zigux/check_phase1_bench.zig`, `scripts\\zigux/check_phase1_shared_reminder_packet.zig`, and `scripts\\zigux/validate_phase1_closure.zig` keep the shipped string-review, direct-owner, bench, shared-reminder, and closure-validator packet explicit from the scripts root" },
    .{ .file = "scripts/zigux/README.md", .marker = "- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `zigux/tests/build.zig`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_helpers_build.zig`, and `zigux/tests/phase1_host_tools_smoke.zig` remain the current reminder-surface companions for that packet" },
    .{ .file = "scripts/zigux/README.md", .marker = "- repeated authenticated reads on current `master` still return missing for the Phase 1 installer-backed path `scripts/zigux/install_zig.zig`, `scripts\\zigux/check_phase1_installer_review_surfaces.zig`, `scripts\\zigux/check_phase1_installer_companion_checks.zig`, `scripts\\zigux/validate_phase1.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/phase1_helpers_c_harness.c`, so treat those installer-backed, older validator-first, bench, and C-harness routes as historical packet members that need fresh re-materialization before they are reused here as direct current-`master` reminder evidence" },
    .{ .file = "scripts/zigux/README.md", .marker = "- current `master` does ship `scripts\\zigux/check_phase1_bench.zig`, and `.github/workflows/zigux-bootstrap.yml` self-tests it, so keep the remaining shared reminder follow-through focused on the broader docs-root, checklist, and tests-root bench wording instead of treating the bench checker itself as a repo-reality gap here" },
    .{ .file = "scripts/zigux/README.md", .marker = "- the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, and string reopen only inside their existing helper-local anchors or already-committed shared fixture keys, while the other nine closed helpers stay parked unless the shared replay or reminder packet drifts" },
    .{ .file = "tools/lib/bitmap.zig", .marker = "test \"bitmap or keeps caller-selected bit window\" {" },
    .{ .file = "tools/lib/bitmap.zig", .marker = "test \"bitmap or across a multiword tail still lets callers clamp the last word\" {" },
    .{ .file = "tools/lib/bitmap.zig", .marker = "test \"bitmap weighted or and xor clamp counts to the declared tail window\" {" },
    .{ .file = "tools/lib/find_bit.zig", .marker = "pub fn findFirstAndNotBit(addr1: []const Word, addr2: []const Word, nbits: usize) usize {" },
    .{ .file = "tools/lib/find_bit.zig", .marker = "pub fn find_first_andnot_bit(addr1: []const Word, addr2: []const Word, nbits: usize) usize {" },
    .{ .file = "tools/lib/find_bit.zig", .marker = "pub fn _find_first_andnot_bit(addr1: []const Word, addr2: []const Word, nbits: usize) usize {" },
    .{ .file = "tools/lib/find_bit.zig", .marker = "pub fn findNextAndNotBit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {" },
    .{ .file = "tools/lib/find_bit.zig", .marker = "pub fn find_next_andnot_bit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {" },
    .{ .file = "tools/lib/find_bit.zig", .marker = "pub fn _find_next_andnot_bit(addr1: []const Word, addr2: []const Word, nbits: usize, start: usize) usize {" },
    .{ .file = "tools/lib/find_bit.zig", .marker = "test \"clump8 past-end scans return without reading bitmap words\" {" },
    .{ .file = "tools/lib/find_bit.zig", .marker = "test \"getValue8 reads aligned bytes from bitmap words\" {" },
    .{ .file = "tools/lib/find_bit.zig", .marker = "test \"find last bit scans backward across words\" {" },
    .{ .file = "tools/lib/find_bit.zig", .marker = "test \"low-level underscore aliases mirror the primary find helpers, including andnot\" {" },
    .{ .file = "tools/lib/find_bit.zig", .marker = "test \"Linux-style aliases mirror the primary find helpers, including andnot\" {" },
    .{ .file = "tools/lib/rbtree.zig", .marker = "test \"rbtree ordered Linux-style aliases mirror traversal and replacement helpers\" {" },
    .{ .file = "tools/lib/rbtree.zig", .marker = "test \"rbtree low-level Linux-style aliases mirror node-state helpers\" {" },
    .{ .file = "tools/lib/rbtree.zig", .marker = "test \"rbtree cached root keeps the leftmost pointer in sync\" {" },
    .{ .file = "tools/lib/rbtree.zig", .marker = "test \"rbtree cached-root Linux-style aliases mirror the primary helpers\" {" },
    .{ .file = "tools/lib/rbtree.zig", .marker = "test \"rbtree eraseInitCached clears singleton cached roots before reseed\" {" },
    .{ .file = "tools/lib/string.zig", .marker = "test \"sysfsStreq treats trailing newline and NUL as equivalent\" {" },
    .{ .file = "tools/lib/string.zig", .marker = "test \"sysfsMatchString finds newline-aware matches and preserves first-match order\" {" },
    .{ .file = "tools/lib/string.zig", .marker = "test \"memchrInv follows the earliest dirty byte as long buffers change\" {" },
    .{ .file = "tools/lib/string.zig", .marker = "test \"strspn counts the accepted prefix with C-string semantics\" {" },
    .{ .file = "tools/lib/string.zig", .marker = "test \"strnchrNul returns the first match, NUL, or count boundary\" {" },
};

const REQUIRED_FILES = [_][]const u8{
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/README.md",
    "scripts/zigux/README.md",
    "scripts/zigux/validate_phase1_closure.zig",
    "scripts/zigux/check_phase1_shared_reminder_packet.zig",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
    "tools/lib/bitmap.zig",
    "tools/lib/find_bit.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
};

const REVIEW_CHECKLIST_REL = "Documentation/zigux/review-checklist.md";

const SCRIPTS_README_REL = "scripts/zigux/README.md";

const SHARED_REMINDER_CHECKER_REL = "scripts/zigux/check_phase1_shared_reminder_packet.zig";

const STRING_HELPER_REL = "tools/lib/string.zig";

const TESTS_README_REL = "zigux/tests/README.md";

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

    for (REQUIRED_FILES) |relative_path| {
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    if (failures.items.len > 0) return failures;

    for (REQUIRED_EXACT_LINES_ENTRIES) |entry| {
        const full_path = try guard.joinPath(allocator, root, entry.file);
        defer allocator.free(full_path);
        const text = guard.readUtf8File(io, allocator, full_path) catch |err| switch (err) {
            guard.GuardError.IOError => {
                const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{entry.file});
                try failures.append(allocator, issue);
                continue;
            },
            else => return err,
        };
        defer allocator.free(text);
        const label = try std.fmt.allocPrint(allocator, "{s}:{s}", .{ entry.file, entry.marker });
        defer allocator.free(label);
        try guard.appendExactTrimmedLineIssue(allocator, &failures, text, label, entry.marker);
    }

    return failures;
}

pub fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    var tmp = try guard.TempWorkspace.init(io, allocator, "selftest");
    defer tmp.deinit();
    const root = try tmp.rootPath(allocator);
    defer allocator.free(root);
    for (REQUIRED_EXACT_LINES_ENTRIES) |entry| {
        const full_path = try guard.joinPath(allocator, root, entry.file);
        defer allocator.free(full_path);
        const existing = guard.readUtf8File(io, allocator, full_path) catch |err| switch (err) {
            guard.GuardError.IOError => try allocator.dupe(u8, "# sample\n\n"),
            else => return err,
        };
        defer allocator.free(existing);
        const updated = try std.fmt.allocPrint(allocator, "{s}{s}\n", .{ existing, entry.marker });
        defer allocator.free(updated);
        try guard.writeUtf8File(io, full_path, updated);
    }
    for (REQUIRED_FILES) |relative_path| {
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            try guard.writeUtf8File(io, full_path, "# sample\n");
        }
    }
    var failures = try collectFailures(io, allocator, root);
    defer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }
    if (failures.items.len != 0) {
        try guard.printLine(io, "PHASE1_DIRECT_OWNER_MARKERS_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        return guard.GuardError.SelfTestFailed;
    }
    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_DIRECT_OWNER_MARKERS_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());

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
        try guard.printLine(io, "PHASE1_DIRECT_OWNER_MARKERS_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE1_DIRECT_OWNER_MARKERS_REQUIRED_FILE_COUNT={d}", .{@as(usize, REQUIRED_FILES.len)});
    try guard.printLine(io, "PHASE1_DIRECT_OWNER_MARKERS_REQUIRED_HELPER_COUNT={d}", .{@as(usize, EXPECTED_HELPERS.len)});
    std.process.exit(0);
}
