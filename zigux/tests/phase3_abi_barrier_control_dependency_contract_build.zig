const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const barrier_helper_path = b.option(
        []const u8,
        "barrier-helper-path",
        "path to zigux/helpers/barrier.zig",
    ) orelse "../helpers/barrier.zig";

    const test_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_barrier_control_dependency_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    test_module.addImport("barrier_helper", b.createModule(.{
        .root_source_file = b.path(barrier_helper_path),
        .target = target,
        .optimize = optimize,
    }));

    const tests = b.addTest(.{
        .root_module = test_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const contract_step = b.step(
        "phase3-abi-barrier-control-dependency-contract",
        "Run the Phase 3 ABI barrier control-dependency contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 3 ABI barrier control-dependency contract");
    test_step.dependOn(&run_tests.step);
    b.default_step.dependOn(&run_tests.step);
}
