// Ported from check-phase1-shared-reminder-packet.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=pass";

const MARKERS_ENTRIES = [_]struct { file: []const u8, marker: []const u8 }{
    .{ .file = "Documentation/zigux/README.md", .marker = "keep the live owner map, the restored closure note and closure validator, the adjacent route-summary guard, the parked shared-replay-versus-direct-anchor split, the shipped bench checker, and the current Phase 1 reminder packet explicit from the docs root without rebuilding the broader host-tools closure stack from older missing validator and replay surfaces." },
    .{ .file = "Documentation/zigux/README.md", .marker = "- `scripts\\zigux/check_phase1_shared_reminder_packet.zig`" },
    .{ .file = "Documentation/zigux/README.md", .marker = "`scripts\\zigux/check_phase1_string_review_packet.zig`, `scripts\\zigux/check_phase1_direct_owner_markers.zig`, and `scripts\\zigux/check_phase1_bench.zig` are the shipped direct checks" },
    .{ .file = "Documentation/zigux/README.md", .marker = "`zig run check_phase1_bench.zig --self-test`" },
    .{ .file = "Documentation/zigux/README.md", .marker = "`zigux/Makefile` is current repo evidence again because its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with bounded later-lane route families across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14." },
    .{ .file = "Documentation/zigux/phase1-closure.md", .marker = "- `scripts\\zigux/check_phase1_shared_reminder_packet.zig`" },
    .{ .file = "Documentation/zigux/phase1-closure.md", .marker = "- `scripts\\zigux/check_phase1_direct_anchor_manifest_gate.zig`" },
    .{ .file = "Documentation/zigux/phase1-closure.md", .marker = "`PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,scripts/zigux/README.md,scripts\\zigux/check_phase1_string_review_packet.zig,scripts\\zigux/check_phase1_direct_owner_markers.zig,scripts\\zigux/check_phase1_direct_anchor_manifest_gate.zig,scripts\\zigux/check_phase1_bench.zig,scripts\\zigux/check_phase1_shared_reminder_packet.zig,scripts\\zigux/validate_phase1_closure.zig,zigux/tests/README.md,zigux/tests/build.zig,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_helpers_build.zig,zigux/tests/phase1_host_tools_smoke.zig,.github/workflows/zigux-bootstrap.yml,zigux/tests/fixtures/phase1_helper_manifest.json`" },
    .{ .file = "Documentation/zigux/phase1-closure.md", .marker = "Current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with bounded later-lane non-Phase-1 routes across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14. It still does not expose `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, or `make -C zigux phase1`, so treat the returned file as current repo evidence while those older Phase 1 wrapper names remain historical packet members rather than active closure proof." },
    .{ .file = "Documentation/zigux/phase1-closure.md", .marker = "`PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=zig run check_phase1_direct_anchor_manifest_gate.zig exact-checks the current direct-anchor helper manifest packet for bitmap, find_bit, rbtree, and string and then reruns the dedicated rbtree direct-anchor checker`" },
    .{ .file = "Documentation/zigux/phase1-closure.md", .marker = "`PHASE1_CLOSURE_VALIDATOR=zig run validate_phase1_closure.zig`" },
    .{ .file = "Documentation/zigux/phase1-closure.md", .marker = "`PHASE1_ROUTE_SUMMARY_GUARD=zig run check_phase1_route_summary_counts.zig`" },
    .{ .file = "Documentation/zigux/phase1-closure.md", .marker = "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`" },
    .{ .file = "Documentation/zigux/phase1-closure.md", .marker = "`PHASE1_FIND_BIT_BENCH_GUARD=scripts\\zigux/check_phase1_bench.zig still hard-codes PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000 and PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS=20000 and still requires PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM and PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM when the broader expectations packet returns`" },
    .{ .file = "Documentation/zigux/phase1-closure.md", .marker = "`PHASE1_FIND_BIT_REVIEW_GUARD=zig run check_phase1_find_bit_review_packet.zig exact-checks helper-local find_bit anchors plus the committed tail-clamped and tail-inclusive-boundary replay packet across the helper, closure note, lane note, manifest, and fixture`" },
    .{ .file = "Documentation/zigux/phase1-closure.md", .marker = "For `tools/lib/bitmap.zig`, current `master` still justifies a parked helper-local follow-up rather than a reopened closure pass. The committed shared replay now already carries bitmap allocator sizing, zero-filled allocation words, copy/copy-clear-tail/copy-and-extend replay, logical operator outputs, range set/clear/fill/zero outcomes, formatting truncation handling, and partial-window xor replay, while the shipped direct anchors still cover whole-word range edges, raw copy and tail-clearing behavior, zero and aligned `copyAndExtend()` handling, zero-sized destination-view no-op behavior, exact-word-boundary equality masking, out-of-range tail masking for predicates and weights, caller-window `xor` and `or` clamping including multiword tails, complement tail clamping, cross-word `scnprintf()` merging, empty-bitmap caller-buffer preservation, Linux-style alias mirrors, and allocator optional-reset coverage." },
    .{ .file = "Documentation/zigux/phase1-closure.md", .marker = "A current helper-family tie-breaker inside that packet is the `find_bit` direct-anchor route: keep `tools/lib/find_bit.zig` parked unless a fresh reread finds drift in the manifest-backed same-word start-mask, head-word, tail-word, or single-word tail inclusive-boundary anchors, zero-window, zero-sized short-circuit, past-`nbits`, `clump8`, `getValue8()`, `findLastBit()`, underscore-alias, Linux-style alias, or tail-word skip anchors, or drift in the already-committed tail-clamped or tail-inclusive-boundary replay fields, and do not reopen older validator-first cues or neighboring helper families by default. Current `master` still keeps the helper-local byte-clump, backward-scan, alias, and shipped `find_*andnot*` entry-point packet directly in `tools/lib/find_bit.zig`, and the manifest-backed review surface together with `Documentation/zigux/phase1-host-helper-lane-sequencing.md` keep that helper-local progress review-visible beside the narrower closure validator. That direct packet now also includes the explicit `clump8 past-end scans return without reading bitmap words` no-read anchor, so the byte-clump coverage is not limited to in-range or zero-bit windows. Current `master` also now spells the lead direct anchor as `find first and next set bits across words, with andnot gaps explicit`, names the underscore and Linux-style alias anchors `including andnot`, and keeps the dedicated `single-word tail windows keep the last in-range next matches reachable from an inclusive start` proof alongside the head-word and tail-word boundary packet, so leave `find_bit` parked unless one of those direct anchors or committed replay fields drifts." },
    .{ .file = "Documentation/zigux/phase1-closure.md", .marker = "A second current helper-family tie-breaker inside that packet is the `rbtree` direct-anchor route: keep `tools/lib/rbtree.zig` parked unless a fresh reread finds drift in the helper-local ordered Linux-style alias proof, the dedicated manifest-backed `low_level_alias_anchor`, the dedicated manifest-backed `cached_root_alias_anchor`, the cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, or reseed anchors, or drift in the already-committed duplicate-search replay fields or exact `cached_leftmost_return_serials` witness. Current `master` still keeps both Linux-style alias proofs named explicitly in `zigux/tests/fixtures/phase1_helper_manifest.json`, while the shared host-tools smoke route and committed Phase 1 fixture already recheck duplicate-range iteration plus the exact cached-leftmost-return packet, so leave rbtree parked unless one of those helper-local anchors or committed replay fields drifts and do not batch a second cached-root widening into the same reopen step." },
    .{ .file = "Documentation/zigux/phase1-host-helper-lane-sequencing.md", .marker = "`PHASE1_DIRECT_ANCHOR_FOLLOWUP_HELPERS=tools/lib/bitmap.zig,tools/lib/find_bit.zig,tools/lib/rbtree.zig,tools/lib/string.zig`" },
    .{ .file = "Documentation/zigux/phase1-host-helper-lane-sequencing.md", .marker = "`PHASE1_DIRECT_OWNER_SHARED_REMINDER_ACTIVE_PACKET=Documentation/zigux/README.md,Documentation/zigux/phase1-closure.md,Documentation/zigux/review-checklist.md,zigux/tests/README.md,scripts/zigux/README.md,scripts\\zigux/validate_phase1_closure.zig,scripts\\zigux/check_phase1_string_review_packet.zig,scripts\\zigux/check_phase1_direct_owner_markers.zig,scripts\\zigux/check_phase1_bench.zig,scripts\\zigux/check_phase1_shared_reminder_packet.zig`" },
    .{ .file = "Documentation/zigux/review-checklist.md", .marker = "`Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts\\zigux/validate_phase1_closure.zig`, `scripts\\zigux/check_phase1_string_review_packet.zig`, `scripts\\zigux/check_phase1_direct_owner_markers.zig`, `scripts\\zigux/check_phase1_bench.zig`, `scripts\\zigux/check_phase1_shared_reminder_packet.zig`, `zigux/tests/README.md`, `zigux/tests/build.zig`, `zigux/tests/phase1_host_tools_smoke.zig`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/fixtures/phase1_helper_manifest.json`, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` still agree on the current closed-helper reminder packet" },
    .{ .file = "Documentation/zigux/review-checklist.md", .marker = "keep `scripts\\zigux/check_phase1_route_summary_counts.zig`, `make -C zigux phase1-route-summary`, and `zigux/Makefile` explicit as the adjacent Phase 1 route-summary evidence for the returned Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, while the older validator-first, parity, bench-route, and replay names stay framed as historical packet members until current `master` materializes them again?" },
    .{ .file = "Documentation/zigux/review-checklist.md", .marker = "keep that partial bitmap packet framed as a separate bounded Phase 9 runtime reminder rather than proof that the broader shared runtime-loader packet returned" },
    .{ .file = "scripts/zigux/README.md", .marker = "current `master` does ship `scripts\\zigux/check_phase1_bench.zig`, and `.github/workflows/zigux-bootstrap.yml` self-tests it" },
    .{ .file = "scripts/zigux/README.md", .marker = "`Documentation/zigux/phase1-closure.md` and `scripts\\zigux/validate_phase1_closure.zig` are back on current `master`" },
    .{ .file = "scripts/zigux/README.md", .marker = "`scripts\\zigux/check_phase1_string_review_packet.zig`, `scripts\\zigux/check_phase1_direct_owner_markers.zig`, `scripts\\zigux/check_phase1_bench.zig`, `scripts\\zigux/check_phase1_shared_reminder_packet.zig`, and `scripts\\zigux/validate_phase1_closure.zig` keep the shipped string-review, direct-owner, bench, shared-reminder, and closure-validator packet explicit from the scripts root" },
    .{ .file = "scripts/zigux/README.md", .marker = "`scripts\\zigux/check_phase1_route_summary_counts.zig`, `make -C zigux phase1-route-summary`, and `.github/workflows/zigux-bootstrap.yml` keep the adjacent Phase 1 route-summary guard explicit beside the narrower reminder packet, so scripts-root follow-through can verify the returned non-Phase-1 Makefile route inventory without promoting the older Phase 1 wrappers back into shipped proof" },
    .{ .file = "scripts/zigux/README.md", .marker = "`zig run validate_phase1_closure.zig`, `zig run check_phase1_string_review_packet.zig --self-test`, `zig run check_phase1_direct_owner_markers.zig --self-test`, `zig run check_phase1_bench.zig --self-test`, and `zig run check_phase1_shared_reminder_packet.zig --self-test` replay the shipped bounded Phase 1 reminder checks" },
    .{ .file = "scripts/zigux/README.md", .marker = "`zigux/Makefile` is current repo evidence again from the scripts root too, because its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded returned `phase3-validate` and `phase3` routes plus the later Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, so keep that returned route summary aligned here while the older Phase 1 wrapper names stay historical reminder vocabulary" },
    .{ .file = "scripts/zigux/README.md", .marker = "repeated authenticated reads on current `master` still return missing for the Phase 1 installer-backed path `scripts/zigux/install_zig.zig`, `scripts\\zigux/check_phase1_installer_review_surfaces.zig`, `scripts\\zigux/check_phase1_installer_companion_checks.zig`, `scripts\\zigux/validate_phase1.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/phase1_helpers_c_harness.c`, so treat those installer-backed, older validator-first, bench, and C-harness routes as historical packet members that need fresh re-materialization before they are reused here as direct current-`master` reminder evidence" },
    .{ .file = "scripts/zigux/check_phase1_bench.zig", .marker = "RBTREE_REQUIRED_EXACT_CHECKSUMS = {" },
    .{ .file = "scripts/zigux/check_phase1_bench.zig", .marker = "def run_self_test() -> None:" },
    .{ .file = "scripts/zigux/check_phase1_direct_anchor_manifest_gate.zig", .marker = "description=\"Validate the Phase 1 direct-anchor helper manifest packet for bitmap, find_bit, rbtree, and string.\"" },
    .{ .file = "scripts/zigux/check_phase1_direct_anchor_manifest_gate.zig", .marker = "print(\"PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=pass\")" },
    .{ .file = "scripts/zigux/check_phase1_direct_anchor_manifest_gate.zig", .marker = "print(\"PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_SELF_TEST=pass\")" },
    .{ .file = "scripts/zigux/check_phase1_direct_owner_markers.zig", .marker = "EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS = [" },
    .{ .file = "scripts/zigux/check_phase1_direct_owner_markers.zig", .marker = "print(\"PHASE1_DIRECT_OWNER_MARKERS=pass\")" },
    .{ .file = "scripts/zigux/check_phase1_find_bit_bench_anchors.zig", .marker = "description=\"Validate that the live find_bit helper still carries the current bench-adjacent edge anchors, including the landed andnot, clump-forward-skip, and tail-word next-skip paths.\"" },
    .{ .file = "scripts/zigux/check_phase1_find_bit_bench_anchors.zig", .marker = "print(\"PHASE1_FIND_BIT_BENCH_ANCHORS=pass\")" },
    .{ .file = "scripts/zigux/check_phase1_find_bit_bench_anchors.zig", .marker = "print(\"PHASE1_FIND_BIT_BENCH_ANCHORS_SELF_TEST=pass\")" },
    .{ .file = "scripts/zigux/check_phase1_find_bit_review_packet.zig", .marker = "\"\"\"Guard the Phase 1 find_bit review packet against helper, fixture, and note drift.\"\"\"" },
    .{ .file = "scripts/zigux/check_phase1_find_bit_review_packet.zig", .marker = "print(\"phase1-find-bit-review-packet:ok\")" },
    .{ .file = "scripts/zigux/check_phase1_route_summary_counts.zig", .marker = "\"\"\"Guard the current Phase 1 route-summary packet across closure, Makefile, and workflow.\"\"\"" },
    .{ .file = "scripts/zigux/check_phase1_route_summary_counts.zig", .marker = "print(\"PHASE1_ROUTE_SUMMARY_COUNTS=pass\")" },
    .{ .file = "scripts/zigux/check_phase1_route_summary_counts.zig", .marker = "print(\"PHASE1_ROUTE_SUMMARY_COUNTS_SELF_TEST=pass\")" },
    .{ .file = "scripts/zigux/check_phase1_string_review_packet.zig", .marker = "EXPECTED_STRING_SOURCE_SYMBOLS = [" },
    .{ .file = "scripts/zigux/check_phase1_string_review_packet.zig", .marker = "EXPECTED_HELPER_TEST_ANCHORS = [" },
    .{ .file = "scripts/zigux/check_phase1_string_review_packet.zig", .marker = "print(\"phase1-string-review-packet:ok\")" },
    .{ .file = "scripts/zigux/validate_phase1_closure.zig", .marker = "PHASE1_CLOSURE_VALIDATION=pass" },
    .{ .file = "scripts/zigux/validate_phase1_closure.zig", .marker = "PHASE1_CLOSURE_SELF_TEST=pass" },
    .{ .file = "zigux/tests/README.md", .marker = "current direct-readback Phase 1 reminder packet:" },
    .{ .file = "zigux/tests/README.md", .marker = "- `scripts\\zigux/check_phase1_direct_anchor_manifest_gate.zig`" },
    .{ .file = "zigux/tests/README.md", .marker = "- `scripts\\zigux/check_phase1_shared_reminder_packet.zig`" },
    .{ .file = "zigux/tests/README.md", .marker = "`zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`" },
    .{ .file = "zigux/tests/README.md", .marker = "broader Phase 1 closure companions stay outside the narrow direct-readback packet: authenticated contents reads on current `master` still return missing for `scripts\\zigux/validate_phase1.zig`, `scripts\\zigux/check_phase1_parity.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/phase1_helpers_c_harness.c`, but current public-tree readback does rematerialize that validator-first, bench, and replay family on `master`, so keep those paths framed as broader closure companions rather than as active tests-root proof inside this direct-readback reminder packet" },
    .{ .file = "zigux/tests/build.zig", .marker = "root_source_file = b.path(\"phase1_host_tools_smoke.zig\")," },
    .{ .file = "zigux/tests/build.zig", .marker = "const slab_module = b.createModule(.{" },
    .{ .file = "zigux/tests/build.zig", .marker = "const str_error_r_module = b.createModule(.{" },
    .{ .file = "zigux/tests/build.zig", .marker = "const vsprintf_module = b.createModule(.{" },
    .{ .file = "zigux/tests/build.zig", .marker = "const zalloc_module = b.createModule(.{" },
    .{ .file = "zigux/tests/build.zig", .marker = "root_module.addImport(\"slab\", slab_module);" },
    .{ .file = "zigux/tests/build.zig", .marker = "root_module.addImport(\"str_error_r\", str_error_r_module);" },
    .{ .file = "zigux/tests/build.zig", .marker = "root_module.addImport(\"vsprintf\", vsprintf_module);" },
    .{ .file = "zigux/tests/build.zig", .marker = "root_module.addImport(\"zalloc\", zalloc_module);" },
    .{ .file = "zigux/tests/build.zig", .marker = ".name = \"phase1-host-tools-smoke\"," },
    .{ .file = "zigux/tests/phase1_helpers.zig", .marker = "test \"phase 1 helper ports match committed parity fixture\" {" },
    .{ .file = "zigux/tests/phase1_helpers_build.zig", .marker = ".name = \"phase1-helpers\"," },
    .{ .file = "zigux/tests/phase1_helpers_build.zig", .marker = "root_source_file = b.path(\"phase1_helpers.zig\")," },
    .{ .file = "zigux/tests/fixtures/phase1_helper_manifest.json", .marker = "\"lane_sequencing\": {" },
    .{ .file = "zigux/tests/fixtures/phase1_helper_manifest.json", .marker = "\"direct_anchor_followup_helpers\": [" },
    .{ .file = "zigux/tests/fixtures/phase1_helper_manifest.json", .marker = "\"rule_summary\": \"Phase 1 helper follow-up stays parked on shared replay for the nine helpers above, while bitmap, find_bit, rbtree, and string keep the only bounded direct helper-local follow-up anchors on current master.\"" },
    .{ .file = "zigux/Makefile", .marker = "phase1-route-summary:" },
    .{ .file = "zigux/Makefile", .marker = "phase2-toolchain:" },
    .{ .file = "zigux/Makefile", .marker = "phase2-tools:" },
    .{ .file = "zigux/Makefile", .marker = "phase2-kconfig:" },
    .{ .file = "zigux/Makefile", .marker = "phase2-cross:" },
    .{ .file = "zigux/Makefile", .marker = "phase2-genksyms:" },
    .{ .file = "zigux/Makefile", .marker = "phase3-validate:" },
    .{ .file = "zigux/Makefile", .marker = "phase4-validate:" },
    .{ .file = "zigux/Makefile", .marker = "phase6-validate:" },
    .{ .file = "zigux/Makefile", .marker = "phase8-validate:" },
    .{ .file = "zigux/Makefile", .marker = "phase12-validate:" },
    .{ .file = "zigux/Makefile", .marker = "phase12-smoke:" },
    .{ .file = "zigux/Makefile", .marker = "phase12-test:" },
    .{ .file = "zigux/Makefile", .marker = "phase12: phase12-validate phase12-smoke phase12-test" },
    .{ .file = "zigux/Makefile", .marker = "phase14-validate:" },
    .{ .file = "zigux/tests/phase1_host_tools_smoke.zig", .marker = "const argv_split = @import(\"argv_split\");" },
    .{ .file = "zigux/tests/phase1_host_tools_smoke.zig", .marker = "const slab = @import(\"slab\");" },
    .{ .file = "zigux/tests/phase1_host_tools_smoke.zig", .marker = "const str_error_r = @import(\"str_error_r\");" },
    .{ .file = "zigux/tests/phase1_host_tools_smoke.zig", .marker = "const vsprintf = @import(\"vsprintf\");" },
    .{ .file = "zigux/tests/phase1_host_tools_smoke.zig", .marker = "const zalloc = @import(\"zalloc\");" },
    .{ .file = "zigux/tests/phase1_host_tools_smoke.zig", .marker = "try std.testing.expect(@hasDecl(bitmap, \"setRange\"));" },
    .{ .file = "zigux/tests/phase1_host_tools_smoke.zig", .marker = "try std.testing.expect(@hasDecl(slab, \"kmallocBytes\"));" },
    .{ .file = "zigux/tests/phase1_host_tools_smoke.zig", .marker = "try std.testing.expect(@hasDecl(str_error_r, \"strErrorR\"));" },
    .{ .file = "zigux/tests/phase1_host_tools_smoke.zig", .marker = "try std.testing.expect(@hasDecl(vsprintf, \"scnprintf\"));" },
    .{ .file = "zigux/tests/phase1_host_tools_smoke.zig", .marker = "try std.testing.expect(@hasDecl(zalloc, \"zallocBytes\"));" },
    .{ .file = ".github/workflows/zigux-bootstrap.yml", .marker = "run: zig run check_phase1_direct_owner_markers.zig --self-test" },
    .{ .file = ".github/workflows/zigux-bootstrap.yml", .marker = "run: zig run check_phase1_direct_owner_markers.zig" },
    .{ .file = ".github/workflows/zigux-bootstrap.yml", .marker = "run: zig run check_phase1_direct_anchor_manifest_gate.zig --self-test" },
    .{ .file = ".github/workflows/zigux-bootstrap.yml", .marker = "run: zig run check_phase1_direct_anchor_manifest_gate.zig" },
    .{ .file = ".github/workflows/zigux-bootstrap.yml", .marker = "run: zig run check_phase1_string_review_packet.zig --self-test" },
    .{ .file = ".github/workflows/zigux-bootstrap.yml", .marker = "run: zig run check_phase1_string_review_packet.zig" },
    .{ .file = ".github/workflows/zigux-bootstrap.yml", .marker = "run: zig run check_phase1_find_bit_review_packet.zig --self-test" },
    .{ .file = ".github/workflows/zigux-bootstrap.yml", .marker = "run: zig run check_phase1_find_bit_review_packet.zig" },
    .{ .file = ".github/workflows/zigux-bootstrap.yml", .marker = "run: zig run check_phase1_route_summary_counts.zig --self-test" },
    .{ .file = ".github/workflows/zigux-bootstrap.yml", .marker = "run: zig run check_phase1_route_summary_counts.zig" },
    .{ .file = ".github/workflows/zigux-bootstrap.yml", .marker = "run: zig run check_phase1_bench.zig --self-test" },
    .{ .file = ".github/workflows/zigux-bootstrap.yml", .marker = "run: zig run check_phase1_find_bit_bench_anchors.zig --self-test" },
    .{ .file = ".github/workflows/zigux-bootstrap.yml", .marker = "run: zig run check_phase1_find_bit_bench_anchors.zig" },
    .{ .file = ".github/workflows/zigux-bootstrap.yml", .marker = "run: zig run check_phase1_shared_reminder_packet.zig --self-test" },
    .{ .file = ".github/workflows/zigux-bootstrap.yml", .marker = "run: zig run check_phase1_shared_reminder_packet.zig" },
    .{ .file = ".github/workflows/zigux-bootstrap.yml", .marker = "run: zig run validate_phase1_closure.zig --self-test" },
    .{ .file = ".github/workflows/zigux-bootstrap.yml", .marker = "run: zig run validate_phase1_closure.zig" },
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

    for (MARKERS_ENTRIES) |entry| {
        const full_path = try guard.joinPath(allocator, root, entry.file);
        defer allocator.free(full_path);
        const text = guard.readUtf8File(io, allocator, full_path) catch |err| switch (err) {
            guard.GuardError.IOError => {
                try guard.appendMissingFileIssue(allocator, &failures, entry.file);
                continue;
            },
            else => return err,
        };
        defer allocator.free(text);
        const count = guard.countOccurrences(text, entry.marker);
        if (count != 1) {
            const issue = try std.fmt.allocPrint(allocator, "{s}:expected=1:actual={d}:{s}", .{ entry.file, count, entry.marker });
            try failures.append(allocator, issue);
        }
    }

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

