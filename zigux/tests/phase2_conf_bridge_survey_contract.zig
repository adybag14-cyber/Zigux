const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.EarlierMarkerMissing;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.LaterMarkerMissing;
    try std.testing.expect(earlier_index < later_index);
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(512 * 1024));
}

test "conf bridge survey keeps the live bridge packet grounded" {
    const allocator = std.testing.allocator;
    const survey = try readRepoFile(allocator, "Documentation/zigux/phase2-conf-bridge-survey.md");
    defer allocator.free(survey);

    try expectContains(survey, "# Phase 2 Conf Bridge Survey");
    try expectContains(survey, "`scripts/zigux/kconfig/conf_bridge.zig` bridge");
    try expectContains(survey, "Phase 2 keeps `scripts/kconfig/conf.c` inside the bounded toolchain and Kbuild enablement tranche.");
    try expectContains(survey, "a `Mode` enum with the live sixteen-mode surface");
    try expectContains(survey, "a `runConfBridge()` JSON emitter");
    try expectContains(survey, "helper-local tests covering mode text and flag mapping");
    try expectContains(survey, "`zigux/tests/fixtures/kconfig_bridge/cases.json` currently keeps a `conf_cases` packet with 16 cases");
    try expectContains(survey, "`Documentation/zigux/phase2-closure.md` still lists `scripts/zigux/kconfig/conf_bridge.zig`");
    try expectContains(survey, "`current master` does not have a remaining roadmap gap at the level of conf bridge scaffolding.");
}

test "conf bridge survey matches manifest and checker allconfig split" {
    const allocator = std.testing.allocator;
    const survey = try readRepoFile(allocator, "Documentation/zigux/phase2-conf-bridge-survey.md");
    defer allocator.free(survey);
    const conf_manifest = try readRepoFile(allocator, "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json");
    defer allocator.free(conf_manifest);
    const checker = try readRepoFile(allocator, "scripts/zigux/check-kconfig-bridge.py");
    defer allocator.free(checker);
    const conf_bridge = try readRepoFile(allocator, "scripts/zigux/kconfig/conf_bridge.zig");
    defer allocator.free(conf_bridge);

    try expectContains(survey, "records the same 16-case packet");
    try expectContains(survey, "limits `allconfig_sentinel_packet` to `allnoconfig_expected.json` and `allyesconfig_expected.json`");
    try expectContains(survey, "keeps the fixture-backed `allconfig_override_packet` on `allmodconfig_expected.json`, `alldefconfig_expected.json`, and `randconfig_expected.json`");
    try expectContains(survey, "a five-mode `helper_local_allconfig_explicit_override_modes` reminder: `allmodconfig`, `allnoconfig`, `allyesconfig`, `alldefconfig`, and `randconfig`");
    try expectContains(survey, "allnoconfig` and `allyesconfig` explicit overrides are still helper-local coverage only today");

    try expectContains(conf_manifest, "\"case_count\": 16");
    try expectContains(conf_manifest, "\"allconfig_sentinel_packet\": [");
    try expectContains(conf_manifest, "\"allnoconfig_expected.json\"");
    try expectContains(conf_manifest, "\"allyesconfig_expected.json\"");
    try std.testing.expect(std.mem.indexOf(u8, conf_manifest, "\"allconfig_sentinel_packet\": [\n    \"allnoconfig_expected.json\",\n    \"allyesconfig_expected.json\",\n    \"alldefconfig_expected.json\"") == null);
    try expectContains(conf_manifest, "\"allconfig_override_packet\": [");
    try expectContains(conf_manifest, "\"allmodconfig_expected.json\"");
    try expectContains(conf_manifest, "\"alldefconfig_expected.json\"");
    try expectContains(conf_manifest, "\"randconfig_expected.json\"");
    try expectContains(checker, "REQUIRED_CONF_HELPER_ANCHORS");
    try expectContains(checker, "\"conf bridge emits explicit empty allconfig override for allmodconfig\"");
    try expectContains(checker, "\"conf bridge emits randconfig tunables when present\"");
    try expectContains(conf_bridge, "fn modeUsesAllConfigSentinel(mode: Mode) bool");
    try expectContains(conf_bridge, "fn modeAcceptsAllConfigOverride(mode: Mode) bool");
}

test "conf bridge survey stays parked below wider closure or confdata work" {
    const allocator = std.testing.allocator;
    const survey = try readRepoFile(allocator, "Documentation/zigux/phase2-conf-bridge-survey.md");
    defer allocator.free(survey);
    const closure = try readRepoFile(allocator, "Documentation/zigux/phase2-closure.md");
    defer allocator.free(closure);

    try expectContains(survey, "The live Phase 2 packet still contains the bridge source, checker, fixture roster, manifest, dedicated survey note, and shared closure reminder surfaces");
    try expectContains(survey, "bridge behavior and expected-output parity for the existing 16 fixture-backed cases are closed on current `master`");
    try expectContains(survey, "The remaining follow-through is the adjacent shared closure-note reminder undercount");
    try expectContains(survey, "Keep the bridge-local survey packet parked unless a future current-master reread finds a fresh bridge-only truthfulness drift.");
    try expectContains(survey, "Do not widen this note into broader Phase 2 closure maintenance");
    try expectContains(survey, "confdata work unless the bridge-only reminder surfaces drift again");

    try expectContains(closure, "scripts/zigux/kconfig/conf_bridge.zig");
    try expectContains(closure, "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json");
    try expectContains(closure, "zigux/tests/fixtures/kconfig_bridge/cases.json");
    try expectBefore(survey, "## Survey Result", "## Next Bounded Step");
}

test "conf bridge fixture roster remains sixteen mode scoped" {
    const allocator = std.testing.allocator;
    const cases = try readRepoFile(allocator, "zigux/tests/fixtures/kconfig_bridge/cases.json");
    defer allocator.free(cases);
    const conf_manifest = try readRepoFile(allocator, "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json");
    defer allocator.free(conf_manifest);
    const checker = try readRepoFile(allocator, "scripts/zigux/check-kconfig-bridge.py");
    defer allocator.free(checker);

    const expected_modes = [_][]const u8{
        "\"oldaskconfig\"",
        "\"syncconfig\"",
        "\"oldconfig\"",
        "\"allnoconfig\"",
        "\"allyesconfig\"",
        "\"allmodconfig\"",
        "\"alldefconfig\"",
        "\"randconfig\"",
        "\"defconfig\"",
        "\"savedefconfig\"",
        "\"listnewconfig\"",
        "\"helpnewconfig\"",
        "\"olddefconfig\"",
        "\"yes2modconfig\"",
        "\"mod2yesconfig\"",
        "\"mod2noconfig\"",
    };

    try expectContains(cases, "\"conf_cases\": [");
    inline for (expected_modes) |mode| {
        try expectContains(cases, mode);
        try expectContains(conf_manifest, mode);
    }
    try expectContains(conf_manifest, "\"case_count\": 16");
    try expectContains(checker, "REQUIRED_CONF_HELPER_ANCHORS");
}
