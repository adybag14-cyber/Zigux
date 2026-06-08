const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("conf_bridge_savedefconfig_mode_arg_with_options_cli_surface_test.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);
    run_tests.setCwd(b.path("../../.."));

    const proof_step = b.step(
        "lane20-conf-bridge-savedefconfig-mode-arg-options-cli-surface",
        "Run the Lane 20 conf_bridge savedefconfig mode-arg options CLI proof",
    );
    proof_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run all tests");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
