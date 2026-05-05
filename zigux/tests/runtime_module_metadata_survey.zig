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

fn expectSurveyedCommitMarker(document: []const u8, commit: []const u8) !void {
    const marker = try std.fmt.allocPrint(std.testing.allocator, "`PHASE9_SURVEYED_COMMIT={s}`", .{commit});
    defer std.testing.allocator.free(marker);
    try std.testing.expect(std.mem.indexOf(u8, document, marker) != null);
}

fn expectPinnedCommitSentence(document: []const u8, commit: []const u8) !void {
    const sentence = try std.fmt.allocPrint(
        std.testing.allocator,
        "the current survey packet is pinned to `master` commit `{s}`",
        .{commit},
    );
    defer std.testing.allocator.free(sentence);
    try std.testing.expect(std.mem.indexOf(u8, document, sentence) != null);
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
    try std.testing.expectEqual(@as(usize, 4), manifest.survey_summary.runtime_loader_plan_count);
    try std.testing.expectEqual(@as(usize, 0), manifest.survey_summary.runtime_sample_only_blocked_count);
    try std.testing.expectEqual(@as(usize, 9), manifest.survey_summary.shared_metadata_field_count);
    try std.testing.expectEqual(@as(usize, 8), manifest.survey_summary.depmod_gap_count);
    try std.testing.expect(manifest.survey_summary.shared_runtime_loader_present);
    try std.testing.expect(manifest.survey_summary.runtime_trace_events_loader_present);
    try std.testing.expectEqual(@as(usize, 4), manifest.descriptor_surfaces.len);
    try std.testing.expectEqual(@as(usize, 9), manifest.shared_runtime_loader_metadata_fields.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.runtime_loader_plans.len);
    try std.testing.expectEqual(@as(usize, 0), manifest.runtime_sample_only_blocked.len);
    try std.testing.expectEqual(@as(usize, 8), manifest.depmod_gap_surfaces.len);
    try std.testing.expectEqual(@as(usize, 8), manifest.delivery_evidence_catalog.len);
    try std.testing.expectEqual(@as(usize, 8), manifest.ownership_map.len);
    try std.testing.expectEqual(@as(usize, 3), manifest.review_prompts.len);

    try std.testing.expectEqualStrings("samples/zigux/runtime_atomic64.zig", manifest.descriptor_surfaces[0].sample_path);
    try std.testing.expectEqualStrings("runtime_atomic64", manifest.descriptor_surfaces[0].module_name);
    try std.testing.expectEqualStrings("samples/trace_events/trace-events-sample.c", manifest.descriptor_surfaces[3].anchor);
    try std.testing.expectEqualStrings("module_name", manifest.shared_runtime_loader_metadata_fields[0]);
    try std.testing.expectEqualStrings("allocator_handoff", manifest.shared_runtime_loader_metadata_fields[8]);
    try std.testing.expectEqualStrings("samples/zigux/runtime_kretprobe_loader.zig", manifest.runtime_loader_plans[2]);
    try std.testing.expectEqualStrings("samples/zigux/runtime_trace_events_loader.zig", manifest.runtime_loader_plans[3]);
    try std.testing.expectEqualStrings("MODULE_INFO()", manifest.depmod_gap_surfaces[0]);
    try std.testing.expectEqualStrings("scripts/depmod.sh", manifest.depmod_gap_surfaces[7]);

    var saw_survey_note = false;
    var saw_manifest = false;
    var saw_survey_gate = false;
    var saw_packet_checker = false;
    var saw_phase9_build_gate = false;
    var saw_tests_readme_guide = false;
    var saw_runtime_loader_contract = false;
    var saw_trace_events_loader_plan = false;
    for (manifest.delivery_evidence_catalog, 0..) |entry, i| {
        try std.testing.expect(entry.id.len > 0);
        try std.testing.expect(entry.kind.len > 0);
        try std.testing.expect(entry.path.len > 0);
        try std.testing.expect(entry.role.len > 0);

        if (std.mem.eql(u8, entry.id, "runtime-module-metadata-survey-note")) {
            saw_survey_note = true;
            try std.testing.expectEqualStrings("documentation", entry.kind);
            try std.testing.expectEqualStrings("Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md", entry.path);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "written survey") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "depmod-facing metadata") != null);
        }
        if (std.mem.eql(u8, entry.id, "runtime-module-metadata-manifest")) {
            saw_manifest = true;
            try std.testing.expectEqualStrings("manifest", entry.kind);
            try std.testing.expectEqualStrings("zigux/tests/runtime_module_metadata_manifest.json", entry.path);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "machine-readable counts") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "depmod-gap catalog") != null);
        }
        if (std.mem.eql(u8, entry.id, "runtime-module-metadata-survey-gate")) {
            saw_survey_gate = true;
            try std.testing.expectEqualStrings("validation", entry.kind);
            try std.testing.expectEqualStrings("zigux/tests/runtime_module_metadata_survey.zig", entry.path);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "focused replay") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "RuntimeLoadRequest metadata") != null);
        }
        if (std.mem.eql(u8, entry.id, "runtime-module-metadata-packet-checker")) {
            saw_packet_checker = true;
            try std.testing.expectEqualStrings("validation", entry.kind);
            try std.testing.expectEqualStrings("scripts/zigux/check-phase9-module-metadata-packet.py", entry.path);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "fail-closed checker") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "shared Phase 9 bundle replay entrypoint") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "tests-root guidance") != null);
        }
        if (std.mem.eql(u8, entry.id, "phase9-build-gate")) {
            saw_phase9_build_gate = true;
            try std.testing.expectEqualStrings("validation", entry.kind);
            try std.testing.expectEqualStrings("zigux/tests/phase9_build.zig", entry.path);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "shared Phase 9 runtime bundle replay entrypoint") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "dedicated metadata survey") != null);
        }
        if (std.mem.eql(u8, entry.id, "phase9-tests-readme-guide")) {
            saw_tests_readme_guide = true;
            try std.testing.expectEqualStrings("documentation", entry.kind);
            try std.testing.expectEqualStrings("zigux/tests/README.md", entry.path);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "tests-root guidance") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "dedicated metadata checker") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "broader Phase 9 runtime packet") != null);
        }
        if (std.mem.eql(u8, entry.id, "shared-runtime-loader-contract")) {
            saw_runtime_loader_contract = true;
            try std.testing.expectEqualStrings("runtime_substrate", entry.kind);
            try std.testing.expectEqualStrings("zigux/kernel/runtime_loader.zig", entry.path);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "RuntimeLoadRequest metadata fields") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "three-lane loader union") != null);
        }
        if (std.mem.eql(u8, entry.id, "runtime-trace-events-loader-plan")) {
            saw_trace_events_loader_plan = true;
            try std.testing.expectEqualStrings("runtime_loader_scaffold", entry.kind);
            try std.testing.expectEqualStrings("samples/zigux/runtime_trace_events_loader.zig", entry.path);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "trace-events loader-side scaffold") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.role, "shared RuntimeLoadRequest union still stops at atomic64, bitmap, and kretprobe") != null);
        }

        for (manifest.delivery_evidence_catalog[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, entry.id, other.id));
            try std.testing.expect(!std.mem.eql(u8, entry.path, other.path));
        }
    }
    try std.testing.expect(saw_survey_note);
    try std.testing.expect(saw_manifest);
    try std.testing.expect(saw_survey_gate);
    try std.testing.expect(saw_packet_checker);
    try std.testing.expect(saw_phase9_build_gate);
    try std.testing.expect(saw_tests_readme_guide);
    try std.testing.expect(saw_runtime_loader_contract);
    try std.testing.expect(saw_trace_events_loader_plan);

    var saw_survey_note_ownership = false;
    var saw_manifest_ownership = false;
    var saw_survey_gate_ownership = false;
    var saw_packet_checker_ownership = false;
    var saw_phase9_build_ownership = false;
    var saw_tests_readme_ownership = false;
    var saw_runtime_loader_ownership = false;
    var saw_trace_events_loader_ownership = false;
    for (manifest.ownership_map, 0..) |entry, i| {
        try std.testing.expect(entry.surface.len > 0);
        try std.testing.expect(entry.owns.len > 0);

        if (std.mem.eql(u8, entry.surface, "Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md")) {
            saw_survey_note_ownership = true;
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "written survey") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "depmod-facing gap") != null);
        }
        if (std.mem.eql(u8, entry.surface, "zigux/tests/runtime_module_metadata_manifest.json")) {
            saw_manifest_ownership = true;
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "machine-readable counts") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "depmod-gap catalog") != null);
        }
        if (std.mem.eql(u8, entry.surface, "zigux/tests/runtime_module_metadata_survey.zig")) {
            saw_survey_gate_ownership = true;
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "focused replay") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "RuntimeLoadRequest metadata") != null);
        }
        if (std.mem.eql(u8, entry.surface, "scripts/zigux/check-phase9-module-metadata-packet.py")) {
            saw_packet_checker_ownership = true;
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "fail-closed checker") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "shared Phase 9 bundle replay entrypoint") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "tests-root guidance") != null);
        }
        if (std.mem.eql(u8, entry.surface, "zigux/tests/phase9_build.zig")) {
            saw_phase9_build_ownership = true;
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "shared Phase 9 runtime bundle replay entrypoint") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "dedicated metadata survey") != null);
        }
        if (std.mem.eql(u8, entry.surface, "zigux/tests/README.md")) {
            saw_tests_readme_ownership = true;
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "tests-root guidance") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "dedicated metadata checker") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "broader Phase 9 runtime packet") != null);
        }
        if (std.mem.eql(u8, entry.surface, "zigux/kernel/runtime_loader.zig")) {
            saw_runtime_loader_ownership = true;
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "RuntimeLoadRequest metadata fields") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "three-lane loader union") != null);
        }
        if (std.mem.eql(u8, entry.surface, "samples/zigux/runtime_trace_events_loader.zig")) {
            saw_trace_events_loader_ownership = true;
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "trace-events loader-side scaffold") != null);
            try std.testing.expect(std.mem.indexOf(u8, entry.owns, "fourth lane") != null);
        }

        for (manifest.ownership_map[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, entry.surface, other.surface));
        }
    }
    try std.testing.expect(saw_survey_note_ownership);
    try std.testing.expect(saw_manifest_ownership);
    try std.testing.expect(saw_survey_gate_ownership);
    try std.testing.expect(saw_packet_checker_ownership);
    try std.testing.expect(saw_phase9_build_ownership);
    try std.testing.expect(saw_tests_readme_ownership);
    try std.testing.expect(saw_runtime_loader_ownership);
    try std.testing.expect(saw_trace_events_loader_ownership);
}

