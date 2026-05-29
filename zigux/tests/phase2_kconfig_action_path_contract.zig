const std = @import("std");

const workflow_markers = [_][]const u8{
    "Self-test current kconfig bridge checker",
    "run: python3 scripts/zigux/check-kconfig-bridge.py --self-test",
    "Check current kconfig bridge packet",
    "run: python3 scripts/zigux/check-kconfig-bridge.py",
    "Run current Phase 2 conf bridge unit tests",
    "run: zig test scripts/zigux/kconfig/conf_bridge.zig",
    "Run current Phase 2 confdata bridge unit tests",
    "run: zig test scripts/zigux/kconfig/confdata_bridge.zig",
    "Self-test current Phase 2 kconfig bridge checker",
    "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
    "Check current Phase 2 kconfig bridge packet",
    "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "Self-test current Phase 2 kconfig allconfig helper checker",
    "run: python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py --self-test",
    "Check current Phase 2 kconfig allconfig helper packet",
    "run: python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    "Run current Phase 2 kconfig make route",
    "run: make -C zigux phase2-kconfig",
};

const makefile_markers = [_][]const u8{
    "phase2-kconfig: phase2-toolchain",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/conf_bridge.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-selftest-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-selftest-alignment.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-allconfig-helper-packet.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-allconfig-helper-packet.py",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
};

const checker_markers = [_][]const u8{
    "ARTIFACT_DIFF = ROOT / \"scripts\" / \"zigux\" / \"artifact_diff.py\"",
    "CONF_BRIDGE = ROOT / \"scripts\" / \"zigux\" / \"kconfig\" / \"conf_bridge.zig\"",
    "CONFDATA_BRIDGE = ROOT / \"scripts\" / \"zigux\" / \"kconfig\" / \"confdata_bridge.zig\"",
    "FIXTURE_DIR = ROOT / \"zigux\" / \"tests\" / \"fixtures\" / \"kconfig_bridge\"",
    "REQUIRED_CONF_HELPER_ANCHORS = [",
    "REQUIRED_CONFDATA_HELPER_ANCHORS = [",
    "conf bridge mode surface stays aligned with conf.c long options",
    "conf bridge emits olddefconfig argv and env",
    "conf bridge emits syncconfig auto files",
    "confdata bridge parses bounded config states",
    "confdata bridge emits bounded json output",
    "confdata bridge parses explicit output modes",
    "EXPECTED_SELF_TEST_CASE_COUNT = 6",
};

const manifest_markers = [_][]const u8{
    "the live kconfig bridge checker and fixture roster",
    "the helper-local kconfig allconfig guard",
    "scripts/zigux/check-kconfig-bridge.py",
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
    "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
    "make -C zigux phase2-kconfig",
    "repo_reality_gaps\": []",
    "status\": \"active\"",
};

const ordered_kconfig_workflow_steps = [_][]const u8{
    "Self-test current kconfig bridge checker",
    "Check current kconfig bridge packet",
    "Run current Phase 2 conf bridge unit tests",
    "Run current Phase 2 confdata bridge unit tests",
    "Self-test current Phase 2 kconfig bridge checker",
    "Check current Phase 2 kconfig bridge packet",
    "Self-test current Phase 2 kconfig allconfig helper checker",
    "Check current Phase 2 kconfig allconfig helper packet",
    "Run current Phase 2 kconfig make route",
};

const ordered_kconfig_make_steps = [_][]const u8{
    "phase2-kconfig: phase2-toolchain",
    "check-kconfig-bridge.py --self-test",
    "check-kconfig-bridge.py",
    "$(ZIG) test scripts/zigux/kconfig/conf_bridge.zig",
    "$(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig",
    "check-phase2-kconfig-selftest-alignment.py --self-test",
    "check-phase2-kconfig-selftest-alignment.py",
    "check-phase2-kconfig-allconfig-helper-packet.py --self-test",
    "check-phase2-kconfig-allconfig-helper-packet.py",
};

fn expectContainsAll(haystack: []const u8, needles: []const []const u8) !void {
    for (needles) |needle| {
        try std.testing.expect(std.mem.containsAtLeast(u8, haystack, 1, needle));
    }
}

