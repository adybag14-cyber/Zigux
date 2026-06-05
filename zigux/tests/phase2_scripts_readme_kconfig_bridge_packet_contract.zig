const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectAbsent(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "scripts readme keeps the phase 2 kconfig bridge packet explicit" {
    const scripts_readme = try readRepoFile("scripts/zigux/README.md", 160 * 1024);
    defer std.testing.allocator.free(scripts_readme);

    try expectContains(scripts_readme, "scripts/zigux/check-phase2-kconfig-selftest-alignment.py");
    try expectContains(scripts_readme, "scripts/zigux/kconfig/conf_bridge.zig");
    try expectContains(scripts_readme, "scripts/zigux/kconfig/confdata_bridge.zig");
    try expectContains(scripts_readme, "zigux/tests/fixtures/kconfig_bridge/cases.json");
    try expectContains(scripts_readme, "keep the manifest-backed kconfig fixture roster explicit");
    try expectContains(scripts_readme, "phase2-kconfig");

    try expectBefore(
        scripts_readme,
        "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
        "zigux/tests/fixtures/kconfig_bridge/cases.json",
    );
}

test "closure note keeps kconfig helper-count sentinels aligned with scripts root" {
    const closure_note = try readRepoFile("Documentation/zigux/phase2-closure.md", 160 * 1024);
    defer std.testing.allocator.free(closure_note);

    const scripts_readme = try readRepoFile("scripts/zigux/README.md", 160 * 1024);
    defer std.testing.allocator.free(scripts_readme);

    try expectContains(closure_note, "PHASE2_KCONFIG_BRIDGE_CONF_HELPER_ANCHOR_COUNT=4");
    try expectContains(closure_note, "PHASE2_KCONFIG_BRIDGE_CONFDATA_CASE_COUNT=16");
    try expectContains(closure_note, "PHASE2_KCONFIG_BRIDGE_CONFDATA_HELPER_ANCHOR_COUNT=36");
    try expectContains(closure_note, "scripts/zigux/kconfig/confdata_bridge.zig");
    try expectContains(closure_note, "scripts/zigux/check-kconfig-bridge.py");
    try expectContains(closure_note, "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json");

    try expectContains(scripts_readme, "scripts/zigux/check-phase2-kconfig-selftest-alignment.py");
    try expectContains(scripts_readme, "scripts/zigux/kconfig/conf_bridge.zig");
    try expectContains(scripts_readme, "scripts/zigux/kconfig/confdata_bridge.zig");
    try expectAbsent(closure_note, "PHASE2_KCONFIG_BRIDGE_CONFDATA_CASE_COUNT=15");
    try expectAbsent(closure_note, "PHASE2_KCONFIG_BRIDGE_CONFDATA_HELPER_ANCHOR_COUNT=28");
}

test "kconfig bridge manifests keep current 16-case request and config packets" {
    const conf_manifest = try readRepoFile("zigux/tests/fixtures/kconfig_bridge/conf_manifest.json", 64 * 1024);
    defer std.testing.allocator.free(conf_manifest);

    const confdata_manifest = try readRepoFile("zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json", 96 * 1024);
    defer std.testing.allocator.free(confdata_manifest);

    try expectContains(conf_manifest, "\"case_count\": 16");
    try expectContains(conf_manifest, "\"allconfig_sentinel_packet\"");
    try expectContains(conf_manifest, "\"allconfig_override_packet\"");
    try expectContains(conf_manifest, "\"helper_local_allconfig_explicit_override_modes\"");
    try expectContains(conf_manifest, "\"allmodconfig\"");
    try expectContains(conf_manifest, "\"alldefconfig\"");
    try expectContains(conf_manifest, "\"randconfig\"");

    try expectContains(confdata_manifest, "\"case_count\": 16");
    try expectContains(confdata_manifest, "\"explicit_empty_assignments\"");
    try expectContains(confdata_manifest, "\"confdata bridge file reader accepts config inputs beyond one mebibyte\"");
    try expectContains(confdata_manifest, "\"confdata bridge preserves duplicate unset ownership on allocation failure\"");
    try expectAbsent(confdata_manifest, "\"case_count\": 15");
}
