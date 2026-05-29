const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase 2 closure note keeps the kconfig allconfig split explicit" {
    const closure_note = try readRepoFile("Documentation/zigux/phase2-closure.md", 64 * 1024);
    defer std.testing.allocator.free(closure_note);

    try expectContains(closure_note, "zigux/tests/fixtures/kconfig_bridge/cases.json");
    try expectContains(closure_note, "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json");
    try expectContains(closure_note, "request-plan `allconfig` overrides stay limited to `allmodconfig`, `alldefconfig`, and `randconfig`");
    try expectContains(closure_note, "`allconfig_sentinel_packet` still covers `allnoconfig` and `allyesconfig`");
    try expectContains(closure_note, "helper-local explicit-override roster remains broader by design");
    try expectContains(closure_note, "explicit `allconfig` overrides");
    try expectContains(closure_note, "`defconfig` and `savedefconfig` mode-argument packet");
    try expectContains(closure_note, "rewrite-mode trio (`yes2modconfig`, `mod2yesconfig`, `mod2noconfig`)");
}

test "phase 2 bootstrap note mirrors the current kconfig manifest evidence" {
    const bootstrap_note = try readRepoFile("Documentation/zigux/phase2-toolchain-bootstrap-notes.md", 128 * 1024);
    defer std.testing.allocator.free(bootstrap_note);

    try expectContains(bootstrap_note, "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json");
    try expectContains(bootstrap_note, "full sixteen-mode `conf_bridge` packet");
    try expectContains(bootstrap_note, "explicit empty `allmodconfig` `allconfig` override packet");
    try expectContains(bootstrap_note, "`randconfig` override packet");
    try expectContains(bootstrap_note, "dedicated `randconfig_env_packet`");
    try expectContains(bootstrap_note, "manifest-backed bridge evidence instead of the older narrower override story");
    try expectContains(bootstrap_note, "make -C zigux phase2-kconfig");
    try expectContains(bootstrap_note, "kconfig bridge alignment");
}

test "phase 2 conf manifest still records the allconfig packet boundaries" {
    const conf_manifest = try readRepoFile("zigux/tests/fixtures/kconfig_bridge/conf_manifest.json", 32 * 1024);
    defer std.testing.allocator.free(conf_manifest);

    try expectContains(conf_manifest, "\"case_count\": 16");
    try expectContains(conf_manifest, "\"allconfig_sentinel_packet\"");
    try expectContains(conf_manifest, "\"allnoconfig_expected.json\"");
    try expectContains(conf_manifest, "\"allyesconfig_expected.json\"");
    try expectContains(conf_manifest, "\"allconfig_override_packet\"");
    try expectContains(conf_manifest, "\"allmodconfig_expected.json\"");
    try expectContains(conf_manifest, "\"alldefconfig_expected.json\"");
    try expectContains(conf_manifest, "\"randconfig_expected.json\"");
    try expectContains(conf_manifest, "\"helper_local_allconfig_implicit_omission_modes\"");
    try expectContains(conf_manifest, "\"helper_local_allconfig_explicit_override_modes\"");
    try expectContains(conf_manifest, "\"randconfig_env_packet\"");
    try expectContains(conf_manifest, "conf bridge emits explicit empty allconfig override for allmodconfig");
    try expectContains(conf_manifest, "bridge options parser accepts explicit allconfig override for allmodconfig");
}
