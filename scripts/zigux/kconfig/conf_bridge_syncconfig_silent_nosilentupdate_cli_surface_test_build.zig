const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const unit_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("conf_bridge_syncconfig_silent_nosilentupdate_cli_surface_test.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(unit_tests);
    run_tests.setCwd(b.path("../../.."));

    const test_step = b.step("test", "Run syncconfig silent nosilentupdate CLI surface tests");
    test_step.dependOn(&run_tests.step);

    const lane20_step = b.step(
        "lane20-conf-bridge-syncconfig-silent-nosilentupdate-cli-surface",
        "Run Lane 20 conf_bridge syncconfig silent nosilentupdate CLI surface proof",
    );
    lane20_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
