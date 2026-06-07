const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const abi_bindings_path = b.option(
        []const u8,
        "abi-bindings-path",
        "Path to zigux/bindings/abi.zig",
    ) orelse "../bindings/abi.zig";

    const abi_bindings = b.createModule(.{
        .root_source_file = b.path(abi_bindings_path),
        .target = target,
        .optimize = optimize,
    });
    const contract = b.createModule(.{
        .root_source_file = b.path("phase3_abi_chrdev_notify_delivery_window_budget_window_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    contract.addImport("abi_bindings", abi_bindings);

    const unit_tests = b.addTest(.{
        .root_module = contract,
    });
    const run_tests = b.addRunArtifact(unit_tests);

    const contract_step = b.step(
        "phase3-abi-chrdev-notify-delivery-window-budget-window-contract",
        "Run the Phase 3 chrdev notify delivery-window budget-window ABI contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run unit tests");
    test_step.dependOn(&run_tests.step);
    b.default_step.dependOn(&run_tests.step);
}
