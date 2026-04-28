const std = @import("std");

const SurveySummary = struct {
    phase6_leaf_helper_count: usize,
    runtime_sample_count: usize,
    runtime_loader_plan_count: usize,
    runtime_loader_projection_gap_count: usize,
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

const DeliveryEvidence = struct {
    id: []const u8,
    kind: []const u8,
    path: []const u8,
    role: []const u8,
};

const OwnershipEntry = struct {
    surface: []const u8,
    owns: []const u8,
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
    delivery_evidence_catalog: []const DeliveryEvidence,
    ownership_map: []const OwnershipEntry,
    gaps: []const Gap,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "blocked_on_loader_projection") or
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

test "runtime loader gap survey manifest keeps the roadmap boundary and shared request surface explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/runtime_loader_gap_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
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
    try std.testing.expectEqual(@as(usize, 2), manifest.survey_summary.runtime_loader_projection_gap_count);
    try std.testing.expect(manifest.survey_summary.shared_runtime_loader_present);
    try std.testing.expect(manifest.survey_summary.allocator_policy_present);
    try std.testing.expect(manifest.survey_summary.shared_init_exit_contract_present);
    try std.testing.expect(!manifest.survey_summary.shared_command_environment_control_present);
    try std.testing.expectEqual(@as(usize, 4), manifest.phase6_leaf_helpers.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.runtime_samples.len);
    try std.testing.expectEqual(@as(usize, 2), manifest.runtime_loader_plans.len);
    try std.testing.expectEqual(@as(usize, 9), manifest.delivery_evidence_catalog.len);
    try std.testing.expectEqual(@as(usize, 9), manifest.ownership_map.len);
    try std.testing.expectEqual(@as(usize, 11), manifest.gaps.len);

    try std.testing.expectEqualStrings("lib/base64.zig", manifest.phase6_leaf_helpers[0]);
    try std.testing.expectEqualStrings("lib/hexdump.zig", manifest.phase6_leaf_helpers[3]);
    try std.testing.expectEqualStrings("samples/zigux/runtime_atomic64.zig", manifest.runtime_samples[0]);
    try std.testing.expectEqualStrings("samples/zigux/runtime_trace_events.zig", manifest.runtime_samples[3]);
    try std.testing.expectEqualStrings("samples/zigux/runtime_bitmap_loader.zig", manifest.runtime_loader_plans[0]);
    try std.testing.expectEqualStrings("samples/zigux/runtime_kretprobe_loader.zig", manifest.runtime_loader_plans[1]);
    try std.testing.expectEqualStrings("runtime-loader-gap-note", manifest.delivery_evidence_catalog[0].id);
    try std.testing.expectEqualStrings("Documentation/zigux/phase9-runtime-loader-gap-survey.md", manifest.delivery_evidence_catalog[0].path);
    try std.testing.expectEqualStrings("runtime-loader-freeze-map", manifest.delivery_evidence_catalog[2].id);
    try std.testing.expectEqualStrings("Documentation/zigux/freeze-map.md", manifest.delivery_evidence_catalog[2].path);
    try std.testing.expectEqualStrings("runtime-loader-gap-manifest", manifest.delivery_evidence_catalog[3].id);
    try std.testing.expectEqualStrings("zigux/tests/runtime_loader_gap_manifest.json", manifest.delivery_evidence_catalog[3].path);
    try std.testing.expectEqualStrings("shared-runtime-loader-contract", manifest.delivery_evidence_catalog[6].id);
    try std.testing.expectEqualStrings("zigux/kernel/runtime_loader.zig", manifest.delivery_evidence_catalog[6].path);
    try std.testing.expectEqualStrings("Documentation/zigux/phase9-runtime-loader-gap-survey.md", manifest.ownership_map[0].surface);
    try std.testing.expectEqualStrings("Documentation/zigux/freeze-map.md", manifest.ownership_map[2].surface);
    try std.testing.expectEqualStrings("zigux/tests/runtime_loader_gap_manifest.json", manifest.ownership_map[3].surface);
    try std.testing.expectEqualStrings("zigux/kernel/runtime_loader.zig", manifest.ownership_map[6].surface);
    try std.testing.expectEqualStrings("samples/zigux/runtime_kretprobe_loader.zig", manifest.ownership_map[8].surface);

    var landed_count: usize = 0;
    var blocked_count: usize = 0;
    var loader_projection_blocked_count: usize = 0;
    var saw_manifest_catalog = false;
    var saw_freeze_map_doc = false;
    var saw_shared_contract = false;
    var saw_bitmap_loader_plan = false;
    var saw_kretprobe_loader_plan = false;

    for (manifest.delivery_evidence_catalog, 0..) |entry, i| {
        try std.testing.expect(entry.id.len > 0);
        try std.testing.expect(entry.kind.len > 0);
        try std.testing.expect(entry.path.len > 0);
        try std.testing.expect(entry.role.len > 0);

        if (std.mem.eql(u8, entry.id, "runtime-loader-gap-manifest")) {
            saw_manifest_catalog = true;
            try std.testing.expectEqualStrings("manifest", entry.kind);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "manifest-backed catalog and ownership map") != null);
        }
        if (std.mem.eql(u8, entry.id, "runtime-loader-freeze-map")) {
            saw_freeze_map_doc = true;
            try std.testing.expectEqualStrings("governance", entry.kind);
            try std.testing.expectEqualStrings("Documentation/zigux/freeze-map.md", entry.path);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "`kernel/workqueue.c`") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "Architecture Council") != null);
        }
        if (std.mem.eql(u8, entry.id, "shared-runtime-loader-contract")) {
            saw_shared_contract = true;
            try std.testing.expectEqualStrings("zigux/kernel/runtime_loader.zig", entry.path);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "shared request contract") != null);
        }
        if (std.mem.eql(u8, entry.id, "bitmap-loader-plan")) {
            saw_bitmap_loader_plan = true;
            try std.testing.expectEqualStrings("samples/zigux/runtime_bitmap_loader.zig", entry.path);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "bitmap loader-plan projection") != null);
        }
        if (std.mem.eql(u8, entry.id, "kretprobe-loader-plan")) {
            saw_kretprobe_loader_plan = true;
            try std.testing.expectEqualStrings("samples/zigux/runtime_kretprobe_loader.zig", entry.path);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "kretprobe loader-plan projection") != null);
        }

        for (manifest.delivery_evidence_catalog[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, entry.id, other.id));
        }
    }

    for (manifest.ownership_map, 0..) |entry, i| {
        try std.testing.expect(entry.surface.len > 0);
        try std.testing.expect(entry.owns.len > 0);

        if (std.mem.eql(u8, entry.surface, "zigux/tests/runtime_loader_gap_manifest.json")) {
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "manifest-backed catalog and ownership map") != null);
        }
        if (std.mem.eql(u8, entry.surface, "Documentation/zigux/freeze-map.md")) {
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "`kernel/workqueue.c`") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "Architecture Council") != null);
        }
        if (std.mem.eql(u8, entry.surface, "zigux/kernel/runtime_loader.zig")) {
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "shared request contract") != null);
        }
        if (std.mem.eql(u8, entry.surface, "samples/zigux/runtime_bitmap_loader.zig")) {
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "bitmap loader-plan projection") != null);
        }
        if (std.mem.eql(u8, entry.surface, "samples/zigux/runtime_kretprobe_loader.zig")) {
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "kretprobe loader-plan projection") != null);
        }

        for (manifest.ownership_map[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, entry.surface, other.surface));
        }
    }

    var saw_build = false;
    var saw_gate = false;
    var saw_note = false;
    var saw_review_checklist = false;
    var saw_plan_inputs = false;
    var saw_atomic64_plan_bridge = false;
    var saw_trace_events_plan_bridge = false;
    var saw_workqueue_freeze_blocker = false;
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
        } else if (std.mem.eql(u8, gap.status, "blocked_on_loader_projection")) {
            blocked_count += 1;
            loader_projection_blocked_count += 1;
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
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "landed shared runtime-loader seam") != null);
        }
        if (std.mem.eql(u8, gap.id, "runtime-loader-gap-note")) {
            saw_note = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase9-runtime-loader-gap-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "Phase 6 should not absorb runtime allocator or init-flow work") != null);
        }
        if (std.mem.eql(u8, gap.id, "runtime-loader-review-checklist")) {
            saw_review_checklist = true;
            try std.testing.expectEqualStrings("Documentation/zigux/review-checklist.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "hidden runtime services") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "implicit allocation posture") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "panic behavior") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "visible unsafe ownership") != null);
        }
        if (std.mem.eql(u8, gap.id, "runtime-loader-plan-inputs")) {
            saw_plan_inputs = true;
            try std.testing.expectEqualStrings("samples/zigux/runtime_*_loader.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "entry and exit symbol names") != null);
        }
        if (std.mem.eql(u8, gap.id, "runtime-loader-atomic64-plan-bridge")) {
            saw_atomic64_plan_bridge = true;
            try std.testing.expectEqualStrings("blocked_on_loader_projection", gap.status);
            try std.testing.expectEqualStrings("samples/zigux/runtime_atomic64.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "Phase 9 starter") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "zigux/kernel/runtime_loader.zig") != null);
        }
        if (std.mem.eql(u8, gap.id, "runtime-loader-trace-events-plan-bridge")) {
            saw_trace_events_plan_bridge = true;
            try std.testing.expectEqualStrings("blocked_on_loader_projection", gap.status);
            try std.testing.expectEqualStrings("samples/zigux/runtime_trace_events.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "Phase 9 starter") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "zigux/kernel/runtime_loader.zig") != null);
        }
        if (std.mem.eql(u8, gap.id, "runtime-loader-workqueue-freeze-map-boundary")) {
            saw_workqueue_freeze_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_runtime_substrate", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase9-runtime-loader-gap-survey.md", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "`kernel/workqueue.c`") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "task scheduling") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "polling") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "event-loop behavior") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "Architecture Council") != null);
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
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/kernel/runtime_loader.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "consumes the allocator policy contract directly") != null);
        }
        if (std.mem.eql(u8, gap.id, "runtime-loader-init-exit-consumer")) {
            saw_init_exit_blocker = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/kernel/runtime_loader.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "shared runtime-loader request surface now carries staged entry and exit symbol names") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 7), landed_count);
    try std.testing.expectEqual(@as(usize, 4), blocked_count);
    try std.testing.expectEqual(@as(usize, 2), loader_projection_blocked_count);
    try std.testing.expect(saw_manifest_catalog);
    try std.testing.expect(saw_freeze_map_doc);
    try std.testing.expect(saw_shared_contract);
    try std.testing.expect(saw_bitmap_loader_plan);
    try std.testing.expect(saw_kretprobe_loader_plan);
    try std.testing.expect(saw_build);
    try std.testing.expect(saw_gate);
    try std.testing.expect(saw_note);
    try std.testing.expect(saw_review_checklist);
    try std.testing.expect(saw_plan_inputs);
    try std.testing.expect(saw_atomic64_plan_bridge);
    try std.testing.expect(saw_trace_events_plan_bridge);
    try std.testing.expect(saw_workqueue_freeze_blocker);
    try std.testing.expect(saw_command_env_blocker);
    try std.testing.expect(saw_allocator_blocker);
    try std.testing.expect(saw_init_exit_blocker);
}