fn expectOrdered(haystack: []const u8, needles: []const []const u8) !void {
    var offset: usize = 0;
    for (needles) |needle| {
        const found = std.mem.indexOf(u8, haystack[offset..], needle) orelse return error.MarkerOutOfOrder;
        offset += found + needle.len;
    }
}

test "Phase 2 workflow keeps the kconfig action path ordered" {
    const workflow_excerpt =
        \\\      - name: Self-test current kconfig bridge checker
        \\\        run: python3 scripts/zigux/check-kconfig-bridge.py --self-test
        \\\
        \\\      - name: Check current kconfig bridge packet
        \\\        run: python3 scripts/zigux/check-kconfig-bridge.py
        \\\
        \\\      - name: Run current Phase 2 conf bridge unit tests
        \\\        run: zig test scripts/zigux/kconfig/conf_bridge.zig
        \\\
        \\\      - name: Run current Phase 2 confdata bridge unit tests
        \\\        run: zig test scripts/zigux/kconfig/confdata_bridge.zig
        \\\
        \\\      - name: Self-test current Phase 2 kconfig bridge checker
        \\\        run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test
        \\\
        \\\      - name: Check current Phase 2 kconfig bridge packet
        \\\        run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py
        \\\
        \\\      - name: Self-test current Phase 2 kconfig allconfig helper checker
        \\\        run: python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py --self-test
        \\\
        \\\      - name: Check current Phase 2 kconfig allconfig helper packet
        \\\        run: python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py
        \\\
        \\\      - name: Run current Phase 2 kconfig make route
        \\\        run: make -C zigux phase2-kconfig
    ;

    try expectContainsAll(workflow_excerpt, &workflow_markers);
    try expectOrdered(workflow_excerpt, &ordered_kconfig_workflow_steps);
}

test "Phase 2 Makefile keeps the kconfig route complete" {
    const makefile_excerpt =
        \\\phase2-kconfig: phase2-toolchain
        \\\    cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --self-test
        \\\    cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py
        \\\    cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/conf_bridge.zig
        \\\    cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig
        \\\    $(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-selftest-alignment.py --self-test
        \\\    $(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-selftest-alignment.py
        \\\    $(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-allconfig-helper-packet.py --self-test
        \\\    $(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-allconfig-helper-packet.py
        \\\
        \\\phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep
    ;

    try expectContainsAll(makefile_excerpt, &makefile_markers);
    try expectOrdered(makefile_excerpt, &ordered_kconfig_make_steps);
}

test "kconfig bridge checker still describes both bridge helper packets" {
    const checker_excerpt =
        \\\ARTIFACT_DIFF = ROOT / "scripts" / "zigux" / "artifact_diff.py"
        \\\CONF_BRIDGE = ROOT / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig"
        \\\CONFDATA_BRIDGE = ROOT / "scripts" / "zigux" / "kconfig" / "confdata_bridge.zig"
        \\\FIXTURE_DIR = ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge"
        \\\REQUIRED_CONF_HELPER_ANCHORS = [
        \\\conf bridge mode surface stays aligned with conf.c long options
        \\\conf bridge emits olddefconfig argv and env
        \\\conf bridge emits syncconfig auto files
        \\\REQUIRED_CONFDATA_HELPER_ANCHORS = [
        \\\confdata bridge parses bounded config states
        \\\confdata bridge emits bounded json output
        \\\confdata bridge parses explicit output modes
        \\\EXPECTED_SELF_TEST_CASE_COUNT = 6
    ;

    try expectContainsAll(checker_excerpt, &checker_markers);
}

test "Phase 2 tool manifest keeps kconfig packet visible" {
    const manifest_excerpt =
        \\\the live kconfig bridge checker and fixture roster
        \\\the helper-local kconfig allconfig guard
        \\\scripts/zigux/check-kconfig-bridge.py
        \\\scripts/zigux/check-phase2-kconfig-selftest-alignment.py
        \\\scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py
        \\\scripts/zigux/kconfig/conf_bridge.zig
        \\\scripts/zigux/kconfig/confdata_bridge.zig
        \\\zigux/tests/fixtures/kconfig_bridge/conf_manifest.json
        \\\zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json
        \\\make -C zigux phase2-kconfig
        \\\repo_reality_gaps": []
        \\\status": "active"
    ;

    try expectContainsAll(manifest_excerpt, &manifest_markers);
}
