const std = @import("std");

fn readRepoFile(allocator: std.mem.Allocator, relative: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        relative,
        allocator,
        .limited(1024 * 1024),
    );
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "phase2 closure note keeps kconfig split and live gap explicit" {
    const allocator = std.testing.allocator;
    const closure = try readRepoFile(allocator, "Documentation/zigux/phase2-closure.md");
    defer allocator.free(closure);

    try requireContains(closure, "`PHASE2_KCONFIG_BRIDGE_CONF_HELPER_ANCHOR_COUNT=4`");
    try requireContains(closure, "`PHASE2_KCONFIG_BRIDGE_CONFDATA_CASE_COUNT=16`");
    try requireContains(closure, "`PHASE2_KCONFIG_BRIDGE_CONFDATA_HELPER_ANCHOR_COUNT=36`");
    try requireContains(closure, "`scripts/zigux/kconfig/confdata_bridge.zig`");
    try requireContains(closure, "`zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`");
    try requireContains(closure, "`PHASE2_CURRENT_GAP_PACKET=Documentation/zigux/phase2-kconfig-bridge-gap-survey.md`");
    try requireContains(closure, "current authenticated repo reads do not expose `scripts/kconfig/conf.c` or `scripts/kconfig/confdata.c` on `master`");
    try requireContains(closure, "request-plan `allconfig` overrides stay limited to `allmodconfig`, `alldefconfig`, and `randconfig`");
    try requireContains(closure, "`allconfig_sentinel_packet` still covers `allnoconfig` and `allyesconfig`");
    try requireNotContains(closure, "`PHASE2_CURRENT_GAP_PACKET=`\n");
}

test "kconfig manifests preserve conf and confdata fixture counts" {
    const allocator = std.testing.allocator;
    const conf = try readRepoFile(allocator, "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json");
    defer allocator.free(conf);
    const confdata = try readRepoFile(allocator, "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json");
    defer allocator.free(confdata);

    try requireContains(conf, "\"tool\": \"scripts/zigux/kconfig/conf_bridge.zig\"");
    try requireContains(conf, "\"case_count\": 16");
    try requireContains(conf, "\"allconfig_sentinel_packet\": [");
    try requireContains(conf, "\"allnoconfig_expected.json\"");
    try requireContains(conf, "\"allyesconfig_expected.json\"");
    try requireContains(conf, "\"allconfig_override_packet\": [");
    try requireContains(conf, "\"allmodconfig_expected.json\"");
    try requireContains(conf, "\"alldefconfig_expected.json\"");
    try requireContains(conf, "\"randconfig_expected.json\"");
    try requireContains(conf, "\"helper_local_allconfig_explicit_override_modes\": [");
    try requireContains(conf, "\"allyesconfig\"");

    try requireContains(confdata, "\"tool\": \"scripts/zigux/kconfig/confdata_bridge.zig\"");
    try requireContains(confdata, "\"case_count\": 16");
    try requireContains(confdata, "\"explicit_empty_assignments.config\"");
    try requireContains(confdata, "\"duplicate_malformed_quoted_assignment_expected.json\"");
    try requireContains(confdata, "\"confdata bridge preserves duplicate unset ownership on allocation failure\"");
}

test "kconfig cases keep request-plan override and sentinel modes separate" {
    const allocator = std.testing.allocator;
    const cases = try readRepoFile(allocator, "zigux/tests/fixtures/kconfig_bridge/cases.json");
    defer allocator.free(cases);

    try requireContains(cases, "\"name\": \"allnoconfig\"");
    try requireContains(cases, "\"name\": \"allyesconfig\"");
    try requireContains(cases, "\"name\": \"allmodconfig\"");
    try requireContains(cases, "\"name\": \"alldefconfig\"");
    try requireContains(cases, "\"name\": \"randconfig\"");
    try requireContains(cases, "\"allconfig\": \"\"");
    try requireContains(cases, "\"allconfig\": \"mini-all.config\"");
    try requireContains(cases, "\"seed\": \"0xC0FFEE\"");
    try requireContains(cases, "\"probability\": \"15:25\"");
    try requireContains(cases, "\"input\": \"explicit_empty_assignments.config\"");
}
