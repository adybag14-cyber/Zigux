const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const test_module = b.createModule(.{
        .root_source_file = b.path("fixdep_target_only_public_entry_test.zig"),
        .target = target,
        .optimize = optimize,
    });

    const test_artifact = b.addTest(.{
        .root_module = test_module,
    });
    const run_tests = b.addRunArtifact(test_artifact);

    const named_step = b.step(
        "fixdep-target-only-public-entry",
        "Run the fixdep target-only public-entry proof",
    );
    named_step.dependOn(&run_tests.step);

    const default_step = b.step("test", "Run the fixdep target-only public-entry proof");
    default_step.dependOn(&run_tests.step);
}
