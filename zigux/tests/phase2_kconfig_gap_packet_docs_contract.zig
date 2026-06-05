const std = @import("std");
const testing = std.testing;

const FilePacket = struct {
    phase2_closure: []const u8,
    kconfig_gap_survey: []const u8,
    cases_json: []const u8,
    conf_manifest: []const u8,
    allconfig_checker: []const u8,
};

const fixture_packet = FilePacket{
    .phase2_closure =
    \\- `PHASE2_CURRENT_GAP_PACKET=Documentation/zigux/phase2-kconfig-bridge-gap-survey.md`
    \\- request-plan `allconfig` overrides stay limited to `allmodconfig`, `alldefconfig`, and `randconfig`
    \\- `allconfig_sentinel_packet` still covers `allnoconfig` and `allyesconfig`
    \\- `scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`
    \\- `PHASE2_KCONFIG_BRIDGE_CONF_HELPER_ANCHOR_COUNT=4`
    \\- `zigux/tests/fixtures/kconfig_bridge/cases.json`
    \\- `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`
    ,
    .kconfig_gap_survey =
    \\The request-plan packet in `zigux/tests/fixtures/kconfig_bridge/cases.json` and `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json` treats these modes as explicit override cases:
    \\- `allmodconfig`
    \\- `alldefconfig`
    \\- `randconfig`
    \\The manifest keeps these sentinel-backed modes separate through `allconfig_sentinel_packet`:
    \\- `allnoconfig`
    \\- `allyesconfig`
    \\The helper-local reminder packet still names the broader explicit-override guard surface through `helper_local_allconfig_explicit_override_modes`:
    \\- `allmodconfig`
    \\- `allnoconfig`
    \\- `allyesconfig`
    \\- `alldefconfig`
    \\- `randconfig`
    \\scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py
    ,
    .cases_json =
    \\{"conf_cases":[{"name":"allnoconfig","mode":"allnoconfig"},{"name":"allyesconfig","mode":"allyesconfig"},{"name":"allmodconfig","mode":"allmodconfig","allconfig":""},{"name":"alldefconfig","mode":"alldefconfig","allconfig":"mini-all.config"},{"name":"randconfig","mode":"randconfig","allconfig":"","seed":"0xC0FFEE","probability":"15:25"}]}
    ,
    .conf_manifest =
    \\{"allconfig_sentinel_packet":["allnoconfig_expected.json","allyesconfig_expected.json"],"allconfig_override_packet":["allmodconfig_expected.json","alldefconfig_expected.json","randconfig_expected.json"],"helper_local_allconfig_implicit_omission_modes":["allmodconfig","randconfig"],"helper_local_allconfig_explicit_override_modes":["allmodconfig","allnoconfig","allyesconfig","alldefconfig","randconfig"],"helper_local_anchors":["conf bridge emits explicit empty allconfig override for allmodconfig","conf bridge emits randconfig tunables when present","conf bridge emits explicit randconfig allconfig override when present","conf bridge omits randconfig allconfig sentinel without explicit override"]}
    ,
    .allconfig_checker =
    \\REQUIRED_HELPER_ANCHORS = [
    \\    "conf bridge emits explicit empty allconfig override for allmodconfig",
    \\    "conf bridge emits randconfig tunables when present",
    \\    "conf bridge emits explicit randconfig allconfig override when present",
    \\    "conf bridge omits randconfig allconfig sentinel without explicit override",
    \\]
    \\REQUIRED_CLOSURE_MARKERS = [
    \\    "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    \\    "PHASE2_KCONFIG_BRIDGE_CONF_HELPER_ANCHOR_COUNT=4",
    \\]
    \\SELF_TEST_CASE_COUNT = 21
    ,
};

const required_closure_markers = [_][]const u8{
    "PHASE2_CURRENT_GAP_PACKET=Documentation/zigux/phase2-kconfig-bridge-gap-survey.md",
    "request-plan `allconfig` overrides stay limited to `allmodconfig`, `alldefconfig`, and `randconfig`",
    "`allconfig_sentinel_packet` still covers `allnoconfig` and `allyesconfig`",
    "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    "PHASE2_KCONFIG_BRIDGE_CONF_HELPER_ANCHOR_COUNT=4",
};

const required_gap_survey_markers = [_][]const u8{
    "zigux/tests/fixtures/kconfig_bridge/cases.json",
    "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
    "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    "allconfig_sentinel_packet",
    "helper_local_allconfig_explicit_override_modes",
};

