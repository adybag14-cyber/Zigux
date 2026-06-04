const std = @import("std");

const conf_manifest = @embedFile("fixtures/kconfig_bridge/conf_manifest.json");

const closure_markers =
    \\`PHASE2_CURRENT_GAP_PACKET=Documentation/zigux/phase2-kconfig-bridge-gap-survey.md`
    \\current authenticated repo reads do not expose `scripts/kconfig/conf.c` or `scripts/kconfig/confdata.c` on `master`
    \\the shipped kconfig bridge packet remains fixture-backed rather than same-tree differential
    \\the next same-family truthfulness pass should keep reminder surfaces aligned with the live split recorded in `zigux/tests/fixtures/kconfig_bridge/cases.json` and `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`
    \\request-plan `allconfig` overrides stay limited to `allmodconfig`, `alldefconfig`, and `randconfig`
    \\`allconfig_sentinel_packet` still covers `allnoconfig` and `allyesconfig`
    \\the helper-local explicit-override roster remains broader by design
    \\add a direct `conf.c` / `confdata.c` provenance anchor once those C sources are readable in-tree again on current `master`
;

const survey_markers =
    \\The live fixture packet and manifest split the `allconfig` story across two explicit surfaces.
    \\The request-plan packet in `zigux/tests/fixtures/kconfig_bridge/cases.json` and `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`
    \\treats these modes as explicit override cases:
    \\The manifest keeps these sentinel-backed modes separate through `allconfig_sentinel_packet`:
    \\The helper-local reminder packet still names the broader explicit-override guard surface through `helper_local_allconfig_explicit_override_modes`:
    \\future drift if one of those surfaces changes without moving the full packet together
    \\Differential replay remains fixture-backed, not source-backed
    \\compare the Zig bridge packet directly against in-repo `conf.c` / `confdata.c` behavior
    \\preserve the current helper-packet guard and avoid widening Phase 2 kconfig claims
;

const request_plan_modes = [_][]const u8{
    "allmodconfig",
    "alldefconfig",
    "randconfig",
};

const sentinel_modes = [_][]const u8{
    "allnoconfig",
    "allyesconfig",
};

const helper_local_modes = [_][]const u8{
    "allmodconfig",
    "allnoconfig",
    "allyesconfig",
    "alldefconfig",
    "randconfig",
};

test "closure names the kconfig gap survey and source-anchor boundary" {
    try expectContains(closure_markers, "`PHASE2_CURRENT_GAP_PACKET=Documentation/zigux/phase2-kconfig-bridge-gap-survey.md`");
    try expectContains(closure_markers, "current authenticated repo reads do not expose `scripts/kconfig/conf.c` or `scripts/kconfig/confdata.c` on `master`");
    try expectContains(closure_markers, "the shipped kconfig bridge packet remains fixture-backed rather than same-tree differential");
    try expectContains(closure_markers, "add a direct `conf.c` / `confdata.c` provenance anchor once those C sources are readable in-tree again on current `master`");

    try expectContains(survey_markers, "Differential replay remains fixture-backed, not source-backed");
    try expectContains(survey_markers, "compare the Zig bridge packet directly against in-repo `conf.c` / `confdata.c` behavior");
}

test "closure and survey keep the allconfig split explicit" {
    try expectContains(closure_markers, "the next same-family truthfulness pass should keep reminder surfaces aligned with the live split recorded in `zigux/tests/fixtures/kconfig_bridge/cases.json` and `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`");
    try expectContains(closure_markers, "request-plan `allconfig` overrides stay limited to `allmodconfig`, `alldefconfig`, and `randconfig`");
    try expectContains(closure_markers, "`allconfig_sentinel_packet` still covers `allnoconfig` and `allyesconfig`");
    try expectContains(closure_markers, "the helper-local explicit-override roster remains broader by design");

    try expectContains(survey_markers, "The live fixture packet and manifest split the `allconfig` story across two explicit surfaces.");
    try expectContains(survey_markers, "The request-plan packet in `zigux/tests/fixtures/kconfig_bridge/cases.json` and `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`");
    try expectContains(survey_markers, "The manifest keeps these sentinel-backed modes separate through `allconfig_sentinel_packet`:");
    try expectContains(survey_markers, "The helper-local reminder packet still names the broader explicit-override guard surface through `helper_local_allconfig_explicit_override_modes`:");
}

test "manifest preserves request-plan, sentinel, and helper-local allconfig rosters" {
    try expectContains(conf_manifest, "\"allconfig_override_packet\"");
    for (request_plan_modes) |mode| {
        try expectContains(conf_manifest, mode);
        try expectContains(closure_markers, mode);
    }

    try expectContains(conf_manifest, "\"allconfig_sentinel_packet\"");
    for (sentinel_modes) |mode| {
        try expectContains(conf_manifest, mode);
        try expectContains(closure_markers, mode);
    }

    try expectContains(conf_manifest, "\"helper_local_allconfig_explicit_override_modes\"");
    for (helper_local_modes) |mode| {
        try expectContains(conf_manifest, mode);
    }

    try expectContains(survey_markers, "future drift if one of those surfaces changes without moving the full packet together");
    try expectContains(survey_markers, "preserve the current helper-packet guard and avoid widening Phase 2 kconfig claims");
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}
