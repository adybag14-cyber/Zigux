const std = @import("std");

const conf_helper_anchor_count = 28;
const conf_bridge_helper_anchor_count = 15;
const conf_mode_argument_helper_anchor_count = 3;
const conf_bridge_options_helper_anchor_count = 10;
const confdata_case_count = 16;
const confdata_helper_anchor_count = 36;

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        allocator,
        .limited(1024 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectExactCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, offset, needle)) |index| {
        count += 1;
        offset = index + needle.len;
    }
    try std.testing.expectEqual(expected, count);
}

fn expectNumberMarker(source: []const u8, comptime fmt: []const u8, value: usize) !void {
    var marker: [96]u8 = undefined;
    const rendered = try std.fmt.bufPrint(&marker, fmt, .{value});
    try expectContains(source, rendered);
}

test "phase2 closure note pins kconfig and confdata count markers" {
    const allocator = std.testing.allocator;
    const closure = try readRepoFile(allocator, "Documentation/zigux/phase2-closure.md");
    defer allocator.free(closure);

    try expectNumberMarker(closure, "`PHASE2_KCONFIG_BRIDGE_CONF_HELPER_ANCHOR_COUNT={}`", conf_helper_anchor_count);
    try expectNumberMarker(closure, "`PHASE2_KCONFIG_BRIDGE_CONFDATA_CASE_COUNT={}`", confdata_case_count);
    try expectNumberMarker(closure, "`PHASE2_KCONFIG_BRIDGE_CONFDATA_HELPER_ANCHOR_COUNT={}`", confdata_helper_anchor_count);
    try expectContains(closure, "`scripts/zigux/kconfig/confdata_bridge.zig`, `scripts/zigux/check-kconfig-bridge.py`, and `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`");
    try expectContains(closure, "request-plan `allconfig` overrides stay limited to `allmodconfig`, `alldefconfig`, and `randconfig`");
    try expectContains(closure, "`allconfig_sentinel_packet` still covers `allnoconfig` and `allyesconfig`");
    try expectContains(closure, "helper-local explicit-override roster remains broader by design");
}

test "phase2 kconfig manifests keep helper counts aligned with closure markers" {
    const allocator = std.testing.allocator;
    const conf_manifest = try readRepoFile(allocator, "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json");
    defer allocator.free(conf_manifest);
    const confdata_manifest = try readRepoFile(allocator, "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json");
    defer allocator.free(confdata_manifest);

    try expectNumberMarker(conf_manifest, "\"case_count\": {}", 16);
    try expectExactCount(conf_manifest, "\"conf bridge ", conf_bridge_helper_anchor_count);
    try expectExactCount(conf_manifest, "\"mode argument ", conf_mode_argument_helper_anchor_count);
    try expectExactCount(conf_manifest, "\"bridge options ", conf_bridge_options_helper_anchor_count);
    try expectContains(conf_manifest, "\"allconfig_sentinel_packet\"");
    try expectContains(conf_manifest, "\"allnoconfig_expected.json\"");
    try expectContains(conf_manifest, "\"allyesconfig_expected.json\"");
    try expectContains(conf_manifest, "\"allconfig_override_packet\"");
    try expectContains(conf_manifest, "\"allmodconfig_expected.json\"");
    try expectContains(conf_manifest, "\"alldefconfig_expected.json\"");
    try expectContains(conf_manifest, "\"randconfig_expected.json\"");
    try expectContains(conf_manifest, "\"helper_local_allconfig_explicit_override_modes\"");
    try expectContains(conf_manifest, "\"allnoconfig\"");
    try expectContains(conf_manifest, "\"allyesconfig\"");

    try expectNumberMarker(confdata_manifest, "\"case_count\": {}", confdata_case_count);
    try expectExactCount(confdata_manifest, "\"confdata bridge ", confdata_helper_anchor_count);
    try expectContains(confdata_manifest, "\"confdata bridge file reader accepts config inputs beyond one mebibyte\"");
    try expectContains(confdata_manifest, "\"confdata bridge releases appended entry ownership on index-allocation failure\"");
    try expectContains(confdata_manifest, "\"confdata bridge preserves duplicate unset ownership on allocation failure\"");
}

test "phase2 helper checkers and readmes keep kconfig count packet discoverable" {
    const allocator = std.testing.allocator;
    const allconfig_checker = try readRepoFile(allocator, "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py");
    defer allocator.free(allconfig_checker);
    const bridge_checker = try readRepoFile(allocator, "scripts/zigux/check-kconfig-bridge.py");
    defer allocator.free(bridge_checker);
    const scripts_readme = try readRepoFile(allocator, "scripts/zigux/README.md");
    defer allocator.free(scripts_readme);
    const tests_readme = try readRepoFile(allocator, "zigux/tests/README.md");
    defer allocator.free(tests_readme);

    try expectContains(allconfig_checker, "\"PHASE2_KCONFIG_BRIDGE_CONF_HELPER_ANCHOR_COUNT=4\"");
    try expectContains(allconfig_checker, "\"scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py\"");
    try expectContains(bridge_checker, "REQUIRED_CONF_HELPER_ANCHORS = [");
    try expectContains(bridge_checker, "REQUIRED_CONFDATA_HELPER_ANCHORS = [");
    try expectContains(bridge_checker, "EXPECTED_SELF_TEST_CASE_COUNT = 7");

    try expectContains(scripts_readme, "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py");
    try expectContains(scripts_readme, "scripts/zigux/kconfig/confdata_bridge.zig");
    try expectContains(scripts_readme, "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json");
    try expectContains(tests_readme, "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py");
    try expectContains(tests_readme, "scripts/zigux/kconfig/confdata_bridge.zig");
    try expectContains(tests_readme, "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json");
}
