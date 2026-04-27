const std = @import("std");

const SurveySummary = struct {
    phase6_leaf_helper_count: usize,
    runtime_sample_count: usize,
    runtime_loader_plan_count: usize,
    shared_runtime_loader_present: bool,
    allocator_policy_present: bool,
    shared_init_exit_contract_present: bool,
    shared_command_environment_control_present: bool,
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
    schedule_phase: []const u8,
    roadmap_runtime_phase: []const u8,
    roadmap_command_environment_phase: []const u8,
    surveyed_commit: []const u8,
    anchor: []const u8,
    survey_summary: SurveySummary,
    phase6_leaf_helpers: []const []const u8,
    runtime_samples: []const []const u8,
    runtime_loader_plans: []const []const u8,
    gaps: []const Gap,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "blocked_on_runtime_substrate");
}

fn isLowerHexSha(value: []const u8) bool {
    if (value.len != 40) return false;
    for (value) |byte| {
        if (!std.ascii.isHex(byte) or std.ascii.isUpper(byte)) return false;
    }
    return true;
}

fn readWorkspaceFile(
    io: anytype,
    allocator: std.mem.Allocator,
    path: []const u8,
    limit: usize,
) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(io, path, allocator, .limited(limit));
}

fn expectContainsAll(haystack: []const u8, needles: []const []const u8) !void {
    for (needles) |needle| {
        try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
    }
}

fn expectContainsNone(haystack: []const u8, needles: []const []const u8) !void {
    for (needles) |needle| {
        try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
    }
}

test "runtime loader gap survey manifest keeps the roadmap boundary and blocker explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/runtime_loader_gap_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P6-L01", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 6", manifest.schedule_phase);
    try std.testing.expectEqualStrings("Phase 9", manifest.roadmap_runtime_phase);
    try std.testing.expectEqualStrings("Phase 8", manifest.roadmap_command_environment_phase);
    try std.testing.expect(isLowerHexSha(manifest.surveyed_commit));
    try std.testing.expect(std.mem.indexOf(u8, manifest.anchor, "zigux/kernel/runtime_loader.zig") != null);
    try std.testing.expectEqual(@as(usize, 4), manifest.survey_summary.phase6_leaf_helper_count);
    try std.testing.expectEqual(@as(usize, 4), manifest.survey_summary.runtime_sample_count);
    try std.testing.expectEqual(@as(usize, 2), manifest.survey_summary.runtime_loader_plan_count);
    try std.testing.expect(!manifest.survey_summary.shared_runtime_loader_present);
    try std.testing.expect(manifest.survey_summary.allocator_policy_present);
    try std.testing.expect(!manifest.survey_summary.shared_init_exit_contract_present);
    try std.testing.expect(!manifest.survey_summary.shared_command_environment_control_present);
    try std.testing.expectEqual(@as(usize, 4), manifest.phase6_leaf_helpers.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.runtime_samples.len);
    try std.testing.expectEqual(@as(usize, 2), manifest.runtime_loader_plans.len);
    try std.testing.expectEqual(@as(usize, 7), manifest.gaps.len);

    try std.testing.expectEqualStrings("lib/base64.zig", manifest.phase6_leaf_helpers[0]);
    try std.testing.expectEqualStrings("lib/hexdump.zig", manifest.phase6_leaf_helpers[3]);
    try std.testing.expectEqualStrings("samples/zigux/runtime_atomic64.zig", manifest.runtime_samples[0]);
    try std.testing.expectEqualStrings("samples/zigux/runtime_trace_events.zig", manifest.runtime_samples[3]);
    try std.testing.expectEqualStrings("samples/zigux/runtime_bitmap_loader.zig", manifest.runtime_loader_plans[0]);
    try std.testing.expectEqualStrings("samples/zigux/runtime_kretprobe_loader.zig", manifest.runtime_loader_plans[1]);

    var landed_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_build = false;
    var saw_gate = false;
    var saw_note = false;
    var saw_plan_inputs = false;
    var saw_command_env_blocker = false;
    var saw_allocator_blocker = false;
    var saw_init_exit_blocker = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_runtime_substrate")) {
            blocked_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "phase9-build-gate")) {
            saw_build = true;
            try std.testing.expectEqualStrings("zigux/tests/phase9_build.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "runtime-loader-gap-survey-gate")) {
            saw_gate = true;
            try std.testing.expectEqualStrings("zigux/tests/runtime_loader_gap_survey.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "Phase 9 roadmap target") != null);
        }
        if (std.mem.eql(u8, gap.id, "runtime-loader-gap-note")) {
            saw_note = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase9-runtime-loader-gap-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "Phase 6 should not absorb runtime allocator or init-flow work") != null);
        }
        if (std.mem.eql(u8, gap.id, "runtime-loader-plan-inputs")) {
            saw_plan_inputs = true;
            try std.testing.expectEqualStrings("samples/zigux/runtime_*_loader.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "entry and exit symbol names") != null);
        }
        if (std.mem.eql(u8, gap.id, "runtime-loader-command-environment-controls")) {
            saw_command_env_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_runtime_substrate", gap.status);
            try std.testing.expectEqualStrings("zigux/kernel/runtime_loader.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "Phase 8 tooling") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "argv-policy") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "environment-derived activation handling") != null);
        }
        if (std.mem.eql(u8, gap.id, "runtime-loader-allocator-handoff")) {
            saw_allocator_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_runtime_substrate", gap.status);
            try std.testing.expectEqualStrings("zigux/helpers/allocator_policy.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "allocator policy surface exists") != null);
        }
        if (std.mem.eql(u8, gap.id, "runtime-loader-init-exit-consumer")) {
            saw_init_exit_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_runtime_substrate", gap.status);
            try std.testing.expectEqualStrings("zigux/kernel/runtime_loader.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "entry and exit symbol names") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 4), landed_count);
    try std.testing.expectEqual(@as(usize, 3), blocked_count);
    try std.testing.expect(saw_build);
    try std.testing.expect(saw_gate);
    try std.testing.expect(saw_note);
    try std.testing.expect(saw_plan_inputs);
    try std.testing.expect(saw_command_env_blocker);
    try std.testing.expect(saw_allocator_blocker);
    try std.testing.expect(saw_init_exit_blocker);
}

test "runtime loader gap survey doc keeps the mixed roadmap phases and control-surface gap explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const survey_note = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "Documentation/zigux/phase9-runtime-loader-gap-survey.md",
        16 * 1024,
    );
    defer std.testing.allocator.free(survey_note);

    try std.testing.expect(std.mem.indexOf(u8, survey_note, "Phase 6") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "Phase 8") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "Phase 9") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "command and environment plumbing") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/helpers/allocator_policy.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/kernel/runtime_loader.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "entry and exit symbol names") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "command or environment control surface") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "argv policy") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "environment-derived activation cues") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "This slice therefore stays survey-only.") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "Phase 6 runtime implementation progress") != null);
}

