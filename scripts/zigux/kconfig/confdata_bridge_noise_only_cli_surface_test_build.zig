const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("confdata_bridge_noise_only_cli_surface_test.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);
    run_tests.setCwd(b.path("../../.."));

    const lane_step = b.step(
        "lane20-confdata-bridge-noise-only-cli-surface",
        "Run the Lane 20 confdata_bridge noise-only CLI surface proof",
    );
    lane_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 20 confdata_bridge noise-only CLI surface proof");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
