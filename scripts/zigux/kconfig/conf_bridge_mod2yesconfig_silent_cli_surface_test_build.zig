const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("conf_bridge_mod2yesconfig_silent_cli_surface_test.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .name = "lane20-conf-bridge-mod2yesconfig-silent-cli-surface-tests",
        .root_module = root_module,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);
    run_unit_tests.setCwd(b.path("../../.."));

    const test_step = b.step(
        "lane20-conf-bridge-mod2yesconfig-silent-cli-surface",
        "Run the Lane 20 conf_bridge mod2yesconfig silent CLI surface proof",
    );
    test_step.dependOn(&run_unit_tests.step);

    const run_tests = b.step("test", "Run the Lane 20 conf_bridge mod2yesconfig silent CLI surface proof");
    run_tests.dependOn(&run_unit_tests.step);

    b.default_step.dependOn(&run_unit_tests.step);
}
