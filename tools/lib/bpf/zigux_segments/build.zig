const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const verify_module = b.createModule(.{
        .root_source_file = b.path("verify.zig"),
        .target = target,
        .optimize = optimize,
    });

    const verify_tests = b.addTest(.{
        .root_module = verify_module,
    });

    const run_verify_tests = b.addRunArtifact(verify_tests);

    const verify_step = b.step(
        "segments-verify",
        "Run focused tests for tools/lib/bpf/zigux_segments",
    );
    verify_step.dependOn(&run_verify_tests.step);

    const test_step = b.step(
        "test",
        "Alias for the focused zigux_segments verification route",
    );
    test_step.dependOn(&run_verify_tests.step);

    b.default_step = test_step;
}
