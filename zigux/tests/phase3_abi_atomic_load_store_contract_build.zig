const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const atomic_helper_path = b.option(
        []const u8,
        "atomic-helper-path",
        "Path to the Phase 3 atomic helper under test",
    ) orelse "../helpers/atomic.zig";

    const atomic_helpers = b.createModule(.{
        .root_source_file = b.path(atomic_helper_path),
        .target = target,
        .optimize = optimize,
    });
    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_atomic_load_store_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("atomic_helpers", atomic_helpers);

    const tests = b.addTest(.{
        .name = "phase3-abi-atomic-load-store-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase3-abi-atomic-load-store-contract",
        "Run the Phase 3 atomic load/store ABI contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 3 atomic load/store ABI contract");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
