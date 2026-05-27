const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const uapi_dev_t = b.createModule(.{
        .root_source_file = b.path("../uapi/dev_t.zig"),
        .target = target,
        .optimize = optimize,
    });
    const root_module = b.createModule(.{
        .root_source_file = b.path("../bindings/dev_t.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("uapi_dev_t", uapi_dev_t);

    const unit_tests = b.addTest(.{
        .name = "phase3-dev-t-binding-test",
        .root_module = root_module,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);

    const test_step = b.step(
        "phase3-dev-t-binding-test",
        "Run the Phase 3 dev_t binding in isolation",
    );
    test_step.dependOn(&run_unit_tests.step);
}
