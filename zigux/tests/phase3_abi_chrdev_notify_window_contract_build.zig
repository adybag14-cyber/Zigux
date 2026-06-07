const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const contract_path = b.option(
        []const u8,
        "contract-path",
        "Path to the chrdev notify-window ABI contract source",
    ) orelse "phase3_abi_chrdev_notify_window_contract.zig";
    const abi_bindings_path = b.option(
        []const u8,
        "abi-bindings-path",
        "Path to zigux/bindings/abi.zig",
    ) orelse "../bindings/abi.zig";

    const contract_module = b.createModule(.{
        .root_source_file = b.path(contract_path),
        .target = target,
        .optimize = optimize,
    });
    contract_module.addImport("abi_bindings", b.createModule(.{
        .root_source_file = b.path(abi_bindings_path),
        .target = target,
        .optimize = optimize,
    }));

    const contract_tests = b.addTest(.{
        .root_module = contract_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "phase3-abi-chrdev-notify-window-contract",
        "Run the Phase 3 ABI chrdev notify-window contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Phase 3 ABI chrdev notify-window contract");
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(&run_contract_tests.step);
}
