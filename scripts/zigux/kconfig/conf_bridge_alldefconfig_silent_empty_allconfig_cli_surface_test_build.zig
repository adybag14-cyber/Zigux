const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const test_exe = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("conf_bridge_alldefconfig_silent_empty_allconfig_cli_surface_test.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(test_exe);
    run_tests.setCwd(b.path("../../.."));

    const named_step = b.step(
        "lane20-conf-bridge-alldefconfig-silent-empty-allconfig-cli-surface",
        "Run the Lane 20 alldefconfig silent empty-allconfig conf_bridge CLI proof",
    );
    named_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 20 alldefconfig silent empty-allconfig conf_bridge CLI proof");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
