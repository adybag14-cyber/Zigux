const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("conf_bridge_syncconfig_env_order_surface_test.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "conf-bridge-syncconfig-env-order-surface-tests",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const route = b.step(
        "conf-bridge-syncconfig-env-order-surface",
        "Run the kconfig conf bridge syncconfig env ordering proof",
    );
    route.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the kconfig conf bridge syncconfig env ordering proof");
    test_step.dependOn(&run_tests.step);
}
