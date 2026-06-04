const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .name = "fixdep-multi-target-names-public-entry",
        .root_module = b.createModule(.{
            .root_source_file = b.path("fixdep_multi_target_names_public_entry_test.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);

    const named_step = b.step(
        "fixdep-multi-target-names-public-entry",
        "Run the fixdep multi-target-name public-entry proof",
    );
    named_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run fixdep multi-target-name public-entry tests");
    test_step.dependOn(&run_tests.step);
}
