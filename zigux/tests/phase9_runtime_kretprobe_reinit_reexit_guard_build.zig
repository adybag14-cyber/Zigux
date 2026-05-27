const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const runtime_kretprobe_reinit_reexit_guard_module = b.createModule(.{
        .root_source_file = b.path("../../samples/zigux/runtime_kretprobe_reinit_reexit_guard.zig"),
        .target = target,
        .optimize = optimize,
    });

    const runtime_kretprobe_reinit_reexit_guard_tests = b.addTest(.{
        .name = "phase9-runtime-kretprobe-reinit-reexit-guard-tests",
        .root_module = runtime_kretprobe_reinit_reexit_guard_module,
    });

    const run_runtime_kretprobe_reinit_reexit_guard_tests = b.addRunArtifact(
        runtime_kretprobe_reinit_reexit_guard_tests,
    );

    const guard_step = b.step(
        "phase9-runtime-kretprobe-reinit-reexit-guard-tests",
        "Run the Phase 9 runtime kretprobe paired re-init and re-exit rollback guard tests.",
    );
    guard_step.dependOn(&run_runtime_kretprobe_reinit_reexit_guard_tests.step);

    const test_step = b.step(
        "test",
        "Run the Phase 9 runtime kretprobe paired re-init and re-exit rollback guard tests.",
    );
    test_step.dependOn(&run_runtime_kretprobe_reinit_reexit_guard_tests.step);
}
