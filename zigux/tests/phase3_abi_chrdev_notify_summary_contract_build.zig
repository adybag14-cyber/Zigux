const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const abi_bindings_path = b.option([]const u8, "abi-bindings-path", "path to zigux/bindings/abi.zig") orelse "../bindings/abi.zig";

    const abi_bindings = b.createModule(.{
        .root_source_file = b.path(abi_bindings_path),
        .target = target,
        .optimize = optimize,
    });

    const test_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_chrdev_notify_summary_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    test_module.addImport("abi_bindings", abi_bindings);

    const contract_tests = b.addTest(.{
        .root_module = test_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const named_step = b.step("phase3-abi-chrdev-notify-summary-contract", "Run the Phase 3 chrdev notify summary ABI contract");
    named_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Phase 3 chrdev notify summary ABI contract");
    test_step.dependOn(&run_contract_tests.step);
    b.default_step.dependOn(&run_contract_tests.step);
}
