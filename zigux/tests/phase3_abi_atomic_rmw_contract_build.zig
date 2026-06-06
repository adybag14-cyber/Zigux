const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const atomic_path = b.option(
        []const u8,
        "atomic-path",
        "path to the Phase 3 atomic helper",
    ) orelse "../helpers/atomic.zig";

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase3_abi_atomic_rmw_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    tests.root_module.addImport("atomic_helpers", b.createModule(.{
        .root_source_file = b.path(atomic_path),
        .target = target,
        .optimize = optimize,
    }));

    const run_tests = b.addRunArtifact(tests);
    const contract_step = b.step(
        "phase3-abi-atomic-rmw-contract",
        "Run the Phase 3 atomic RMW ABI contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 3 atomic RMW ABI contract");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
