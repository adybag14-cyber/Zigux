const std = @import("std");

const repo_paths = struct {
    const scripts_readme = "scripts/zigux/README.md";
    const tests_readme = "zigux/tests/README.md";
    const phase2_closure = "Documentation/zigux/phase2-closure.md";
    const makefile = "zigux/Makefile";
    const check_kconfig_bridge = "scripts/zigux/check-kconfig-bridge.py";
    const check_kconfig_alignment = "scripts/zigux/check-phase2-kconfig-selftest-alignment.py";
    const check_kconfig_allconfig = "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py";
    const cases = "zigux/tests/fixtures/kconfig_bridge/cases.json";
    const conf_manifest = "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json";
    const confdata_manifest = "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json";
};

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        allocator,
        .limited(1024 * 1024),
    );
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireInOrder(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

fn requireAll(haystack: []const u8, markers: []const []const u8) !void {
    for (markers) |marker| {
        try requireContains(haystack, marker);
    }
}

fn requireAllconfigSplit(conf_manifest: []const u8) !void {
    try requireContains(conf_manifest, "\"allconfig_sentinel_packet\"");
    try requireContains(conf_manifest, "\"allnoconfig_expected.json\"");
    try requireContains(conf_manifest, "\"allyesconfig_expected.json\"");
    try requireContains(conf_manifest, "\"allconfig_override_packet\"");
    try requireContains(conf_manifest, "\"allmodconfig_expected.json\"");
    try requireContains(conf_manifest, "\"alldefconfig_expected.json\"");
    try requireContains(conf_manifest, "\"randconfig_expected.json\"");
    try requireContains(conf_manifest, "\"helper_local_allconfig_implicit_omission_modes\"");
    try requireContains(conf_manifest, "\"helper_local_allconfig_explicit_override_modes\"");
}

test "scripts root keeps the Phase 2 kconfig packet explicit" {
    const allocator = std.testing.allocator;
    const scripts_readme = try readRepoFile(allocator, repo_paths.scripts_readme);
    defer allocator.free(scripts_readme);

    const scripts_markers = [_][]const u8{
        "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
        "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
        "scripts/zigux/kconfig/conf_bridge.zig",
        "scripts/zigux/kconfig/confdata_bridge.zig",
        "zigux/tests/fixtures/kconfig_bridge/cases.json",
        "the manifest-backed kconfig fixture roster",
        "make -C zigux phase2-kconfig",
    };
    try requireAll(scripts_readme, &scripts_markers);
    try requireInOrder(
        scripts_readme,
        "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
        "the manifest-backed kconfig fixture roster",
    );
}

test "closure, tests root, and Makefile agree on the kconfig replay route" {
    const allocator = std.testing.allocator;
    const closure = try readRepoFile(allocator, repo_paths.phase2_closure);
    defer allocator.free(closure);
    const tests_readme = try readRepoFile(allocator, repo_paths.tests_readme);
    defer allocator.free(tests_readme);
    const makefile = try readRepoFile(allocator, repo_paths.makefile);
    defer allocator.free(makefile);

    const closure_markers = [_][]const u8{
        "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
        "PHASE2_KCONFIG_BRIDGE_CONF_HELPER_ANCHOR_COUNT=4",
        "scripts/zigux/kconfig/confdata_bridge.zig",
        "PHASE2_KCONFIG_BRIDGE_CONFDATA_CASE_COUNT=16",
        "PHASE2_KCONFIG_BRIDGE_CONFDATA_HELPER_ANCHOR_COUNT=36",
    };
    try requireAll(closure, &closure_markers);

    const tests_markers = [_][]const u8{
        "current shared Phase 2 kconfig route: `make -C zigux phase2-kconfig`",
        "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
        "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
        "scripts/zigux/check-kconfig-bridge.py",
        "scripts/zigux/kconfig/conf_bridge.zig",
        "scripts/zigux/kconfig/confdata_bridge.zig",
        "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
        "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
    };
    try requireAll(tests_readme, &tests_markers);

    const makefile_markers = [_][]const u8{
        "phase2-kconfig: phase2-toolchain",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --zig \"$(ZIG_REPO_ROOT)\"",
        "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/kconfig/conf_bridge.zig",
        "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/kconfig/confdata_bridge.zig",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-selftest-alignment.py --self-test",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-allconfig-helper-packet.py",
    };
    try requireAll(makefile, &makefile_markers);
}

test "kconfig manifests and checkers preserve conf and confdata packet counts" {
    const allocator = std.testing.allocator;
    const bridge_checker = try readRepoFile(allocator, repo_paths.check_kconfig_bridge);
    defer allocator.free(bridge_checker);
    const alignment_checker = try readRepoFile(allocator, repo_paths.check_kconfig_alignment);
    defer allocator.free(alignment_checker);
    const allconfig_checker = try readRepoFile(allocator, repo_paths.check_kconfig_allconfig);
    defer allocator.free(allconfig_checker);
    const cases = try readRepoFile(allocator, repo_paths.cases);
    defer allocator.free(cases);
    const conf_manifest = try readRepoFile(allocator, repo_paths.conf_manifest);
    defer allocator.free(conf_manifest);
    const confdata_manifest = try readRepoFile(allocator, repo_paths.confdata_manifest);
    defer allocator.free(confdata_manifest);

    try requireContains(bridge_checker, "REQUIRED_CONF_HELPER_ANCHORS");
    try requireContains(bridge_checker, "REQUIRED_CONFDATA_HELPER_ANCHORS");
    try requireContains(alignment_checker, "KCONFIG_BRIDGE_SURFACE_PATHS");
    try requireContains(allconfig_checker, "REQUIRED_HELPER_ANCHORS");
    try requireContains(allconfig_checker, "SELF_TEST_CASE_COUNT = 21");

    try requireContains(cases, "\"conf_cases\"");
    try requireContains(cases, "\"confdata_cases\"");
    try requireContains(cases, "\"name\": \"allmodconfig\"");
    try requireContains(cases, "\"name\": \"explicit_empty_assignments\"");

    try requireContains(conf_manifest, "\"tool\": \"scripts/zigux/kconfig/conf_bridge.zig\"");
    try requireContains(conf_manifest, "\"case_count\": 16");
    try requireContains(conf_manifest, "\"helper_local_anchors\"");
    try requireAllconfigSplit(conf_manifest);

    try requireContains(confdata_manifest, "\"tool\": \"scripts/zigux/kconfig/confdata_bridge.zig\"");
    try requireContains(confdata_manifest, "\"case_count\": 16");
    try requireContains(confdata_manifest, "\"explicit_empty_assignments\"");
    try requireContains(confdata_manifest, "\"confdata bridge parses explicit output modes\"");
    try requireContains(confdata_manifest, "\"confdata bridge preserves duplicate unset ownership on allocation failure\"");
}
