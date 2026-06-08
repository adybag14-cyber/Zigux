const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("conf_bridge_wrong_mode_option_cli_surface_test.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);
    run_tests.setCwd(b.path("../../.."));

    const named_step = b.step(
        "lane20-conf-bridge-wrong-mode-option-cli-surface",
        "Run Lane 20 conf_bridge wrong-mode bridge option CLI proof",
    );
    named_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run tests");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
