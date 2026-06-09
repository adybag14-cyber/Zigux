const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

fn countExactLines(haystack: []const u8, marker: []const u8) usize {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, std.mem.trim(u8, line, " \t\r"), marker)) {
            count += 1;
        }
    }
    return count;
}

fn expectSingleLine(haystack: []const u8, marker: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countExactLines(haystack, marker));
}

test "phase 2 closure manifest names the kconfig allconfig helper packet" {
    const closure_note = try readRepoFile("Documentation/zigux/phase2-closure.md", 128 * 1024);
    defer std.testing.allocator.free(closure_note);

    const tool_manifest = try readRepoFile("zigux/tests/fixtures/phase2_tool_manifest.json", 256 * 1024);
    defer std.testing.allocator.free(tool_manifest);

    try expectContains(closure_note, "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py");
    try expectContains(closure_note, "PHASE2_KCONFIG_BRIDGE_CONF_HELPER_ANCHOR_COUNT=4");
    try expectContains(closure_note, "Documentation/zigux/phase2-conf-bridge-survey.md");
    try expectContains(closure_note, "PHASE2_CURRENT_GAP_PACKET=Documentation/zigux/phase2-kconfig-bridge-gap-survey.md");
    try expectContains(
        closure_note,
        "PHASE2_SHARED_TOOLING_CHECKERS=python3 scripts/zigux/check-phase2-tool-manifest.py,python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py,python3 scripts/zigux/check-phase2-artifact-tools-manifest.py,python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py,python3 scripts/zigux/check-phase2-cross.py,python3 scripts/zigux/check-phase2-fixdep-gate.py,python3 scripts/zigux/check-fixdep-diff.py",
    );

    try expectContains(tool_manifest, "\"scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py\"");
    try expectContains(tool_manifest, "\"scripts/zigux/kconfig/conf_bridge.zig\"");
    try expectContains(tool_manifest, "\"zigux/tests/fixtures/kconfig_bridge/conf_manifest.json\"");
    try expectContains(tool_manifest, "Keep the dedicated manifest guards, the bootstrap workflow-routes guard, the primary artifact_diff helper, the helper-local kconfig allconfig guard");
}

test "kconfig conf manifest and checker agree on allconfig helper mode packets" {
    const conf_manifest = try readRepoFile("zigux/tests/fixtures/kconfig_bridge/conf_manifest.json", 96 * 1024);
    defer std.testing.allocator.free(conf_manifest);

    const allconfig_checker = try readRepoFile("scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py", 192 * 1024);
    defer std.testing.allocator.free(allconfig_checker);

    try expectContains(conf_manifest, "\"helper_local_allconfig_implicit_omission_modes\": [");
    try expectContains(conf_manifest, "\"allmodconfig\"");
    try expectContains(conf_manifest, "\"randconfig\"");
    try expectContains(conf_manifest, "\"helper_local_allconfig_explicit_override_modes\": [");
    try expectContains(conf_manifest, "\"allnoconfig\"");
    try expectContains(conf_manifest, "\"allyesconfig\"");
    try expectContains(conf_manifest, "\"alldefconfig\"");

    try expectContains(allconfig_checker, "REQUIRED_CONF_HELPER_LOCAL_ALLCONFIG_IMPLICIT_OMISSION_MODES");
    try expectContains(allconfig_checker, "REQUIRED_CONF_HELPER_LOCAL_ALLCONFIG_EXPLICIT_OVERRIDE_MODES");
    try expectContains(allconfig_checker, "SELF_TEST_IMPLICIT_MODES = [\"allmodconfig\", \"randconfig\"]");
    try expectContains(allconfig_checker, "SELF_TEST_EXPLICIT_MODES = [\"allmodconfig\", \"allnoconfig\", \"allyesconfig\", \"alldefconfig\", \"randconfig\"]");
    try expectContains(allconfig_checker, "PHASE2_KCONFIG_ALLCONFIG_HELPER_PACKET_SELF_TEST_CASE_COUNT");
}

test "conf bridge keeps helper-local allconfig behavior anchored in Zig tests" {
    const conf_bridge = try readRepoFile("scripts/zigux/kconfig/conf_bridge.zig", 256 * 1024);
    defer std.testing.allocator.free(conf_bridge);

    const bridge_checker = try readRepoFile("scripts/zigux/check-kconfig-bridge.py", 256 * 1024);
    defer std.testing.allocator.free(bridge_checker);

    try expectContains(conf_bridge, "conf bridge emits explicit empty allconfig override for allmodconfig");
    try expectContains(conf_bridge, "conf bridge emits randconfig tunables when present");
    try expectContains(conf_bridge, "conf bridge emits explicit randconfig allconfig override when present");
    try expectContains(conf_bridge, "conf bridge omits randconfig allconfig sentinel without explicit override");
    try expectContains(conf_bridge, "var alldefconfig_path_capture = try TestCapture.init(std.testing.allocator, 224);");
    try expectContains(conf_bridge, ".allconfig = \"mini-all.config\",");
    try expectContains(conf_bridge, "allconfig_fallbacks");
    try expectContains(conf_bridge, "allrandom.config");
    try expectContains(conf_bridge, "all.config");

    try expectContains(bridge_checker, "REQUIRED_CONF_HELPER_ANCHORS");
    try expectContains(bridge_checker, "REQUIRED_CONF_HELPER_LOCAL_ALLCONFIG_IMPLICIT_OMISSION_MODES");
    try expectContains(bridge_checker, "REQUIRED_CONF_HELPER_LOCAL_ALLCONFIG_EXPLICIT_OVERRIDE_MODES");
}

test "makefile and workflow run allconfig helper checks after the base kconfig bridge" {
    const makefile = try readRepoFile("zigux/Makefile", 128 * 1024);
    defer std.testing.allocator.free(makefile);

    const workflow = try readRepoFile(".github/workflows/zigux-bootstrap.yml", 512 * 1024);
    defer std.testing.allocator.free(workflow);

    const bridge_make_check = "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --zig \"$(ZIG_REPO_ROOT)\"";
    const helper_make_self_test = "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-allconfig-helper-packet.py --self-test";
    const helper_make_live = "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-allconfig-helper-packet.py";
    const bridge_workflow_check = "run: python3 scripts/zigux/check-kconfig-bridge.py";
    const helper_workflow_self_test = "run: python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py --self-test";
    const helper_workflow_live = "run: python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py";

    try expectContains(makefile, "phase2-kconfig: phase2-toolchain");
    try expectSingleLine(makefile, helper_make_self_test);
    try expectSingleLine(makefile, helper_make_live);
    try expectBefore(makefile, bridge_make_check, helper_make_self_test);
    try expectBefore(
        makefile,
        "\n\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-allconfig-helper-packet.py --self-test\n",
        "\n\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-allconfig-helper-packet.py\n",
    );

    try expectSingleLine(workflow, helper_workflow_self_test);
    try expectSingleLine(workflow, helper_workflow_live);
    try expectBefore(workflow, bridge_workflow_check, helper_workflow_self_test);
    try expectBefore(
        workflow,
        "\n        run: python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py --self-test\n",
        "\n        run: python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py\n",
    );
}
