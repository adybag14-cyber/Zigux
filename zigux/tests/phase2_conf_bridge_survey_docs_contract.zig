const std = @import("std");

const survey_note =
    \\# Phase 2 Conf Bridge Survey
    \\
    \\This note records the current `master` readback for the roadmap-backed `scripts/zigux/kconfig/conf_bridge.zig` bridge so Phase 2 review stays grounded in the live scaffold packet instead of replaying older already-landed or now-drifted claims.
    \\
    \\- Phase 2 keeps `scripts/kconfig/conf.c` inside the bounded toolchain and Kbuild enablement tranche.
    \\- The roadmap's recommended Zigux destination is `scripts/zigux/kconfig/conf_bridge.zig` beside `scripts/zigux/kconfig/confdata_bridge.zig`.
    \\- The bootstrap ledger's bounded kconfig bridge scaffolding packet centers on `scripts/zigux/kconfig/conf_bridge.zig`, `scripts/zigux/check-kconfig-bridge.py`, and `zigux/tests/fixtures/kconfig_bridge/`.
    \\- `scripts/zigux/kconfig/conf_bridge.zig` is present on `master` and still ships the bounded request-plan bridge shape: a `Mode` enum with the live sixteen-mode surface, a `runConfBridge()` JSON emitter, a CLI `main()` wrapper, and helper-local tests covering mode text and flag mapping, mode-argument validation, silent handling, syncconfig environment wiring, allconfig handling, randconfig tunables, and option-parser duplicate rejection.
    \\- `scripts/zigux/check-kconfig-bridge.py` is present on `master` and still treats the conf-side packet as a bounded bridge-plus-fixture surface, with the current required mode inventory, manifest packet checks, and helper-anchor inventory review.
    \\- `zigux/tests/fixtures/kconfig_bridge/cases.json` currently keeps a `conf_cases` packet with 16 cases: `oldaskconfig`, `syncconfig`, `oldconfig`, `allnoconfig`, `allyesconfig`, `allmodconfig`, `alldefconfig`, `randconfig`, `defconfig`, `savedefconfig`, `listnewconfig`, `helpnewconfig`, `olddefconfig`, `yes2modconfig`, `mod2yesconfig`, and `mod2noconfig`.
    \\- `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json` is present, marks the tool `closed`, records the same 16-case packet, keeps `randconfig_expected.json` in the override packet, limits `allconfig_sentinel_packet` to `allnoconfig_expected.json` and `allyesconfig_expected.json`, keeps the fixture-backed `allconfig_override_packet` on `allmodconfig_expected.json`, `alldefconfig_expected.json`, and `randconfig_expected.json`, and currently inventories a five-mode `helper_local_allconfig_explicit_override_modes` reminder: `allmodconfig`, `allnoconfig`, `allyesconfig`, `alldefconfig`, and `randconfig`.
    \\- `Documentation/zigux/phase2-closure.md` still lists `scripts/zigux/kconfig/conf_bridge.zig`, `scripts/zigux/kconfig/confdata_bridge.zig`, `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`, and `zigux/tests/fixtures/kconfig_bridge/cases.json` inside the current directly readable Phase 2 closure packet.
    \\- `current master` does not have a remaining roadmap gap at the level of conf bridge scaffolding.
    \\- The honest survey-level result is back to a parked bridge-local story: bridge behavior and expected-output parity for the existing 16 fixture-backed cases are closed on current `master`, and the checker plus manifest now count the same explicit-override helper coverage that the shipped bridge code already exercises.
    \\- Fixture-backed explicit override governance remains narrower than helper-local behavior on current `master`: the `conf_cases` packet still only materializes explicit override expected-output coverage through `allmodconfig`, `alldefconfig`, and `randconfig`, so `allnoconfig` and `allyesconfig` explicit overrides are still helper-local coverage only today.
    \\- Keep the bridge-local survey packet parked unless a future current-master reread finds a fresh bridge-only truthfulness drift.
;

const closure_note =
    \\- `Documentation/zigux/phase2-conf-bridge-survey.md` remains the dedicated conf bridge survey note for the live `conf_bridge.zig`, checker, fixture roster, manifest, and closure-reminder packet.
    \\- `PHASE2_KCONFIG_BRIDGE_CONF_HELPER_ANCHOR_COUNT=4`
    \\- `scripts/zigux/kconfig/confdata_bridge.zig`, `scripts/zigux/check-kconfig-bridge.py`, and `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json` keep the bounded `confdata.c` bridge replay packet directly readable at 16 committed fixture cases and 36 helper-local anchors.
;

const conf_manifest =
    \\{
    \\  "tool": "scripts/zigux/kconfig/conf_bridge.zig",
    \\  "status": "closed",
    \\  "mode": "bounded request-plan bridge",
    \\  "fixture_case_source": "zigux/tests/fixtures/kconfig_bridge/cases.json",
    \\  "case_count": 16,
    \\  "allconfig_sentinel_packet": [
    \\    "allnoconfig_expected.json",
    \\    "allyesconfig_expected.json"
    \\  ],
    \\  "allconfig_override_packet": [
    \\    "allmodconfig_expected.json",
    \\    "alldefconfig_expected.json",
    \\    "randconfig_expected.json"
    \\  ],
    \\  "helper_local_allconfig_explicit_override_modes": [
    \\    "allmodconfig",
    \\    "allnoconfig",
    \\    "allyesconfig",
    \\    "alldefconfig",
    \\    "randconfig"
    \\  ]
    \\}
