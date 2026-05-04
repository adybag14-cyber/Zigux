const std = @import("std");
const syscalls = @import("landlock_syscalls");

const SurveySummary = struct {
    syscalls_c_lines: usize,
    landlock_security_file_count: usize,
    preexisting_phase13_build_present: bool,
    preexisting_phase13_make_target_present: bool,
    preexisting_syscalls_zig_present: bool,
    preexisting_phase13_landlock_syscalls_test_present: bool,
    preexisting_phase13_landlock_syscalls_reviewability_present: bool,
    preexisting_phase13_landlock_syscalls_slice_note_present: bool,
    preexisting_phase13_landlock_syscalls_survey_note_present: bool,
};

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    anchor: []const u8,
    roadmap_destinations: []const []const u8,
    survey_summary: SurveySummary,
    gaps: []const Gap,
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectGap(manifest: Manifest, id: []const u8, status: []const u8, destination: []const u8) !void {
    for (manifest.gaps) |gap| {
        if (!std.mem.eql(u8, gap.id, id)) continue;

        try std.testing.expectEqualStrings(status, gap.status);
        try std.testing.expectEqualStrings(destination, gap.zigux_destination);
        return;
    }

    return error.MissingManifestGap;
}

test "phase13 landlock syscalls reviewability ties helper, survey, manifest, and build wiring together" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase13_landlock_syscalls_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P13-L16", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 13", manifest.phase);
    try std.testing.expectEqualStrings("security/landlock/syscalls.c", manifest.anchor);
    try std.testing.expectEqualStrings("672d03034b090ab859f4088396160ea13120e1d6", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.syscalls_c_lines >= 500);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_landlock_syscalls_test_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_landlock_syscalls_reviewability_present);
    try std.testing.expectEqual(@as(usize, 17), manifest.gaps.len);
    try expectGap(manifest, "phase13-landlock-ruleset-fops-followup", "starter_landed", "security/landlock/syscalls.zig");

    const descriptor = syscalls.SyscallsHelperLab.descriptor();
    try std.testing.expectEqualStrings("landlock_syscalls_helper_lab", descriptor.name);
    try std.testing.expectEqualStrings("security/landlock/syscalls.c", descriptor.anchor);
    try std.testing.expect(descriptor.provides_abi_shape_reporting);
    try std.testing.expect(descriptor.provides_initialization_gate_planning);
    try std.testing.expect(descriptor.provides_min_struct_copy_planning);
    try std.testing.expect(descriptor.provides_create_ruleset_query_planning);
    try std.testing.expect(descriptor.provides_restrict_self_flag_planning);
    try std.testing.expect(descriptor.provides_restrict_self_credential_handoff_planning);
    try std.testing.expect(descriptor.provides_add_rule_planning);
    try std.testing.expect(descriptor.provides_rule_attr_copy_planning);
    try std.testing.expect(descriptor.provides_ruleset_fd_planning);
    try std.testing.expect(descriptor.provides_ruleset_fd_creation_planning);
    try std.testing.expect(descriptor.provides_ruleset_fops_planning);
    try std.testing.expect(descriptor.provides_path_fd_planning);
    try std.testing.expect(descriptor.provides_path_beneath_handoff_planning);
    try std.testing.expect(descriptor.provides_net_port_handoff_planning);
    try std.testing.expect(!descriptor.touches_live_fd_table);
    try std.testing.expect(!descriptor.touches_live_paths);
    try std.testing.expect(!descriptor.touches_live_credentials);
    try std.testing.expect(!descriptor.touches_live_domains);

    const slice_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase13-landlock-syscalls-slice.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(slice_note);

    try expectContains(slice_note, "# Phase 13 Landlock Syscalls Slice");
    try expectContains(slice_note, "PHASE13_OWNERSHIP_BOUNDARY=ruleset-fd-handoff-helper-only");
    try expectContains(slice_note, "landlock_put_ruleset()");
    try expectContains(slice_note, "fop_ruleset_release()");
    try expectContains(slice_note, "`zigux/tests/phase13_landlock_ruleset_fops_sync.zig`");
    try expectContains(slice_note, "same-family `zigux/tests/phase13_landlock_ruleset_fops_sync.zig` guard");
    try expectContains(slice_note, "live FD-table ownership remains with the C implementation");

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase13-landlock-syscalls-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    try expectContains(survey_note, "# Phase 13 Landlock Syscalls Survey");
    try expectContains(survey_note, "PHASE13_SLICE=landlock-syscalls-helper-pure-handoff-boundary");
    try expectContains(survey_note, "PHASE13_SURVEYED_COMMIT=672d03034b090ab859f4088396160ea13120e1d6");
    try expectContains(survey_note, "`zigux/tests/phase13_landlock_syscalls_reviewability.zig`");
    try expectContains(survey_note, "- `zigux/tests/phase13_landlock_ruleset_fops_sync.zig`");
    try expectContains(survey_note, "`zigux/tests/phase13_landlock_ruleset_fops_sync.zig`");
    try expectContains(survey_note, "dedicated reviewability gate now ties the helper surface, manifest, survey note, the same-family `phase13_landlock_ruleset_fops_sync.zig` evidence, and shared Phase 13 build wiring together");
    try expectContains(survey_note, "landed `phase13-landlock-syscalls-reviewability-gate`");
    try expectContains(survey_note, "manifest-backed reviewability gate");

    const traceability_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase13-roadmap-traceability.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(traceability_note);

    try expectContains(traceability_note, "future docs-root, release-note, or checklist updates should keep the dedicated `zigux/tests/phase13_landlock_syscalls_reviewability.zig` gate and the same-family `zigux/tests/phase13_landlock_ruleset_fops_sync.zig` guard visible together with the roadmap-adjacent notifier packet, including `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `include/zigux/notifier_abi.h`, and `zigux/helpers/notifier_chain_view.zig`, while continuing to describe Phase 13 closure through the four manifest-backed roadmap anchors only");

    const build_file = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase13_build.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(build_file);

    try expectContains(build_file, "phase13_landlock_syscalls_reviewability.zig");
    try expectContains(build_file, "phase13-landlock-syscalls-reviewability-tests");
    try expectContains(build_file, "phase13_landlock_syscalls_reviewability_module.addImport(\"landlock_syscalls\", landlock_syscalls_module);");
    try expectContains(build_file, "test_step.dependOn(&run_phase13_landlock_syscalls_reviewability_tests.step);");
    try expectContains(build_file, "phase13_landlock_ruleset_fops_sync.zig");
    try expectContains(build_file, "phase13-landlock-ruleset-fops-sync-tests");
}