const request_plan_override_modes = [_][]const u8{
    "allmodconfig",
    "alldefconfig",
    "randconfig",
};

const sentinel_modes = [_][]const u8{
    "allnoconfig",
    "allyesconfig",
};

const explicit_override_modes = [_][]const u8{
    "allmodconfig",
    "allnoconfig",
    "allyesconfig",
    "alldefconfig",
    "randconfig",
};

const helper_anchors = [_][]const u8{
    "conf bridge emits explicit empty allconfig override for allmodconfig",
    "conf bridge emits randconfig tunables when present",
    "conf bridge emits explicit randconfig allconfig override when present",
    "conf bridge omits randconfig allconfig sentinel without explicit override",
};

fn containsAll(haystack: []const u8, markers: []const []const u8) bool {
    for (markers) |marker| {
        if (std.mem.indexOf(u8, haystack, marker) == null) return false;
    }
    return true;
}

fn expectContainsAll(haystack: []const u8, markers: []const []const u8) !void {
    for (markers) |marker| {
        try testing.expect(std.mem.indexOf(u8, haystack, marker) != null);
    }
}

fn quoted(name: []const u8) []const u8 {
    return name;
}

fn expectJsonStringArray(json_text: []const u8, field: []const u8, values: []const []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, json_text, field) != null);
    for (values) |value| {
        try testing.expect(std.mem.indexOf(u8, json_text, quoted(value)) != null);
    }
}

fn validatePacket(packet: FilePacket) !void {
    try expectContainsAll(packet.phase2_closure, &required_closure_markers);
    try expectContainsAll(packet.kconfig_gap_survey, &required_gap_survey_markers);

    try expectContainsAll(packet.kconfig_gap_survey, &request_plan_override_modes);
    try expectContainsAll(packet.kconfig_gap_survey, &sentinel_modes);
    try expectContainsAll(packet.kconfig_gap_survey, &explicit_override_modes);

    try expectJsonStringArray(packet.cases_json, "\"conf_cases\"", &request_plan_override_modes);
    try expectJsonStringArray(packet.cases_json, "\"conf_cases\"", &sentinel_modes);

    try expectJsonStringArray(packet.conf_manifest, "\"allconfig_override_packet\"", &.{
        "allmodconfig_expected.json",
        "alldefconfig_expected.json",
        "randconfig_expected.json",
    });
    try expectJsonStringArray(packet.conf_manifest, "\"allconfig_sentinel_packet\"", &.{
        "allnoconfig_expected.json",
        "allyesconfig_expected.json",
    });
    try expectJsonStringArray(packet.conf_manifest, "\"helper_local_allconfig_explicit_override_modes\"", &explicit_override_modes);
    try expectJsonStringArray(packet.conf_manifest, "\"helper_local_allconfig_implicit_omission_modes\"", &.{
        "allmodconfig",
        "randconfig",
    });

    try expectContainsAll(packet.conf_manifest, &helper_anchors);
    try expectContainsAll(packet.allconfig_checker, &helper_anchors);
    try expectContainsAll(packet.allconfig_checker, &.{
        "REQUIRED_CLOSURE_MARKERS",
        "PHASE2_KCONFIG_BRIDGE_CONF_HELPER_ANCHOR_COUNT=4",
        "SELF_TEST_CASE_COUNT = 21",
    });
}

test "fixture packet preserves current kconfig gap reconciliation shape" {
    try validatePacket(fixture_packet);
}

test "closure and survey both name the allconfig split owners" {
    try expectContainsAll(fixture_packet.phase2_closure, &.{
        "Documentation/zigux/phase2-kconfig-bridge-gap-survey.md",
        "zigux/tests/fixtures/kconfig_bridge/cases.json",
        "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
    });
    try expectContainsAll(fixture_packet.kconfig_gap_survey, &.{
        "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
        "helper_local_allconfig_explicit_override_modes",
    });
}

test "contract rejects collapsed request-plan and sentinel allconfig packets" {
    const broken = FilePacket{
        .phase2_closure = fixture_packet.phase2_closure,
        .kconfig_gap_survey = fixture_packet.kconfig_gap_survey,
        .cases_json = fixture_packet.cases_json,
        .conf_manifest = "{\"allconfig_override_packet\":[\"allmodconfig_expected.json\",\"alldefconfig_expected.json\",\"randconfig_expected.json\",\"allnoconfig_expected.json\",\"allyesconfig_expected.json\"]}",
        .allconfig_checker = fixture_packet.allconfig_checker,
    };

    try testing.expectError(error.TestUnexpectedResult, validatePacket(broken));
}
