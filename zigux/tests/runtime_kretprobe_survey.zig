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
    try expectContains(
        sample_file,
        "try std.testing.expectEqualStrings(\"do_sys_openat2\", selftest.symbol_name);",
    );
    try expectContains(
        sample_file,
        "try std.testing.expectEqualStrings(\"do_sys_openat2\", exit_report.symbol_name);",
    );

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
    try expectContains(
        module_file,
        "try std.testing.expectEqualStrings(\"do_sys_openat2\", initialized.symbol_name);",
    );
    try expectContains(
        module_file,
        "try std.testing.expectEqualStrings(\"do_sys_openat2\", selftest_summary.symbol_name);",
    );
    try expectContains(
        module_file,
        "try std.testing.expectEqualStrings(\"do_sys_openat2\", before_exit.symbol_name);",
    );
    try expectContains(
        module_file,
        "try std.testing.expectEqualStrings(\"do_sys_openat2\", exit_report.symbol_name);",
    );
    try expectContains(
        module_file,
        "try std.testing.expectEqualStrings(\"do_sys_openat2\", after_exit.symbol_name);",
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
    try expectContains(phase9_build, "\"phase9-runtime-kretprobe-survey-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-kretprobe-module-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-kretprobe-tests\"");
    try expectContains(
        phase9_build,
        "\"phase9-first-loadable-runtime-module-parity-behavior-tests\"",
    );
    try expectContains(
        phase9_build,
        "Run the Phase 9 runtime kretprobe loader handoff and blocked shared-request tests.",
    );
    try expectContains(
        phase9_build,
        "Run the Phase 9 runtime kretprobe sample, loader, initialized-snapshot guard, registration-reentry gate, survey, and module lifecycle tests.",
    );
    try expectContains(
        phase9_build,
        "Run the Phase 9 first-loadable runtime-module parity behavior tests.",
    );
}
