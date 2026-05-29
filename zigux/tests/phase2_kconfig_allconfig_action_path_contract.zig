const std = @import("std");

const helper_checker_markers = [_][]const u8{
    "CONF_MANIFEST = ROOT / \"zigux\" / \"tests\" / \"fixtures\" / \"kconfig_bridge\" / \"conf_manifest.json\"",
    "CONF_BRIDGE = ROOT / \"scripts\" / \"zigux\" / \"kconfig\" / \"conf_bridge.zig\"",
    "KCONFIG_BRIDGE_CHECKER = ROOT / \"scripts\" / \"zigux\" / \"check-kconfig-bridge.py\"",
    "PHASE2_VALIDATE = ROOT / \"scripts\" / \"zigux\" / \"validate-phase2.py\"",
    "PHASE2_CLOSURE_VALIDATE = ROOT / \"scripts\" / \"zigux\" / \"validate-phase2-closure.py\"",
    "PHASE2_TOOL_MANIFEST = ROOT / \"zigux\" / \"tests\" / \"fixtures\" / \"phase2_tool_manifest.json\"",
    "conf bridge emits explicit empty allconfig override for allmodconfig",
    "conf bridge emits randconfig tunables when present",
    "conf bridge emits explicit randconfig allconfig override when present",
    "conf bridge omits randconfig allconfig sentinel without explicit override",
    "run: python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py --self-test",
    "run: python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-allconfig-helper-packet.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-allconfig-helper-packet.py",
    "SELF_TEST_CASE_COUNT = 17",
};

const conf_manifest_snippet =
    \\\{
    \\\  "tool": "scripts/zigux/kconfig/conf_bridge.zig",
    \\\  "status": "closed",
    \\\  "mode": "bounded request-plan bridge",
    \\\  "case_count": 16,
    \\\  "allconfig_sentinel_packet": [
    \\\    "allnoconfig_expected.json",
    \\\    "allyesconfig_expected.json"
    \\\  ],
    \\\  "allconfig_override_packet": [
    \\\    "allmodconfig_expected.json",
    \\\    "alldefconfig_expected.json",
    \\\    "randconfig_expected.json"
    \\\  ],
    \\\  "helper_local_allconfig_implicit_omission_modes": [
    \\\    "allmodconfig",
    \\\    "randconfig"
    \\\  ],
    \\\  "helper_local_allconfig_explicit_override_modes": [
    \\\    "allmodconfig",
    \\\    "allnoconfig",
    \\\    "allyesconfig",
    \\\    "alldefconfig",
    \\\    "randconfig"
    \\\  ],
    \\\  "helper_local_anchors": [
    \\\    "conf bridge emits explicit empty allconfig override for allmodconfig",
    \\\    "conf bridge emits randconfig tunables when present",
    \\\    "conf bridge emits explicit randconfig allconfig override when present",
    \\\    "conf bridge omits randconfig allconfig sentinel without explicit override"
    \\\  ]
    \\\}
;

const tool_manifest_markers = [_][]const u8{
    "the helper-local kconfig allconfig guard",
    "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/check-phase2-kbuild-routes.py",
    "scripts/zigux/check-phase2-tool-manifest.py",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
    "make -C zigux phase2-kconfig",
    "repo_reality_gaps\": []",
    "status\": \"active\"",
};

const ordered_conf_modes = [_][]const u8{
    "helper_local_allconfig_implicit_omission_modes",
    "allmodconfig",
    "randconfig",
    "helper_local_allconfig_explicit_override_modes",
    "allmodconfig",
    "allnoconfig",
    "allyesconfig",
    "alldefconfig",
    "randconfig",
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

test "kconfig allconfig helper checker keeps Phase 2 action path explicit" {
    const checker_excerpt =
        \\\CONF_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "conf_manifest.json"
        \\\CONF_BRIDGE = ROOT / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig"
        \\\KCONFIG_BRIDGE_CHECKER = ROOT / "scripts" / "zigux" / "check-kconfig-bridge.py"
        \\\PHASE2_VALIDATE = ROOT / "scripts" / "zigux" / "validate-phase2.py"
        \\\PHASE2_CLOSURE_VALIDATE = ROOT / "scripts" / "zigux" / "validate-phase2-closure.py"
        \\\PHASE2_TOOL_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"
        \\\conf bridge emits explicit empty allconfig override for allmodconfig
        \\\conf bridge emits randconfig tunables when present
        \\\conf bridge emits explicit randconfig allconfig override when present
        \\\conf bridge omits randconfig allconfig sentinel without explicit override
        \\\run: python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py --self-test
        \\\run: python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py
        \\\$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-allconfig-helper-packet.py --self-test
        \\\$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-allconfig-helper-packet.py
        \\\SELF_TEST_CASE_COUNT = 17
    ;

    try expectContainsAll(checker_excerpt, &helper_checker_markers);
}

test "kconfig conf manifest preserves helper-local allconfig mode split" {
    try expectContainsAll(conf_manifest_snippet, &.{
        "\"case_count\": 16",
        "\"allconfig_sentinel_packet\"",
        "\"allconfig_override_packet\"",
        "\"allnoconfig_expected.json\"",
        "\"allyesconfig_expected.json\"",
        "\"allmodconfig_expected.json\"",
        "\"alldefconfig_expected.json\"",
        "\"randconfig_expected.json\"",
        "\"helper_local_allconfig_implicit_omission_modes\"",
        "\"helper_local_allconfig_explicit_override_modes\"",
    });
    try expectOrdered(conf_manifest_snippet, &ordered_conf_modes);
}

test "Phase 2 tool manifest names the helper-local allconfig packet" {
    const tool_manifest_excerpt =
        \\\Keep the dedicated manifest guards, the bootstrap workflow-routes guard, the primary artifact_diff helper, the helper-local kconfig allconfig guard, and the dedicated genksyms selftest-alignment guard explicit through scripts/zigux/check-phase2-tool-manifest.py, scripts/zigux/check-phase2-bootstrap-workflow-routes.py, scripts/zigux/check-phase2-artifact-tools-manifest.py, scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py, scripts/zigux/artifact_diff.py, and scripts/zigux/check-phase2-genksyms-selftest-alignment.py so Phase 2 packet drift fails closed beside the other reminder checkers.
        \\\scripts/zigux/check-phase2-kconfig-selftest-alignment.py
        \\\scripts/zigux/check-phase2-kbuild-routes.py
        \\\scripts/zigux/kconfig/conf_bridge.zig
        \\\zigux/tests/fixtures/kconfig_bridge/conf_manifest.json
        \\\make -C zigux phase2-kconfig
        \\\repo_reality_gaps": []
        \\\status": "active"
    ;

    try expectContainsAll(tool_manifest_excerpt, &tool_manifest_markers);
}