test "runtime loader gap survey proves the existing loader control surfaces directly" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const bitmap_loader = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "samples/zigux/runtime_bitmap_loader.zig",
        16 * 1024,
    );
    defer std.testing.allocator.free(bitmap_loader);

    const kretprobe_loader = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "samples/zigux/runtime_kretprobe_loader.zig",
        16 * 1024,
    );
    defer std.testing.allocator.free(kretprobe_loader);

    const shared_loader_surface = [_][]const u8{
        "pub const LoaderStage = enum(u8)",
        "idle,",
        "prepared,",
        "waiting_on_runtime_substrate,",
        "released_without_substrate,",
        "entry_symbol",
        "exit_symbol",
        "requires_runtime_substrate",
        "provides_selftest_hook",
        "handoff_stage",
        "pub fn requestRuntimeLoad",
        "pub fn releaseWithoutSubstrate",
    };
    const absent_command_env_surface = [_][]const u8{
        "command_name",
        "argv_policy",
        "activation_env",
    };

    try expectContainsAll(bitmap_loader, &shared_loader_surface);
    try expectContainsAll(kretprobe_loader, &shared_loader_surface);
    try expectContainsNone(bitmap_loader, &absent_command_env_surface);
    try expectContainsNone(kretprobe_loader, &absent_command_env_surface);

    try expectContainsAll(bitmap_loader, &.{
        "pub const RuntimeBitmapLoadPlan = struct",
        "summary: runtime_bitmap_sample.RuntimeBitmapSummary",
        "\"zigux_runtime_bitmap_init\"",
        "\"zigux_runtime_bitmap_exit\"",
    });
    try expectContainsAll(kretprobe_loader, &.{
        "pub const RuntimeKretprobeLoadPlan = struct",
        "register_api",
        "unregister_api",
        "symbol_name",
        "maxactive",
        "private_data_bytes",
        "\"zigux_runtime_kretprobe_init\"",
        "\"zigux_runtime_kretprobe_exit\"",
        "\"register_kretprobe\"",
        "\"unregister_kretprobe\"",
    });
}
