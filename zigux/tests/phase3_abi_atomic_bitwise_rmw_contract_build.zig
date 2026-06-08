const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const atomic_helper_path = b.option(
        []const u8,
        "atomic-helper-path",
        "Path to the Phase 3 atomic helper implementation.",
    ) orelse "../helpers/atomic.zig";

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase3_abi_atomic_bitwise_rmw_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    tests.root_module.addImport("atomic_helpers", b.createModule(.{
        .root_source_file = b.path(atomic_helper_path),
        .target = target,
        .optimize = optimize,
    }));

    const run_tests = b.addRunArtifact(tests);

    const named = b.step(
        "phase3-abi-atomic-bitwise-rmw-contract",
        "Run the Phase 3 ABI atomic bitwise RMW contract.",
    );
    named.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 3 ABI atomic bitwise RMW contract tests.");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