;

const conf_bridge_source =
    \\pub const Mode = enum {
    \\    oldaskconfig,
    \\    syncconfig,
    \\    oldconfig,
    \\    allnoconfig,
    \\    allyesconfig,
    \\    allmodconfig,
    \\    alldefconfig,
    \\    randconfig,
    \\    defconfig,
    \\    savedefconfig,
    \\    listnewconfig,
    \\    helpnewconfig,
    \\    olddefconfig,
    \\    yes2modconfig,
    \\    mod2yesconfig,
    \\    mod2noconfig,
    \\
    \\pub const Request = struct {
    \\    mode: Mode,
    \\    kconfig: []const u8,
    \\    config: []const u8,
    \\    arch: []const u8,
    \\    silent: bool = false,
    \\    mode_arg: ?[]const u8 = null,
;

const conf_cases =
    \\"oldaskconfig"
    \\"syncconfig"
    \\"oldconfig"
    \\"allnoconfig"
    \\"allyesconfig"
    \\"allmodconfig"
    \\"alldefconfig"
    \\"randconfig"
    \\"defconfig"
    \\"savedefconfig"
    \\"listnewconfig"
    \\"helpnewconfig"
    \\"olddefconfig"
    \\"yes2modconfig"
    \\"mod2yesconfig"
    \\"mod2noconfig"
;

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBefore;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfter;
    try std.testing.expect(before_index < after_index);
}

test "conf bridge survey keeps roadmap, source, checker, fixture, and closure anchors explicit" {
    try expectContains(survey_note, "Phase 2 keeps `scripts/kconfig/conf.c` inside the bounded toolchain and Kbuild enablement tranche.");
    try expectContains(survey_note, "`scripts/zigux/kconfig/conf_bridge.zig` beside `scripts/zigux/kconfig/confdata_bridge.zig`");
    try expectContains(survey_note, "`scripts/zigux/check-kconfig-bridge.py`");
    try expectContains(survey_note, "`zigux/tests/fixtures/kconfig_bridge/cases.json` currently keeps a `conf_cases` packet with 16 cases");
    try expectContains(survey_note, "`zigux/tests/fixtures/kconfig_bridge/conf_manifest.json` is present, marks the tool `closed`");
    try expectContains(survey_note, "`Documentation/zigux/phase2-closure.md` still lists `scripts/zigux/kconfig/conf_bridge.zig`");
    try expectContains(closure_note, "`Documentation/zigux/phase2-conf-bridge-survey.md` remains the dedicated conf bridge survey note");
    try expectContains(closure_note, "`PHASE2_KCONFIG_BRIDGE_CONF_HELPER_ANCHOR_COUNT=4`");
}

test "conf bridge manifest and fixture roster keep the sixteen-mode request-plan packet" {
    try expectContains(conf_manifest, "\"status\": \"closed\"");
    try expectContains(conf_manifest, "\"mode\": \"bounded request-plan bridge\"");
    try expectContains(conf_manifest, "\"case_count\": 16");
    try expectContains(conf_manifest, "\"fixture_case_source\": \"zigux/tests/fixtures/kconfig_bridge/cases.json\"");
    try expectContains(conf_bridge_source, "pub const Mode = enum");
    try expectContains(conf_bridge_source, "pub const Request = struct");

    const modes = [_][]const u8{
        "oldaskconfig",
        "syncconfig",
        "oldconfig",
        "allnoconfig",
        "allyesconfig",
        "allmodconfig",
        "alldefconfig",
        "randconfig",
        "defconfig",
        "savedefconfig",
        "listnewconfig",
        "helpnewconfig",
        "olddefconfig",
        "yes2modconfig",
        "mod2yesconfig",
        "mod2noconfig",
    };

    for (modes) |mode| {
        try expectContains(conf_cases, mode);
        try expectContains(conf_bridge_source, mode);
    }
}

test "conf bridge survey preserves explicit allconfig governance split" {
    try expectContains(survey_note, "Fixture-backed explicit override governance remains narrower than helper-local behavior");
    try expectContains(survey_note, "`allnoconfig` and `allyesconfig` explicit overrides are still helper-local coverage only today.");
    try expectContains(conf_manifest, "\"allconfig_sentinel_packet\"");
    try expectContains(conf_manifest, "\"allconfig_override_packet\"");
    try expectContains(conf_manifest, "\"helper_local_allconfig_explicit_override_modes\"");
    try expectOrdered(conf_manifest, "\"allconfig_sentinel_packet\"", "\"allconfig_override_packet\"");
    try expectOrdered(conf_manifest, "\"allconfig_override_packet\"", "\"helper_local_allconfig_explicit_override_modes\"");
    try expectContains(conf_manifest, "\"allnoconfig_expected.json\"");
    try expectContains(conf_manifest, "\"allyesconfig_expected.json\"");
    try expectContains(conf_manifest, "\"allmodconfig_expected.json\"");
    try expectContains(conf_manifest, "\"alldefconfig_expected.json\"");
    try expectContains(conf_manifest, "\"randconfig_expected.json\"");
}
