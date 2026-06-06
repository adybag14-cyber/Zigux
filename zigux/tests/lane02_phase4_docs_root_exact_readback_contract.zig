const std = @import("std");

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "lane02 phase4 docs root keeps the exact-readback packet bounded" {
    const docs_readme = try readRepoFile(std.testing.allocator, "Documentation/zigux/README.md");
    defer std.testing.allocator.free(docs_readme);

    try expectContains(
        docs_readme,
        "## Phase 4 Exact-Readback Reminder",
    );
    try expectContains(
        docs_readme,
        "the current docs-root Phase 4 reminder packet should stay parked on the directly readable helper",
    );
    try expectContains(
        docs_readme,
        "current `master` keeps the broader Phase 4 validator, build, and bitmap replay companions in a split-readback state rather than the missing bucket",
    );
    try expectContains(
        docs_readme,
        "`scripts/zigux/validate-phase4.py` now rereads directly in authenticated contents reads",
    );
    try expectContains(
        docs_readme,
        "`zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` still flap",
    );
    try expectContains(
        docs_readme,
        "exact authenticated blob-pin refresh remains pending for those three routes",
    );
}

test "lane02 phase4 review checklist keeps rollback and perf ownership prompts explicit" {
    const review_checklist = try readRepoFile(std.testing.allocator, "Documentation/zigux/review-checklist.md");
    defer std.testing.allocator.free(review_checklist);

    try expectContains(
        review_checklist,
        "if the change touches the shared Phase 4 rollback-ownership and lab-matrix packet",
    );
    try expectContains(
        review_checklist,
        "`Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase4-tests-readme-packet.py`, `scripts/zigux/check-phase4-repo-reality-warning.py`, and `scripts/zigux/check-phase4-reversible-delivery-pins.py` still agree on the current direct-readback packet",
    );
    try expectContains(
        review_checklist,
        "keep the directly readable local-only perf packet explicit",
    );
    try expectContains(
        review_checklist,
        "keep the roadmap-backed `atomic64_diff` pair explicit as direct current-head evidence",
    );
    try expectContains(
        review_checklist,
        "keep the Validation and Perf Team as the decision owner for any broader shared-CI perf promotion",
    );
    try expectContains(
        review_checklist,
        "keep the pending shared-CI perf-promotion posture explicit instead of implying shared CI perf approval",
    );
}

test "lane02 phase4 handoff note keeps mixed-provenance exact-readback status visible" {
    const phase4_note = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase4-reversible-delivery-evidence.md");
    defer std.testing.allocator.free(phase4_note);

    try expectContains(
        phase4_note,
        "PHASE4_REVERSIBLE_DELIVERY_STATUS=shared_evidence_packet_keeps_archival_self_pins_and_flapping_broader_blob_refresh_debt",
    );
    try expectContains(
        phase4_note,
        "PHASE4_REVERSIBLE_DELIVERY_EXACT_READBACK_REF=master",
    );
    try expectContains(
        phase4_note,
        "PHASE4_REPO_REALITY_WARNING_SELF_TEST_CASES=32",
    );
    try expectContains(
        phase4_note,
        "PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=20",
    );
    try expectContains(
        phase4_note,
        "Current direct-readback packet members:",
    );
    try expectContains(
        phase4_note,
        "The Phase 4 blob-pin lines therefore remain mixed provenance in this handoff:",
    );
    try expectContains(
        phase4_note,
        "current-head blob-pin proof for `scripts/zigux/validate-phase4.py` on `master`",
    );
    try expectContains(
        phase4_note,
        "public-raw current-tree proof that `zigux/tests/phase4_build.zig`, `zigux/tests/bitmap_diff.zig`, and `zigux/tests/phase4_bitmap_live_helper_replay.zig` are present again on `master`",
    );
    try expectContains(
        phase4_note,
        "historical blob-pin provenance for that broader build-and-bitmap trio until exact authenticated blob capture stabilizes",
    );
    try expectNotContains(
        phase4_note,
        "shared CI perf approval",
    );
}

test "lane02 phase4 checker pair preserves stale-claim fail-closed counts" {
    const repo_reality_checker = try readRepoFile(std.testing.allocator, "scripts/zigux/check-phase4-repo-reality-warning.py");
    defer std.testing.allocator.free(repo_reality_checker);
    const pin_checker = try readRepoFile(std.testing.allocator, "scripts/zigux/check-phase4-reversible-delivery-pins.py");
    defer std.testing.allocator.free(pin_checker);

    try expectContains(
        repo_reality_checker,
        "EXPECTED_REPO_REALITY_WARNING_SELF_TEST_CASES = 32",
    );
    try expectContains(
        repo_reality_checker,
        "EXPECTED_PIN_SELF_TEST_CASES = 20",
    );
    try expectContains(
        repo_reality_checker,
        "The Phase 4 blob-pin lines therefore remain mixed provenance in this handoff:",
    );
    try expectContains(
        pin_checker,
        "EXPECTED_REPO_REALITY_WARNING_SELF_TEST_CASES = 32",
    );
    try expectContains(
        pin_checker,
        "EXPECTED_PIN_SELF_TEST_CASES = 20",
    );
    try expectContains(
        pin_checker,
        "PIN_SELF_TEST_COUNT_LABEL = \"PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT\"",
    );
    try expectContains(
        pin_checker,
        "LEGACY_PIN_SELF_TEST_CASES_LABEL = \"PHASE4_REVERSIBLE_DELIVERY_PINS_SELF_TEST_CASES\"",
    );
}
