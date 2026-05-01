const std = @import("std");

const SurveySummary = struct {
    runtime_descriptor_count: usize,
    runtime_loader_lane_count: usize,
    runtime_loader_plan_count: usize,
    runtime_sample_only_blocked_count: usize,
    shared_metadata_field_count: usize,
    depmod_gap_count: usize,
    shared_runtime_loader_present: bool,
    runtime_trace_events_loader_present: bool,
};

const DescriptorSurface = struct {
    sample_path: []const u8,
    module_name: []const u8,
    anchor: []const u8,
};

const SampleOnlyBlocked = struct {
    sample_path: []const u8,
    blocked_loader_path: []const u8,
    blocker_note: []const u8,
    why_blocked: []const u8,
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
    phase: []const u8,
    surveyed_commit: []const u8,
    anchor: []const u8,
    roadmap_destinations: []const []const u8,
    survey_summary: SurveySummary,
    descriptor_surfaces: []const DescriptorSurface,
    shared_runtime_loader_metadata_fields: []const []const u8,
    runtime_loader_plans: []const []const u8,
    runtime_sample_only_blocked: []const SampleOnlyBlocked,
    depmod_gap_surfaces: []const []const u8,
    delivery_evidence_catalog: []const DeliveryEvidence,
    ownership_map: []const OwnershipEntry,
    review_prompts: []const []const u8,
};

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

fn isLowerHexSha(value: []const u8) bool {
    if (value.len != 40) return false;
    for (value) |byte| {
        if (!std.ascii.isHex(byte) or std.ascii.isUpper(byte)) return false;
    }
    return true;
}

test "runtime module metadata manifest keeps the dedicated descriptor and depmod-gap packet explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "zigux/tests/runtime_module_metadata_manifest.json",
        24 * 1024,
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P9-L07", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 9", manifest.phase);
    try std.testing.expect(isLowerHexSha(manifest.surveyed_commit));
    try std.testing.expect(std.mem.indexOf(u8, manifest.anchor, "RuntimeLoadRequest") != null);
    try std.testing.expectEqual(@as(usize, 2), manifest.roadmap_destinations.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.survey_summary.runtime_descriptor_count);
    try std.testing.expectEqual(@as(usize, 3), manifest.survey_summary.runtime_loader_lane_count);
    try std.testing.expectEqual(@as(usize, 3), manifest.survey_summary.runtime_loader_plan_count);
    try std.testing.expectEqual(@as(usize, 1), manifest.survey_summary.runtime_sample_only_blocked_count);
    try std.testing.expectEqual(@as(usize, 9), manifest.survey_summary.shared_metadata_field_count);
    try std.testing.expectEqual(@as(usize, 8), manifest.survey_summary.depmod_gap_count);
    try std.testing.expect(manifest.survey_summary.shared_runtime_loader_present);
    try std.testing.expect(!manifest.survey_summary.runtime_trace_events_loader_present);
    try std.testing.expectEqual(@as(usize, 4), manifest.descriptor_surfaces.len);
    try std.testing.expectEqual(@as(usize, 9), manifest.shared_runtime_loader_metadata_fields.len);
    try std.testing.expectEqual(@as(usize, 3), manifest.runtime_loader_plans.len);
    try std.testing.expectEqual(@as(usize, 1), manifest.runtime_sample_only_blocked.len);
    try std.testing.expectEqual(@as(usize, 8), manifest.depmod_gap_surfaces.len);
    try std.testing.expectEqual(@as(usize, 5), manifest.delivery_evidence_catalog.len);
    try std.testing.expectEqual(@as(usize, 5), manifest.ownership_map.len);
    try std.testing.expectEqual(@as(usize, 3), manifest.review_prompts.len);

    try std.testing.expectEqualStrings("samples/zigux/runtime_atomic64.zig", manifest.descriptor_surfaces[0].sample_path);
    try std.testing.expectEqualStrings("runtime_atomic64", manifest.descriptor_surfaces[0].module_name);
    try std.testing.expectEqualStrings("samples/trace_events/trace-events-sample.c", manifest.descriptor_surfaces[3].anchor);
    try std.testing.expectEqualStrings("module_name", manifest.shared_runtime_loader_metadata_fields[0]);
    try std.testing.expectEqualStrings("allocator_handoff", manifest.shared_runtime_loader_metadata_fields[8]);
    try std.testing.expectEqualStrings("samples/zigux/runtime_kretprobe_loader.zig", manifest.runtime_loader_plans[2]);
    try std.testing.expectEqualStrings("samples/zigux/runtime_trace_events_loader.zig", manifest.runtime_sample_only_blocked[0].blocked_loader_path);
    try std.testing.expect(std.mem.indexOf(u8, manifest.runtime_sample_only_blocked[0].why_blocked, "sample-only") != null);
    try std.testing.expectEqualStrings("MODULE_INFO()", manifest.depmod_gap_surfaces[0]);
    try std.testing.expectEqualStrings("scripts/depmod.sh", manifest.depmod_gap_surfaces[7]);
}

