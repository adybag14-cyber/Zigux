const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const atomic_path = b.option(
        []const u8,
        "atomic-helper-path",
        "Path to zigux/helpers/atomic.zig",
    ) orelse "../helpers/atomic.zig";

    const atomic_helpers = b.createModule(.{
        .root_source_file = b.path(atomic_path),
        .target = target,
        .optimize = optimize,
    });

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_atomic_extrema_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("atomic_helpers", atomic_helpers);

    const tests = b.addTest(.{
        .name = "phase3-abi-atomic-extrema-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase3-abi-atomic-extrema-contract",
        "Run the Phase 3 ABI atomic extrema contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 3 ABI atomic extrema contract");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
