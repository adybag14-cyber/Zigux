const std = @import("std");

const max_file_size = 128 * 1024;

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        std.Io.Threaded.global_single_threaded.io(),
        path,
        allocator,
        .limited(max_file_size),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

fn countNeedle(haystack: []const u8, needle: []const u8) usize {
    var rest = haystack;
    var count: usize = 0;
    while (std.mem.indexOf(u8, rest, needle)) |index| {
        count += 1;
        rest = rest[index + needle.len ..];
    }
    return count;
}

test "closure note keeps the kconfig gap packet parked and source-backed follow-through gated" {
    const closure_note = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase2-closure.md");
    defer std.testing.allocator.free(closure_note);

    try expectContains(closure_note, "PHASE2_CURRENT_GAP_PACKET=Documentation/zigux/phase2-kconfig-bridge-gap-survey.md");
    try expectContains(closure_note, "current authenticated repo reads do not expose `scripts/kconfig/conf.c` or `scripts/kconfig/confdata.c` on `master`");
    try expectContains(closure_note, "fixture-backed rather than same-tree differential");
    try expectContains(closure_note, "add a direct `conf.c` / `confdata.c` provenance anchor once those C sources are readable in-tree again");

    try expectBefore(
        closure_note,
        "request-plan `allconfig` overrides stay limited to `allmodconfig`, `alldefconfig`, and `randconfig`",
        "allconfig_sentinel_packet` still covers `allnoconfig` and `allyesconfig`",
    );
    try expectBefore(
        closure_note,
        "allconfig_sentinel_packet` still covers `allnoconfig` and `allyesconfig`",
        "helper-local explicit-override roster remains broader by design",
    );
    try expectBefore(
        closure_note,
        "preserves the live split between request-plan overrides",
        "then add a direct `conf.c` / `confdata.c` provenance anchor",
    );
}

test "kconfig gap survey keeps current source gap distinct from guarded allconfig drift" {
    const gap_survey = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase2-kconfig-bridge-gap-survey.md");
    defer std.testing.allocator.free(gap_survey);

    try expectContains(gap_survey, "Upstream source-anchor gap");
    try expectContains(gap_survey, "current authenticated repo reads still do not expose those C sources on `master`");
    try expectContains(gap_survey, "same-tree parity against current in-repo C sources is still unavailable");
    try expectContains(gap_survey, "Differential replay remains fixture-backed, not source-backed");

    try expectContains(gap_survey, "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py");
    try expectContains(gap_survey, "compares them to `conf_manifest.json`");
    try expectContains(gap_survey, "allconfig_sentinel_packet");
    try expectContains(gap_survey, "helper_local_allconfig_explicit_override_modes");
    try expectContains(gap_survey, "keep the `allconfig` helper-packet checker, manifest, closure note, and Phase 2 validators aligned");
    try expectNotContains(gap_survey, "the kconfig bridge lane is source-backed");
}

test "manifest and fixture roster preserve the three-way allconfig split named by the closure note" {
    const conf_manifest = try readRepoFile(std.testing.allocator, "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json");
    defer std.testing.allocator.free(conf_manifest);
    const cases_json = try readRepoFile(std.testing.allocator, "zigux/tests/fixtures/kconfig_bridge/cases.json");
    defer std.testing.allocator.free(cases_json);

    try expectContains(conf_manifest, "\"case_count\": 16");
    try expectContains(conf_manifest, "\"allconfig_override_packet\"");
    try expectContains(conf_manifest, "\"allmodconfig_expected.json\"");
    try expectContains(conf_manifest, "\"alldefconfig_expected.json\"");
    try expectContains(conf_manifest, "\"randconfig_expected.json\"");
    try expectContains(conf_manifest, "\"allconfig_sentinel_packet\"");
    try expectContains(conf_manifest, "\"allnoconfig_expected.json\"");
    try expectContains(conf_manifest, "\"allyesconfig_expected.json\"");
    try expectContains(conf_manifest, "\"helper_local_allconfig_explicit_override_modes\"");

    try expectContains(cases_json, "\"name\": \"allmodconfig\"");
    try expectContains(cases_json, "\"name\": \"alldefconfig\"");
    try expectContains(cases_json, "\"name\": \"randconfig\"");
    try expectContains(cases_json, "\"name\": \"allnoconfig\"");
    try expectContains(cases_json, "\"name\": \"allyesconfig\"");
    try std.testing.expectEqual(@as(usize, 3), countNeedle(cases_json, "\"allconfig\""));
}