test "runtime loader gap survey doc keeps the mixed roadmap phases and remaining control-surface gap explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const freeze_map = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "Documentation/zigux/freeze-map.md",
        16 * 1024,
    );
    defer std.testing.allocator.free(freeze_map);

    const survey_note = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "Documentation/zigux/phase9-runtime-loader-gap-survey.md",
        16 * 1024,
    );
    defer std.testing.allocator.free(survey_note);

    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "## Study / Boundary Only") != null);
    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "`kernel/workqueue.c`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "Phase 6") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "Phase 8") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "Phase 9") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "command and environment plumbing") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`runtime_atomic64` and `runtime_trace_events` starters still do not have shared loader-plan projections") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "Documentation/zigux/freeze-map.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`kernel/workqueue.c`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "Study / Boundary Only") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "workqueue parity") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "Architecture Council") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/helpers/allocator_policy.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/kernel/runtime_loader.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "entry and exit symbol names") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "no shared loader-plan projection yet exists for `samples/zigux/runtime_atomic64.zig` or `samples/zigux/runtime_trace_events.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "command or environment control surface") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "argv policy") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "environment-derived activation cues") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "bounded shared runtime-loader request surface") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "Documentation/zigux/review-checklist.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "no hidden runtime services") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "no implicit allocation posture beyond the explicit allocator-handoff contract") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "no unclear panic or unsafe ownership story") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "Delivery ownership map") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "manifest-backed catalog") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "bitmap loader-plan projection") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "kretprobe loader-plan projection") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "pre-execution") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "Phase 6 runtime implementation progress") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "add one shared loader-plan projection for either `samples/zigux/runtime_atomic64.zig` or `samples/zigux/runtime_trace_events.zig`") != null);
}

test "runtime loader gap survey keeps the review checklist runtime guardrails explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const review_checklist = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "Documentation/zigux/review-checklist.md",
        16 * 1024,
    );
    defer std.testing.allocator.free(review_checklist);

    try expectContainsAll(review_checklist, &.{
        "## ABI and Runtime",
        "does the change avoid hidden runtime services, implicit allocation, or unclear panic behavior?",
        "if unsafe code exists, is it narrow, visible, and review-owned?",
        "are parity tests or fixture checks included?",
        "is there a stated rollback owner and fallback path?",
        "if the change touches the shared Phase 9 runtime-loader evidence packet, does the manifest-backed catalog and ownership map still keep the survey note, review checklist, shared request contract, sample-side loader plans, and shared `phase9_build.zig` entrypoint in one reviewable ownership packet?",
    });
}

test "runtime loader gap survey proves the shared request surface and existing loader controls directly" {
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

    const runtime_loader_file = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "zigux/kernel/runtime_loader.zig",
        16 * 1024,
    );
    defer std.testing.allocator.free(runtime_loader_file);

    const shared_loader_surface = [_][]const u8{
        "pub const LoaderStage = runtime_loader.LoaderStage;",
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
        "pub fn requestSharedRuntimeLoad",
        "pub fn releaseWithoutSubstrate",
        "@import(\"runtime_loader\")",
    };
    const shared_request_surface = [_][]const u8{
        "pub const RuntimeLoadRequest = struct",
        "pub fn isWaitingOnRuntimeSubstrate",
        "pub fn isReleasedWithoutSubstrate",
        "pub fn releasedWithoutSubstrate",
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
    try expectContainsNone(runtime_loader_file, &absent_command_env_surface);
    try expectContainsAll(runtime_loader_file, &.{
        "pub const AllocatorHandoff = struct",
        "pub const LoaderPayload = union(LoaderLane)",
        "allocator_handoff",
        "pub fn allocatorHandoffFor",
    });
    try expectContainsAll(runtime_loader_file, &shared_request_surface);

    try expectContainsAll(bitmap_loader, &.{
        "pub const RuntimeBitmapLoadPlan = struct",
        "summary: runtime_bitmap_sample.RuntimeBitmapSummary",
        "\"zigux_runtime_bitmap_init\"",
        "\"zigux_runtime_bitmap_exit\"",
        "pub fn toSharedRequest",
        ".allocator_handoff = runtime_loader.allocatorHandoffFor(.kernel_heap)",
        ".payload = .{",
        ".bitmap = .{",
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
        "pub fn toSharedRequest",
        ".allocator_handoff = runtime_loader.allocatorHandoffFor(.kernel_heap)",
        ".kretprobe = .{",
    });
}
