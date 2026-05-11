const std = @import("std");

const Gap = struct {
    id: []const u8,
    status: []const u8,
    evidence: []const u8,
    next_step: []const u8,
};

const Summary = struct {
    c_anchor_present: bool,
    c_anchor_exports_managed_ioremap: bool,
    c_anchor_exports_managed_resource_wrapper: bool,
    zig_helper_missing_or_empty: bool,
    latest_phase13_commit_targets_devres: bool,
    note_records_roadmap_anchor_set: bool,
    note_records_churn_warning: bool,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    anchor: []const u8,
    helper_target: []const u8,
    surveyed_commit: []const u8,
    surveyed_commit_title: []const u8,
    status_bucket: []const u8,
    validation_gate: []const u8,
    gaps: []const Gap,
    survey_summary: Summary,
};

fn isLowerHex40(value: []const u8) bool {
    if (value.len != 40) return false;
    for (value) |ch| {
        switch (ch) {
            '0'...'9', 'a'...'f' => {},
            else => return false,
        }
    }
    return true;
}

fn hasGapWithStatus(gaps: []const Gap, gap_id: []const u8, status: []const u8) bool {
    for (gaps) |gap| {
        if (std.mem.eql(u8, gap.id, gap_id) and std.mem.eql(u8, gap.status, status)) {
            return true;
        }
    }
    return false;
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase13 devres manifest records the current resource lifetime helper gap" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase13_devres_resource_lifetime_manifest.json",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P13-L07", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 13", manifest.phase);
    try std.testing.expectEqualStrings("lib/devres.c", manifest.anchor);
    try std.testing.expectEqualStrings("lib/devres.zig", manifest.helper_target);
    try std.testing.expect(isLowerHex40(manifest.surveyed_commit));
    try std.testing.expectEqualStrings(
        "Align Phase 13 notifier priority checker with repo reality",
        manifest.surveyed_commit_title,
    );
    try std.testing.expectEqualStrings("survey_only", manifest.status_bucket);
    try std.testing.expectEqualStrings(
        "zig test zigux/tests/phase13_devres_resource_lifetime_survey.zig",
        manifest.validation_gate,
    );
    try std.testing.expectEqual(@as(usize, 3), manifest.gaps.len);
    try std.testing.expect(hasGapWithStatus(
        manifest.gaps,
        "phase13-devres-zig-anchor-empty",
        "blocked_on_repo_gap",
    ));
    try std.testing.expect(hasGapWithStatus(
        manifest.gaps,
        "phase13-devres-managed-ioremap-slice",
        "ready_next",
    ));
    try std.testing.expect(hasGapWithStatus(
        manifest.gaps,
        "phase13-shared-helper-churn-risk",
        "guardrail",
    ));
    try std.testing.expect(manifest.survey_summary.c_anchor_present);
    try std.testing.expect(manifest.survey_summary.c_anchor_exports_managed_ioremap);
    try std.testing.expect(manifest.survey_summary.c_anchor_exports_managed_resource_wrapper);
    try std.testing.expect(manifest.survey_summary.zig_helper_missing_or_empty);
    try std.testing.expect(!manifest.survey_summary.latest_phase13_commit_targets_devres);
    try std.testing.expect(manifest.survey_summary.note_records_roadmap_anchor_set);
    try std.testing.expect(manifest.survey_summary.note_records_churn_warning);
}

test "phase13 devres survey note and fixture reflect the bounded next step" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const allocator = std.testing.allocator;

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase13_devres_resource_lifetime_manifest.json",
        allocator,
        .limited(16 * 1024),
    );
    defer allocator.free(manifest_json);
    const manifest = try std.json.parseFromSlice(Manifest, allocator, manifest_json, .{});
    defer manifest.deinit();

    const note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase13-devres-resource-lifetime-survey.md",
        allocator,
        .limited(16 * 1024),
    );
    defer allocator.free(note);

    try expectContains(note, "# Phase 13 Devres Resource Lifetime Survey");
    try expectContains(note, manifest.value.anchor);
    try expectContains(note, manifest.value.helper_target);
    try expectContains(note, manifest.value.surveyed_commit);
    try expectContains(note, manifest.value.surveyed_commit_title);
    try expectContains(note, "resource lifetime helpers");
    try expectContains(note, "fs/libfs.c");
    try expectContains(note, "security/landlock/ruleset.c");
    try expectContains(note, "security/landlock/syscalls.c");
    try expectContains(note, "devm_ioremap");
    try expectContains(note, "devm_ioremap_resource");
    try expectContains(note, "devm_ioport_map");
    try expectContains(note, "devm_arch_phys_wc_add");
    try expectContains(note, "empty placeholder");
    try expectContains(note, "Next bounded step");
    try expectContains(note, "managed ioremap/resource wrapper slice");
    try expectContains(note, "shared-subsystem helper churn");

    try expectContains(note, "devm_arch_io_reserve_memtype_wc");
}
