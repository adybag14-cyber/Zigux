const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const uapi_dev_t = b.createModule(.{
        .root_source_file = b.path("../uapi/dev_t.zig"),
        .target = target,
        .optimize = optimize,
    });

    const dev_t_binding = b.createModule(.{
        .root_source_file = b.path("../bindings/dev_t.zig"),
        .target = target,
        .optimize = optimize,
    });
    dev_t_binding.addImport("uapi_dev_t", uapi_dev_t);

    const uapi_tests = b.addTest(.{
        .name = "phase3_uapi_dev_t_tests",
        .root_module = uapi_dev_t,
    });

    const binding_tests = b.addTest(.{
        .name = "phase3_dev_t_binding_tests",
        .root_module = dev_t_binding,
    });

    const run_uapi_tests = b.addRunArtifact(uapi_tests);
    const run_binding_tests = b.addRunArtifact(binding_tests);

    const test_step = b.step(
        "phase3-dev-t-pair-test",
        "Run the focused Phase 3 dev_t UAPI and binding pair replay.",
    );
    test_step.dependOn(&run_uapi_tests.step);
    test_step.dependOn(&run_binding_tests.step);
}
