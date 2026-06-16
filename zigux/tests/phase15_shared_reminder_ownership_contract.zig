const std = @import("std");

const docs_readme_phase15 =
    \\Phase 15 notes - `Documentation/zigux/freeze-map.md` - `Documentation/zigux/phase15-freeze-map-governance.md` - `Documentation/zigux/phase15-architecture-council-review-process.md`
    \\`scripts\zigux/check_phase15_docs_readme_alignment.zig`, `scripts\zigux/check_phase15_architecture_council_packet.zig`, and `scripts\zigux/validate_phase15.zig` keep the current docs-root Phase 15 reminder packet reviewable while the remaining shared-summary follow-through stays limited to the handoff note, the shared-summary gap note, the scripts-root reminder, and the tests-root reminder rather than widening into deep-core delivery or approval claims.
    \\keep the Phase 15 reminder bounded below any Architecture Council approval claim
    \\no Architecture Council approval is currently recorded for a freeze-map status change
;

const scripts_readme_phase15 =
    \\Phase 15 flow - the current scripts-root governance reminder packet stays in maintenance-mode truthfulness work, keeping the landed freeze-map, readiness, handoff, parity, stay-in-C, study-only, and shared-summary surfaces aligned without implying Architecture Council approval or a deep-core port-readiness decision
    \\`scripts\zigux/check_phase15_docs_readme_alignment.zig`, `scripts\zigux/check_phase15_scripts_readme_alignment.zig`, `scripts\zigux/check_phase15_tests_readme_alignment.zig`, `scripts\zigux/check_phase15_architecture_council_packet.zig`, `scripts\zigux/check_phase15_review_process_handoff.zig`, `scripts\zigux/check_phase15_handoff_note_alignment.zig`, `scripts\zigux/check_phase15_review_checklist_study_only_alignment.zig`, `scripts\zigux/check_phase15_shared_summary_gap.zig`, `scripts\zigux/check_phase15_readiness_gate_packet.zig`, and `scripts\zigux/validate_phase15.zig` keep the current scripts-root governance packet explicit from the scripts root while the broader dedicated `phase15*` wrapper and shared-CI companions still stay blocked
    \\the directly readable `scripts\zigux/validate_phase15.zig` maintenance gate and the directly readable `zigux/tests/phase15_build.zig` shared build companion both remain part of the wider validator-first reminder family
    \\although `zigux/Makefile` is present on current `master`, it still does not materialize `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15`
    \\`.github/workflows/zigux-bootstrap.yml` is present on current `master`, but it still carries no dedicated Phase 15 validate, test, or aggregate route
    \\no Architecture Council approval is currently recorded for a freeze-map status change
;

const tests_readme_phase15 =
    \\## Phase 15 shared governance packet
    \\
    \\  * Keep Phase 15 governance wording separate from the Phase 14 shared smoke route until a dedicated Phase 15 checker expands this tests-root section.
;

const shared_summary_gap =
    \\The remaining Phase 15 discipline work is broad-summary truthfulness and route wording exactness, not missing-file recovery by wishful thinking
    \\`Documentation/zigux/README.md` now keeps a dedicated Phase 15 reminder packet explicit, so reread it with `scripts\zigux/check_phase15_docs_readme_alignment.zig`
    \\`scripts/zigux/README.md` now keeps the directly materialized `scripts\zigux/validate_phase15.zig` maintenance gate, the directly materialized `scripts\zigux/check_phase15_architecture_council_packet.zig` Architecture Council packet checker, and the directly materialized `zigux/tests/phase15_build.zig` shared build companion explicit
    \\the landed `zigux/tests/README.md` Phase 15 governance section still needs rereads with `scripts\zigux/check_phase15_tests_readme_alignment.zig`
    \\do not treat the parked make-route vocabulary or shared-CI route vocabulary as shipped evidence until direct current-tree reads recover them
;

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, haystack, needle) == null) {
        std.debug.print("missing marker: {s}\n", .{needle});
        return error.MissingMarker;
    }
}

fn requireAbsent(haystack: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, haystack, needle) != null) {
        std.debug.print("unexpected marker: {s}\n", .{needle});
        return error.UnexpectedMarker;
    }
}

test "scripts root owns reminder alignment without route or approval claims" {
    try requireContains(scripts_readme_phase15, "scripts-root governance reminder packet");
    try requireContains(scripts_readme_phase15, "without implying Architecture Council approval or a deep-core port-readiness decision");
    try requireContains(scripts_readme_phase15, "validate-phase15.py` maintenance gate");
    try requireContains(scripts_readme_phase15, "zigux/tests/phase15_build.zig` shared build companion");
    try requireContains(scripts_readme_phase15, "broader dedicated `phase15*` wrapper and shared-CI companions still stay blocked");
    try requireContains(scripts_readme_phase15, "still does not materialize `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15`");
    try requireContains(scripts_readme_phase15, "still carries no dedicated Phase 15 validate, test, or aggregate route");
    try requireContains(scripts_readme_phase15, "no Architecture Council approval is currently recorded for a freeze-map status change");
}

test "tests root stays a reminder section until dedicated checker expansion" {
    try requireContains(tests_readme_phase15, "Phase 15 shared governance packet");
    try requireContains(tests_readme_phase15, "governance wording separate from the Phase 14 shared smoke route");
    try requireContains(tests_readme_phase15, "until a dedicated Phase 15 checker expands this tests-root section");
    try requireAbsent(tests_readme_phase15, "make -C zigux phase15-validate");
    try requireAbsent(tests_readme_phase15, "Architecture Council approval");
}

test "docs root and shared gap keep reminder ownership bounded" {
    try requireContains(docs_readme_phase15, "shared-summary follow-through stays limited to the handoff note, the shared-summary gap note, the scripts-root reminder, and the tests-root reminder");
    try requireContains(docs_readme_phase15, "rather than widening into deep-core delivery or approval claims");
    try requireContains(docs_readme_phase15, "keep the Phase 15 reminder bounded below any Architecture Council approval claim");
    try requireContains(shared_summary_gap, "broad-summary truthfulness and route wording exactness");
    try requireContains(shared_summary_gap, "do not treat the parked make-route vocabulary or shared-CI route vocabulary as shipped evidence");
    try requireContains(shared_summary_gap, "scripts\zigux/check_phase15_tests_readme_alignment.zig");
}
