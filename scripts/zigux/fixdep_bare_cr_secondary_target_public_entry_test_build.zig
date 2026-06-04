const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("fixdep_bare_cr_secondary_target_public_entry_test.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const route = b.step(
        "fixdep-bare-cr-secondary-target-public-entry",
        "Run the fixdep bare-CR secondary-target public-entry proof",
    );
    route.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the fixdep bare-CR secondary-target public-entry proof");
    test_step.dependOn(&run_tests.step);
}