test "runtime module metadata docs stay aligned with the manifest-backed surveyed commit" {
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

    const survey_note = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md",
        24 * 1024,
    );
    defer std.testing.allocator.free(survey_note);

    try expectContainsAll(survey_note, &.{
        "`PHASE9_SLICE=runtime-module-metadata-depmod-bridge-survey`",
        "ModuleDescriptor",
        "RuntimeLoadRequest",
        "samples/zigux/runtime_trace_events_loader.zig",
        "MODULE_INFO()",
        "scripts/depmod.sh",
        "it is not yet loadable-module metadata parity",
        "the shared runtime loader currently exposes three tagged loader lanes: `atomic64`, `bitmap`, and `kretprobe`",
        "four landed loader-plan files now stay at `samples/zigux/runtime_atomic64_loader.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_kretprobe_loader.zig`, and `samples/zigux/runtime_trace_events_loader.zig`",
        "the first three landed loader-plan files currently project `command_name = null` into `RuntimeLoadRequest`, so the optional command-name field is still reserved for a future shared activation surface rather than exercised by the shipped starter packet",
        "The dedicated `samples/zigux/runtime_trace_events_loader.zig` scaffold is now landed too, but it still stops outside that shared `RuntimeLoadRequest` union",
    });
    try expectSurveyedCommitMarker(survey_note, manifest.surveyed_commit);
    try expectPinnedCommitSentence(survey_note, manifest.surveyed_commit);
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

    try expectContainsAll(survey_note, &.{
        "PHASE9_SLICE=runtime-module-metadata-depmod-bridge-survey",
        "PHASE9_SURVEYED_COMMIT=949994db4046ec70abf044d1b2ea874fde9bc4a6",
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
        "scripts/zigux/check-phase9-module-metadata-packet.py",
        "zigux/tests/phase9_build.zig",
        "zigux/tests/README.md",
        "fail-closed checker",
        "shared Phase 9 runtime bundle replay entrypoint",
        "tests-root guidance",
        "loadable-module metadata parity",
        "depmod bridge",
        "the first three landed loader-plan files currently project `command_name = null` into `RuntimeLoadRequest`",
        "python3 scripts/zigux/validate-phase9.py --self-test",
        "python3 scripts/zigux/check-phase9-module-metadata-packet.py --self-test",
        "python3 scripts/zigux/validate-phase9.py",
        "python3 scripts/zigux/check-phase9-module-metadata-packet.py",
        "make -C zigux phase9-validate",
        "zig build test --build-file zigux/tests/phase9_build.zig --summary all",
        "zig test zigux/tests/runtime_module_metadata_survey.zig",
        "make -C zigux phase9-module-metadata-survey",
        "The dedicated `samples/zigux/runtime_trace_events_loader.zig` scaffold is now landed too, but it still stops outside that shared `RuntimeLoadRequest` union",
    });
}

