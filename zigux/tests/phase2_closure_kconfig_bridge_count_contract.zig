const std = @import("std");

const closure_note =
    \\- `PHASE2_KCONFIG_BRIDGE_CONF_HELPER_ANCHOR_COUNT=4`
    \\- `PHASE2_KCONFIG_BRIDGE_CONFDATA_CASE_COUNT=16`
    \\- `PHASE2_KCONFIG_BRIDGE_CONFDATA_HELPER_ANCHOR_COUNT=36`
    \\- current authenticated repo reads do not expose `scripts/kconfig/conf.c` or `scripts/kconfig/confdata.c` on `master`, so the shipped kconfig bridge packet remains fixture-backed rather than same-tree differential
    \\- the next same-family truthfulness pass should keep reminder surfaces aligned with the live split recorded in `zigux/tests/fixtures/kconfig_bridge/cases.json` and `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`: request-plan `allconfig` overrides stay limited to `allmodconfig`, `alldefconfig`, and `randconfig`, `allconfig_sentinel_packet` still covers `allnoconfig` and `allyesconfig`, and the helper-local explicit-override roster remains broader by design
;

const conf_manifest = @embedFile("fixtures/kconfig_bridge/conf_manifest.json");
const confdata_manifest = @embedFile("fixtures/kconfig_bridge/confdata_manifest.json");
const cases_manifest = @embedFile("fixtures/kconfig_bridge/cases.json");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var rest = haystack;
    while (std.mem.indexOf(u8, rest, needle)) |index| {
        count += 1;
        rest = rest[index + needle.len ..];
    }
    return count;
}

test "closure note pins current kconfig bridge count sentinels" {
    try expectContains(closure_note, "PHASE2_KCONFIG_BRIDGE_CONF_HELPER_ANCHOR_COUNT=4");
    try expectContains(closure_note, "PHASE2_KCONFIG_BRIDGE_CONFDATA_CASE_COUNT=16");
    try expectContains(closure_note, "PHASE2_KCONFIG_BRIDGE_CONFDATA_HELPER_ANCHOR_COUNT=36");
    try expectContains(closure_note, "fixture-backed rather than same-tree differential");
    try expectNotContains(closure_note, "PHASE2_KCONFIG_BRIDGE_CONFDATA_CASE_COUNT=15");
    try expectNotContains(closure_note, "PHASE2_KCONFIG_BRIDGE_CONFDATA_HELPER_ANCHOR_COUNT=28");
}

test "kconfig bridge manifests keep the current 16 case packet" {
    try expectContains(conf_manifest, "\"tool\": \"scripts/zigux/kconfig/conf_bridge.zig\"");
    try expectContains(conf_manifest, "\"case_count\": 16");
    try expectContains(conf_manifest, "\"fixture_case_source\": \"zigux/tests/fixtures/kconfig_bridge/cases.json\"");

    try expectContains(confdata_manifest, "\"tool\": \"scripts/zigux/kconfig/confdata_bridge.zig\"");
    try expectContains(confdata_manifest, "\"case_count\": 16");
    try expectContains(confdata_manifest, "\"fixture_case_source\": \"zigux/tests/fixtures/kconfig_bridge/cases.json\"");

    try std.testing.expectEqual(@as(usize, 16), countOccurrences(confdata_manifest, "_expected.json\""));
    try expectContains(cases_manifest, "\"name\": \"mod2noconfig\"");
    try expectContains(confdata_manifest, "\"explicit_empty_assignments\"");
}

test "closure split remains narrower than helper-local kconfig coverage" {
    try expectContains(closure_note, "request-plan `allconfig` overrides stay limited to `allmodconfig`, `alldefconfig`, and `randconfig`");
    try expectContains(closure_note, "`allconfig_sentinel_packet` still covers `allnoconfig` and `allyesconfig`");
    try expectContains(closure_note, "helper-local explicit-override roster remains broader by design");

    try expectContains(conf_manifest, "\"allconfig_override_packet\"");
    try expectContains(conf_manifest, "\"allmodconfig_expected.json\"");
    try expectContains(conf_manifest, "\"alldefconfig_expected.json\"");
    try expectContains(conf_manifest, "\"randconfig_expected.json\"");
    try expectContains(conf_manifest, "\"allconfig_sentinel_packet\"");
    try expectContains(conf_manifest, "\"allnoconfig_expected.json\"");
    try expectContains(conf_manifest, "\"allyesconfig_expected.json\"");
    try expectContains(conf_manifest, "\"allmodconfig\"");
    try expectContains(conf_manifest, "\"randconfig\"");

    try std.testing.expectEqual(@as(usize, 36), countOccurrences(confdata_manifest, "\"confdata bridge "));
}
