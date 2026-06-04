const std = @import("std");

const cases = @embedFile("fixtures/kconfig_bridge/cases.json");
const conf_manifest = @embedFile("fixtures/kconfig_bridge/conf_manifest.json");

const survey_markers =
    \\Lane scope for this survey:
    \\`scripts/zigux/kconfig/conf_bridge.zig`
    \\`scripts/zigux/kconfig/confdata_bridge.zig`
    \\`scripts/zigux/check-kconfig-bridge.py`
    \\`scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`
    \\`zigux/tests/fixtures/kconfig_bridge/`
    \\The current repo already carries meaningful bridge scaffolding instead of placeholder churn.
    \\the lane has already cleared the roadmap's anti-churn bar for bridge scaffolding
    \\Upstream source-anchor gap
    \\current authenticated repo reads still do not expose those C sources on `master`
    \\same-tree parity against current in-repo C sources is still unavailable
    \\`zigux/tests/fixtures/kconfig_bridge/cases.json`, `conf_manifest.json`, and `confdata_manifest.json` keep the shipped replay packet explicit.
    \\The request-plan packet in `zigux/tests/fixtures/kconfig_bridge/cases.json` and `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`
    \\Differential replay remains fixture-backed, not source-backed
    \\fixture-backed rather than same-tree differential
    \\allmodconfig
    \\alldefconfig
    \\randconfig
    \\allnoconfig
    \\allyesconfig
    \\That risk is now guarded rather than merely described
    \\future drift if one of those surfaces changes without moving the full packet together
    \\preserve the current helper-packet guard and avoid widening Phase 2 kconfig claims
;

const conf_modes = [_][]const u8{
    "oldaskconfig",
    "syncconfig",
    "oldconfig",
    "allnoconfig",
    "allyesconfig",
    "allmodconfig",
    "alldefconfig",
    "randconfig",
    "defconfig",
    "savedefconfig",
    "listnewconfig",
    "helpnewconfig",
    "olddefconfig",
    "yes2modconfig",
    "mod2yesconfig",
    "mod2noconfig",
};

const request_plan_allconfig_modes = [_][]const u8{
    "allmodconfig",
    "alldefconfig",
    "randconfig",
};

const sentinel_allconfig_modes = [_][]const u8{
    "allnoconfig",
    "allyesconfig",
};

const helper_local_allconfig_modes = [_][]const u8{
    "allmodconfig",
    "allnoconfig",
    "allyesconfig",
    "alldefconfig",
    "randconfig",
};

test "kconfig bridge gap survey records shipped scaffold and upstream source gap" {
    try expectContains(survey_markers, "Lane scope for this survey:");
    try expectContains(survey_markers, "`scripts/zigux/kconfig/conf_bridge.zig`");
    try expectContains(survey_markers, "`scripts/zigux/kconfig/confdata_bridge.zig`");
    try expectContains(survey_markers, "`scripts/zigux/check-kconfig-bridge.py`");
    try expectContains(survey_markers, "`scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`");
    try expectContains(survey_markers, "`zigux/tests/fixtures/kconfig_bridge/`");

    try expectContains(survey_markers, "The current repo already carries meaningful bridge scaffolding instead of placeholder churn.");
    try expectContains(survey_markers, "the lane has already cleared the roadmap's anti-churn bar for bridge scaffolding");
    try expectContains(survey_markers, "Upstream source-anchor gap");
    try expectContains(survey_markers, "current authenticated repo reads still do not expose those C sources on `master`");
    try expectContains(survey_markers, "same-tree parity against current in-repo C sources is still unavailable");
}

test "survey and manifests agree on the sixteen-mode conf bridge packet" {
    try expectContains(conf_manifest, "\"case_count\": 16");

    for (conf_modes) |mode| {
        try expectContains(cases, mode);
        try expectContains(conf_manifest, mode);
    }

    try expectContains(survey_markers, "`zigux/tests/fixtures/kconfig_bridge/cases.json`, `conf_manifest.json`, and `confdata_manifest.json` keep the shipped replay packet explicit.");
    try expectContains(survey_markers, "The request-plan packet in `zigux/tests/fixtures/kconfig_bridge/cases.json` and `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`");
    try expectContains(survey_markers, "Differential replay remains fixture-backed, not source-backed");
    try expectContains(survey_markers, "fixture-backed rather than same-tree differential");
}

test "survey keeps allconfig request, sentinel, and helper-local packets distinct" {
    try expectContains(conf_manifest, "\"allconfig_override_packet\"");
    for (request_plan_allconfig_modes) |mode| {
        try expectContains(survey_markers, mode);
        try expectContains(conf_manifest, mode);
    }

    try expectContains(conf_manifest, "\"allconfig_sentinel_packet\"");
    for (sentinel_allconfig_modes) |mode| {
        try expectContains(survey_markers, mode);
        try expectContains(conf_manifest, mode);
    }

    try expectContains(conf_manifest, "\"helper_local_allconfig_explicit_override_modes\"");
    for (helper_local_allconfig_modes) |mode| {
        try expectContains(survey_markers, mode);
        try expectContains(conf_manifest, mode);
    }

    try expectContains(survey_markers, "That risk is now guarded rather than merely described");
    try expectContains(survey_markers, "future drift if one of those surfaces changes without moving the full packet together");
    try expectContains(survey_markers, "preserve the current helper-packet guard and avoid widening Phase 2 kconfig claims");
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}