test "runtime module metadata survey keeps the shared phase9 validator route explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const validate_phase9 = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "scripts/zigux/validate-phase9.py",
        64 * 1024,
    );
    defer std.testing.allocator.free(validate_phase9);

    try expectContainsAll(validate_phase9, &.{
        "Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md",
        "zigux/tests/runtime_module_metadata_manifest.json",
        "zigux/tests/runtime_module_metadata_survey.zig",
        "scripts/zigux/check-phase9-module-metadata-packet.py",
        "phase9-runtime-module-metadata-survey-tests",
    });
}

test "runtime module metadata survey proves the landed loader-plan scaffolds stay explicit and the shared metadata boundary stays narrow" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const runtime_atomic64_loader = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "samples/zigux/runtime_atomic64_loader.zig",
        48 * 1024,
    );
    defer std.testing.allocator.free(runtime_atomic64_loader);

    const runtime_bitmap_loader = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "samples/zigux/runtime_bitmap_loader.zig",
        48 * 1024,
    );
    defer std.testing.allocator.free(runtime_bitmap_loader);

    const runtime_kretprobe_loader = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "samples/zigux/runtime_kretprobe_loader.zig",
        48 * 1024,
    );
    defer std.testing.allocator.free(runtime_kretprobe_loader);

    const runtime_trace_events_loader = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "samples/zigux/runtime_trace_events_loader.zig",
        48 * 1024,
    );
    defer std.testing.allocator.free(runtime_trace_events_loader);

    try expectContainsAll(runtime_atomic64_loader, &.{
        "pub const RuntimeAtomic64LoadPlan = struct",
        "pub fn toSharedRequest(plan: RuntimeAtomic64LoadPlan) runtime_loader.RuntimeLoadRequest",
        "return planForWithCommandName(module, null);",
        "\"zigux_runtime_atomic64_init\"",
        "\"zigux_runtime_atomic64_exit\"",
        "try std.testing.expectEqual(@as(?[]const u8, null), plan.command_name);",
        "try std.testing.expectEqual(@as(?[]const u8, null), request.command_name);",
        ".waitingOnRuntimeSubstrate();",
        "releasedWithoutSubstrate();",
        "\"perf-runtime-atomic64\"",
    });
    try expectContainsAll(runtime_bitmap_loader, &.{
        "pub const RuntimeBitmapLoadPlan = struct",
        "pub fn toSharedRequest(plan: RuntimeBitmapLoadPlan) runtime_loader.RuntimeLoadRequest",
        "return planForWithCommandName(module, null);",
        "\"zigux_runtime_bitmap_init\"",
        "\"zigux_runtime_bitmap_exit\"",
        "try std.testing.expectEqual(@as(?[]const u8, null), plan.command_name);",
        "try std.testing.expectEqual(@as(?[]const u8, null), request.command_name);",
        ".waitingOnRuntimeSubstrate();",
        "releasedWithoutSubstrate();",
        "\"perf-runtime-bitmap\"",
    });
    try expectContainsAll(runtime_kretprobe_loader, &.{
        "pub const RuntimeKretprobeLoadPlan = struct",
        "pub fn toSharedRequest(plan: RuntimeKretprobeLoadPlan) runtime_loader.RuntimeLoadRequest",
        "return planForWithCommandName(module, null);",
        "\"register_kretprobe\"",
        "\"unregister_kretprobe\"",
        "\"zigux_runtime_kretprobe_init\"",
        "\"zigux_runtime_kretprobe_exit\"",
        "try std.testing.expectEqual(@as(?[]const u8, null), plan.command_name);",
        "try std.testing.expectEqual(@as(?[]const u8, null), request.command_name);",
        ".waitingOnRuntimeSubstrate();",
        "releasedWithoutSubstrate();",
        "\"perf-runtime-kretprobe\"",
    });
    try expectContainsAll(runtime_trace_events_loader, &.{
        "const runtime_loader = @import(\"runtime_loader\");",
        "pub const LoaderStage = runtime_loader.LoaderStage;",
        "pub const RuntimeTraceEventsLoadPlan = struct",
        "register_api",
        "unregister_api",
        "main_thread_label",
        "function_thread_label",
        "pub fn requestRuntimeLoad",
        "pub fn releaseWithoutSubstrate",
        "\"zigux_runtime_trace_events_init\"",
        "\"zigux_runtime_trace_events_exit\"",
        "\"foo_bar_reg\"",
        "\"foo_bar_unreg\"",
    });
    try std.testing.expect(std.mem.indexOf(u8, runtime_trace_events_loader, "RuntimeLoadRequest") == null);

    for ([_][]const u8{ runtime_atomic64_loader, runtime_bitmap_loader, runtime_kretprobe_loader, runtime_trace_events_loader }) |loader_text| {
        try std.testing.expect(std.mem.indexOf(u8, loader_text, "MODULE_INFO(") == null);
        try std.testing.expect(std.mem.indexOf(u8, loader_text, "MODULE_ALIAS(") == null);
        try std.testing.expect(std.mem.indexOf(u8, loader_text, ".modinfo") == null);
        try std.testing.expect(std.mem.indexOf(u8, loader_text, "modules.alias") == null);
        try std.testing.expect(std.mem.indexOf(u8, loader_text, "scripts/depmod.sh") == null);
    }
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
