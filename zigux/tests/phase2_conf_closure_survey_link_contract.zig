const std = @import("std");

const closure_path = "Documentation/zigux/phase2-closure.md";
const conf_survey_path = "Documentation/zigux/phase2-conf-bridge-survey.md";
const kconfig_gap_path = "Documentation/zigux/phase2-kconfig-bridge-gap-survey.md";

const closure_current_shared_tooling_packet =
    \\- `scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`, `scripts/zigux/check-phase2-cross.py`, `Documentation/zigux/phase2-fixdep-dual-implementation-survey.md`, `zigux/tests/fixtures/phase2_cross_targets.json`, `scripts/zigux/check-phase2-fixdep-gate.py`, and `scripts/zigux/check-fixdep-diff.py` keep the helper-local kconfig, direct cross-route, and fixdep governance/parity packet directly replayable beside the closure note.
    \\- `Documentation/zigux/phase2-conf-bridge-survey.md` remains the dedicated conf bridge survey note for the live `conf_bridge.zig`, checker, fixture roster, manifest, and closure-reminder packet.
    \\- `scripts/zigux/kconfig/confdata_bridge.zig`, `scripts/zigux/check-kconfig-bridge.py`, and `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json` keep the bounded `confdata.c` bridge replay packet directly readable at 16 committed fixture cases and 36 helper-local anchors.
;

const closure_gap_packet =
    \\- `PHASE2_CURRENT_GAP_PACKET=Documentation/zigux/phase2-kconfig-bridge-gap-survey.md`
    \\- current authenticated repo reads do not expose `scripts/kconfig/conf.c` or `scripts/kconfig/confdata.c` on `master`, so the shipped kconfig bridge packet remains fixture-backed rather than same-tree differential
;

const conf_survey_gap_packet =
    \\- One shared reminder mismatch still remains adjacent to this bridge-local packet: `Documentation/zigux/phase2-conf-bridge-survey.md` is the dedicated current-master note for this conf-side packet, but `Documentation/zigux/phase2-closure.md` still undercounts that bridge-family reminder surface by listing the bridge source, checker, fixtures, and manifests without naming this survey note.
;

const conf_survey_next_step =
    \\- If the adjacent shared reminder undercount is still live when this family reopens, update `Documentation/zigux/phase2-closure.md` so the shared Phase 2 closure packet explicitly names this dedicated survey note.
;

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.FirstMarkerMissing;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.SecondMarkerMissing;
    try std.testing.expect(first_index < second_index);
}

test "phase2 closure names the dedicated conf bridge survey note" {
    try expectContains(closure_current_shared_tooling_packet, conf_survey_path);
    try expectContains(closure_current_shared_tooling_packet, "`scripts/zigux/kconfig/confdata_bridge.zig`");
    try expectContains(closure_current_shared_tooling_packet, "`scripts/zigux/check-kconfig-bridge.py`");
    try expectContains(closure_current_shared_tooling_packet, "`zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`");
}

test "conf bridge survey still records why the closure link matters" {
    try expectContains(conf_survey_gap_packet, "dedicated current-master note for this conf-side packet");
    try expectContains(conf_survey_next_step, "shared Phase 2 closure packet explicitly names this dedicated survey note");
    try expectContains(conf_survey_gap_packet, closure_path);
}

test "closure keeps separate kconfig gap and genksyms survey surfaces intact" {
    try expectContains(closure_current_shared_tooling_packet, "Documentation/zigux/phase2-fixdep-dual-implementation-survey.md");
    try expectContains(closure_gap_packet, kconfig_gap_path);
    try expectBefore(closure_current_shared_tooling_packet ++ closure_gap_packet, conf_survey_path, kconfig_gap_path);
}