test "runtime module metadata survey note keeps descriptor fields, shared loader metadata, and depmod gaps explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const survey_note = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md",
        24 * 1024,
    );
    defer std.testing.allocator.free(survey_note);

    const loader_gap_note = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "Documentation/zigux/phase9-runtime-loader-gap-survey.md",
        24 * 1024,
    );
    defer std.testing.allocator.free(loader_gap_note);

    try expectContainsAll(survey_note, &.{
        "PHASE9_SLICE=runtime-module-metadata-depmod-bridge-survey",
        "PHASE9_SURVEYED_COMMIT=5a2398b1223d2c1e39c84c500f684244f4182eff",
        "ModuleDescriptor",
        "name",
        "anchor",
        "requires_runtime_substrate",
        "provides_selftest_hook",
        "RuntimeLoadRequest",
        "module_name",
        "command_name",
        "entry_symbol",
        "exit_symbol",
        "handoff_stage",
        "allocator_handoff",
        "samples/zigux/runtime_trace_events_loader.zig",
        "MODULE_INFO()",
        "MODULE_ALIAS()",
        ".modinfo",
        "modules.alias",
        "modules.order",
        "modules.builtin",
        "Module.symvers",
        "scripts/depmod.sh",
        "loadable-module metadata parity",
        "depmod bridge",
        "python3 scripts/zigux/validate-phase9.py",
        "zig build test --build-file zigux/tests/phase9_build.zig --summary all",
        "zig test zigux/tests/runtime_module_metadata_survey.zig",
    });
    try expectContainsAll(loader_gap_note, &.{
        "samples/zigux/runtime_trace_events_loader.zig",
        "sample-only blocked runtime pilot",
    });
}

test "runtime module metadata survey proves the live starter descriptors and shared loader metadata surface directly" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const runtime_atomic64 = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "samples/zigux/runtime_atomic64.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(runtime_atomic64);

    const runtime_bitmap = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "samples/zigux/runtime_bitmap.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(runtime_bitmap);

    const runtime_kretprobe = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "samples/zigux/runtime_kretprobe.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(runtime_kretprobe);

    const runtime_trace_events = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "samples/zigux/runtime_trace_events.zig",
        40 * 1024,
    );
    defer std.testing.allocator.free(runtime_trace_events);

    const runtime_loader = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "zigux/kernel/runtime_loader.zig",
        40 * 1024,
    );
    defer std.testing.allocator.free(runtime_loader);

    try expectContainsAll(runtime_atomic64, &.{
        "pub const ModuleDescriptor = struct",
        ".name = \"runtime_atomic64\"",
        ".anchor = \"lib/atomic64_test.c\"",
        ".requires_runtime_substrate = true",
        ".provides_selftest_hook = true",
    });
    try expectContainsAll(runtime_bitmap, &.{
        "pub const ModuleDescriptor = struct",
        ".name = \"runtime_bitmap\"",
        ".anchor = \"lib/test_bitmap.c\"",
        ".requires_runtime_substrate = true",
        ".provides_selftest_hook = true",
    });
    try expectContainsAll(runtime_kretprobe, &.{
        "pub const ModuleDescriptor = struct",
        ".name = \"runtime_kretprobe\"",
        ".anchor = \"samples/kprobes/kretprobe_example.c\"",
        ".requires_runtime_substrate = true",
        ".provides_selftest_hook = true",
    });
    try expectContainsAll(runtime_trace_events, &.{
        "pub const ModuleDescriptor = struct",
        ".name = \"runtime_trace_events\"",
        ".anchor = \"samples/trace_events/trace-events-sample.c\"",
        ".requires_runtime_substrate = true",
        ".provides_selftest_hook = true",
    });
    try expectContainsAll(runtime_loader, &.{
        "pub const LoaderLane = enum(u8)",
        "atomic64",
        "bitmap",
        "kretprobe",
        "pub const RuntimeLoadRequest = struct",
        "module_name",
        "command_name",
        "anchor",
        "entry_symbol",
        "exit_symbol",
        "requires_runtime_substrate",
        "provides_selftest_hook",
        "handoff_stage",
        "allocator_handoff",
    });
    try std.testing.expect(std.mem.indexOf(u8, runtime_loader, "trace_events") == null);
    try std.testing.expect(std.mem.indexOf(u8, runtime_atomic64, "MODULE_INFO(") == null);
    try std.testing.expect(std.mem.indexOf(u8, runtime_bitmap, "MODULE_ALIAS(") == null);
    try std.testing.expect(std.mem.indexOf(u8, runtime_kretprobe, ".modinfo") == null);
    try std.testing.expect(std.mem.indexOf(u8, runtime_trace_events, "modules.alias") == null);
}
