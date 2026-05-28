const std = @import("std");
const sample = @import("runtime_kretprobe_sample");

fn readRepoFileAlloc(path: []const u8, max_bytes: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        std.testing.allocator,
        .limited(max_bytes),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectSnapshotStable(
    before: sample.LifecycleSnapshot,
    after: sample.LifecycleSnapshot,
) !void {
    try std.testing.expectEqual(before.stage, after.stage);
    try std.testing.expectEqual(before.init_runs, after.init_runs);
    try std.testing.expectEqual(before.selftest_runs, after.selftest_runs);
    try std.testing.expectEqual(before.exit_runs, after.exit_runs);
    try std.testing.expectEqual(before.registration_runs, after.registration_runs);
    try std.testing.expectEqual(before.unregistration_runs, after.unregistration_runs);
    try std.testing.expectEqual(before.probe_registered, after.probe_registered);
    try std.testing.expectEqual(before.active_instances, after.active_instances);
    try std.testing.expectEqual(before.completed_instances, after.completed_instances);
    try std.testing.expectEqual(before.last_retval, after.last_retval);
}

test "phase9 runtime kretprobe survey gate matches the roadmap-backed sample and module packet" {
    const descriptor = sample.RuntimeKretprobeSample.descriptor();
    try std.testing.expectEqualStrings("runtime_kretprobe", descriptor.name);
    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", descriptor.anchor);
    try std.testing.expect(descriptor.requires_runtime_substrate);
    try std.testing.expect(descriptor.provides_selftest_hook);

    var runtime_module = sample.RuntimeKretprobeSample{};
    try runtime_module.init();
    const selftest_summary = try runtime_module.runSelftest();
    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", selftest_summary.anchor);
    try std.testing.expect(selftest_summary.checked_registration_paths);
    try std.testing.expect(selftest_summary.checked_return_paths);
    try std.testing.expect(selftest_summary.checked_lifecycle_guards);
    try runtime_module.exit();

    const sample_file = try readRepoFileAlloc("samples/zigux/runtime_kretprobe.zig", 64 * 1024);
    defer std.testing.allocator.free(sample_file);
    const loader_file = try readRepoFileAlloc("samples/zigux/runtime_kretprobe_loader.zig", 64 * 1024);
    defer std.testing.allocator.free(loader_file);
    const module_file = try readRepoFileAlloc("zigux/tests/runtime_kretprobe_module.zig", 64 * 1024);
    defer std.testing.allocator.free(module_file);
    const manifest_file = try readRepoFileAlloc("zigux/tests/runtime_kretprobe_manifest.json", 16 * 1024);
    defer std.testing.allocator.free(manifest_file);
    const initialized_guard_file = try readRepoFileAlloc(
        "samples/zigux/runtime_kretprobe_initialized_snapshot_guard.zig",
        16 * 1024,
    );
    defer std.testing.allocator.free(initialized_guard_file);
    const registration_reentry_guard_file = try readRepoFileAlloc(
        "samples/zigux/runtime_kretprobe_registration_reentry_gate.zig",
        16 * 1024,
    );
    defer std.testing.allocator.free(registration_reentry_guard_file);
    const reinit_reexit_guard_file = try readRepoFileAlloc(
        "samples/zigux/runtime_kretprobe_reinit_reexit_guard.zig",
        16 * 1024,
    );
    defer std.testing.allocator.free(reinit_reexit_guard_file);
    const parity_behavior_file = try readRepoFileAlloc(
        "zigux/tests/runtime_first_loadable_parity_behavior.zig",
        64 * 1024,
    );
    defer std.testing.allocator.free(parity_behavior_file);
    const phase9_build = try readRepoFileAlloc("zigux/tests/phase9_build.zig", 64 * 1024);
    defer std.testing.allocator.free(phase9_build);

    try expectContains(sample_file, ".requires_runtime_substrate = true");
    try expectContains(sample_file, ".provides_selftest_hook = true");
    try expectContains(sample_file, "pub const ModuleStage = enum(u8)");
    try expectContains(sample_file, "selftest_complete");
    try expectContains(sample_file, "pub fn runSelftest");
    try expectContains(sample_file, "pub fn exit");

    try expectContains(loader_file, "pub const LoaderStage = enum(u8)");
    try expectContains(loader_file, "pub const RuntimeKretprobeLoader = struct");
    try expectContains(loader_file, "pub fn requestSharedRuntimeLoad(");
    try expectContains(loader_file, "pub fn releaseSharedWithoutSubstrate(");
    try expectContains(loader_file, "released_without_substrate");
    try expectContains(loader_file, "waiting_on_runtime_substrate");
    try expectContains(loader_file, "error.InvalidLoaderState");
    try expectContains(
        loader_file,
        "runtime kretprobe loader keeps initialized-stage shared contract plans explicit",
    );
    try expectContains(
        loader_file,
        "runtime kretprobe loader keeps initialized shared-request snapshots stable across later selftest activity",
    );
    try expectContains(
        loader_file,
        "runtime kretprobe loader keeps initialized reusable probe cycles from drifting shared-request plans before selftest",
    );
    try expectContains(
        loader_file,
        "runtime kretprobe loader keeps post-selftest reusable probe cycles from disturbing the blocked shared-request path",
    );
    try expectContains(
        loader_file,
        "runtime kretprobe loader keeps invalid loader transitions fail-closed without disturbing shared-request snapshots",
    );
    try expectContains(
        loader_file,
        "runtime kretprobe loader keeps selftest-complete shared requests blocked by the current loader family contract",
    );
    try expectContains(
        loader_file,
        "runtime kretprobe loader rejects cold and exited sample stages before preparing a shared request",
    );

    try expectContains(
        module_file,
        "runtime kretprobe sample keeps selftest summary replay explicit at the module boundary",
    );
    try expectContains(
        module_file,
        "runtime kretprobe sample keeps lifecycle snapshot replay explicit at the module boundary",
    );
    try expectContains(
        module_file,
        "runtime kretprobe sample keeps initialized-stage exit replay explicit at the module boundary",
    );
    try expectContains(
        module_file,
        "runtime kretprobe sample keeps rejected re-selftest rollback explicit at the module boundary",
    );
    try expectContains(
        module_file,
        "runtime kretprobe sample keeps duplicate registration and failed exit rollback explicit at the module boundary",
    );

    try expectContains(manifest_file, "\"phase\": \"Phase 9\"");
    try expectContains(manifest_file, "\"lane_key\": \"runtime-pilot\"");
    try expectContains(manifest_file, "\"status\": \"active\"");
    try expectContains(
        manifest_file,
        "\"sample_path\": \"samples/zigux/runtime_kretprobe.zig\"",
    );
    try expectContains(
        manifest_file,
        "\"loader_path\": \"samples/zigux/runtime_kretprobe_loader.zig\"",
    );
    try expectContains(
        manifest_file,
        "\"initialized_snapshot_guard_path\": \"samples/zigux/runtime_kretprobe_initialized_snapshot_guard.zig\"",
    );
    try expectContains(
        manifest_file,
        "\"registration_reentry_guard_path\": \"samples/zigux/runtime_kretprobe_registration_reentry_gate.zig\"",
    );
    try expectContains(
        manifest_file,
        "\"reinit_reexit_guard_path\": \"samples/zigux/runtime_kretprobe_reinit_reexit_guard.zig\"",
    );
    try expectContains(
        manifest_file,
        "\"module_path\": \"zigux/tests/runtime_kretprobe_module.zig\"",
    );
    try expectContains(
        manifest_file,
        "\"survey_path\": \"zigux/tests/runtime_kretprobe_survey.zig\"",
    );
    try expectContains(
        manifest_file,
        "\"parity_survey_path\": \"zigux/tests/runtime_first_loadable_parity_survey.zig\"",
    );
    try expectContains(
        manifest_file,
        "\"parity_behavior_path\": \"zigux/tests/runtime_first_loadable_parity_behavior.zig\"",
    );
    try expectContains(manifest_file, "\"build_path\": \"zigux/tests/phase9_build.zig\"");
    try expectContains(manifest_file, "\"validation_entrypoint\": \"phase9-runtime-kretprobe-tests\"");
    try expectContains(
        manifest_file,
        "bounded runtime kretprobe pilot packet, direct sample proof, direct loader proof",
    );
    try expectContains(
        manifest_file,
        "Keep the direct sample, loader, initialized-snapshot guard, registration-reentry guard, paired reinit-reexit rollback guard, module witness, and survey gate aligned before widening any shared reminder surface.",
    );

    try expectContains(
        initialized_guard_file,
        "phase9 kretprobe sample keeps captured initialized snapshot replay explicit across later selftest and exit",
    );
    try expectContains(
        registration_reentry_guard_file,
        "runtime kretprobe registration reentry stays reusable before selftest",
    );
    try expectContains(
        registration_reentry_guard_file,
        "runtime kretprobe registration reentry stays reusable after selftest",
    );
    try expectContains(
        registration_reentry_guard_file,
        "runtime kretprobe registration reentry stays fail-closed after exit",
    );
    try expectContains(
        reinit_reexit_guard_file,
        "phase9 kretprobe sample keeps paired rejected re-init and re-exit rollback explicit after initialized direct activity",
    );
    try expectContains(
        reinit_reexit_guard_file,
        "phase9 kretprobe sample keeps paired rejected re-init and re-exit rollback explicit after selftest-ready replay",
    );

    try expectContains(
        parity_behavior_file,
        "first-loadable runtime pilot families keep descriptor parity explicit",
    );
    try expectContains(
        parity_behavior_file,
        "first-loadable runtime pilot families keep init selftest and exit counts aligned",
    );
    try expectContains(
        parity_behavior_file,
        "first-loadable runtime pilot families keep direct exit parity explicit before selftest",
    );
    try expectContains(
        parity_behavior_file,
        "first-loadable runtime pilot families keep post-selftest mutation parity explicit",
    );
    try expectContains(parity_behavior_file, "runtime_kretprobe");
    try expectContains(parity_behavior_file, "samples/kprobes/kretprobe_example.c");

    try expectContains(phase9_build, "\"phase9-runtime-kretprobe-sample-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-kretprobe-loader-tests\"");
    try expectContains(
        phase9_build,
        "\"phase9-runtime-kretprobe-initialized-snapshot-guard-tests\"",
    );
    try expectContains(
        phase9_build,
        "\"phase9-runtime-kretprobe-registration-reentry-gate-tests\"",
    );
    try expectContains(
        phase9_build,
        "\"phase9-runtime-kretprobe-reinit-reexit-guard-tests\"",
    );
    try expectContains(phase9_build, "\"phase9-runtime-kretprobe-survey-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-kretprobe-module-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-kretprobe-tests\"");
    try expectContains(
        phase9_build,
        "Run the Phase 9 runtime kretprobe paired re-init and re-exit rollback guard tests.",
    );
    try expectContains(
        phase9_build,
        "Run the Phase 9 runtime kretprobe sample, loader, initialized-snapshot guard, registration-reentry gate, reinit-reexit guard, survey, and module lifecycle tests.",
    );
    try expectContains(
        phase9_build,
        "\"phase9-first-loadable-runtime-module-parity-behavior-tests\"",
    );
    try expectContains(
        phase9_build,
        "Run the Phase 9 first-loadable runtime-module parity behavior tests.",
    );
}

test "phase9 runtime kretprobe survey keeps captured initialized snapshot replay explicit across later selftest and exit" {
    var module = sample.RuntimeKretprobeSample{};
    try module.init();

    const initialized_snapshot = module.lifecycleSnapshot();
    try std.testing.expectEqual(sample.ModuleStage.initialized, initialized_snapshot.stage);
    try std.testing.expectEqual(@as(usize, 1), initialized_snapshot.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_snapshot.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_snapshot.exit_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_snapshot.registration_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_snapshot.unregistration_runs);
    try std.testing.expect(!initialized_snapshot.probe_registered);
    try std.testing.expectEqual(@as(usize, 0), initialized_snapshot.active_instances);
    try std.testing.expectEqual(@as(usize, 0), initialized_snapshot.completed_instances);
    try std.testing.expectEqual(@as(?i32, null), initialized_snapshot.last_retval);

    _ = try module.runSelftest();
    try module.exit();

    const exited_snapshot = module.lifecycleSnapshot();
    try std.testing.expectEqual(sample.ModuleStage.exited, module.stage());
    try expectSnapshotStable(initialized_snapshot, .{
        .stage = initialized_snapshot.stage,
        .init_runs = initialized_snapshot.init_runs,
        .selftest_runs = initialized_snapshot.selftest_runs,
        .exit_runs = initialized_snapshot.exit_runs,
        .registration_runs = initialized_snapshot.registration_runs,
        .unregistration_runs = initialized_snapshot.unregistration_runs,
        .probe_registered = initialized_snapshot.probe_registered,
        .active_instances = initialized_snapshot.active_instances,
        .completed_instances = initialized_snapshot.completed_instances,
        .last_retval = initialized_snapshot.last_retval,
        .last_entry_timestamp_ns = initialized_snapshot.last_entry_timestamp_ns,
        .last_return_timestamp_ns = initialized_snapshot.last_return_timestamp_ns,
        .last_duration_ns = initialized_snapshot.last_duration_ns,
        .oldest_active_entry_timestamp_ns = initialized_snapshot.oldest_active_entry_timestamp_ns,
        .newest_active_entry_timestamp_ns = initialized_snapshot.newest_active_entry_timestamp_ns,
    });
    try std.testing.expectEqual(@as(usize, 1), exited_snapshot.init_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_snapshot.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_snapshot.exit_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_snapshot.registration_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_snapshot.unregistration_runs);
    try std.testing.expect(!exited_snapshot.probe_registered);
    try std.testing.expectEqual(@as(usize, 0), exited_snapshot.active_instances);
    try std.testing.expectEqual(@as(usize, 1), exited_snapshot.completed_instances);
    try std.testing.expectEqual(@as(?i32, 0), exited_snapshot.last_retval);
}

test "phase9 runtime kretprobe survey keeps captured initialized direct-activity snapshot replay explicit across later selftest and exit" {
    var module = sample.RuntimeKretprobeSample{};
    try module.init();
    try module.registerProbe();
    try module.recordEntry();
    try module.recordReturn(13);
    try module.unregisterProbe();

    const initialized_snapshot = module.lifecycleSnapshot();
    try std.testing.expectEqual(sample.ModuleStage.initialized, initialized_snapshot.stage);
    try std.testing.expectEqual(@as(usize, 1), initialized_snapshot.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_snapshot.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_snapshot.exit_runs);
    try std.testing.expectEqual(@as(usize, 1), initialized_snapshot.registration_runs);
    try std.testing.expectEqual(@as(usize, 1), initialized_snapshot.unregistration_runs);
    try std.testing.expect(!initialized_snapshot.probe_registered);
    try std.testing.expectEqual(@as(usize, 0), initialized_snapshot.active_instances);
    try std.testing.expectEqual(@as(usize, 1), initialized_snapshot.completed_instances);
    try std.testing.expectEqual(@as(?i32, 13), initialized_snapshot.last_retval);

    _ = try module.runSelftest();
    try module.exit();

    const exited_snapshot = module.lifecycleSnapshot();
    try std.testing.expectEqual(sample.ModuleStage.exited, module.stage());
    try std.testing.expectEqual(sample.ModuleStage.initialized, initialized_snapshot.stage);
    try std.testing.expectEqual(@as(usize, 1), initialized_snapshot.init_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_snapshot.selftest_runs);
    try std.testing.expectEqual(@as(usize, 0), initialized_snapshot.exit_runs);
    try std.testing.expectEqual(@as(usize, 1), initialized_snapshot.registration_runs);
    try std.testing.expectEqual(@as(usize, 1), initialized_snapshot.unregistration_runs);
    try std.testing.expect(!initialized_snapshot.probe_registered);
    try std.testing.expectEqual(@as(usize, 0), initialized_snapshot.active_instances);
    try std.testing.expectEqual(@as(usize, 1), initialized_snapshot.completed_instances);
    try std.testing.expectEqual(@as(?i32, 13), initialized_snapshot.last_retval);
    try std.testing.expectEqual(@as(usize, 1), exited_snapshot.init_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_snapshot.selftest_runs);
    try std.testing.expectEqual(@as(usize, 1), exited_snapshot.exit_runs);
    try std.testing.expectEqual(@as(usize, 2), exited_snapshot.registration_runs);
    try std.testing.expectEqual(@as(usize, 2), exited_snapshot.unregistration_runs);
    try std.testing.expect(!exited_snapshot.probe_registered);
    try std.testing.expectEqual(@as(usize, 0), exited_snapshot.active_instances);
    try std.testing.expectEqual(@as(usize, 2), exited_snapshot.completed_instances);
    try std.testing.expectEqual(@as(?i32, 0), exited_snapshot.last_retval);
}
