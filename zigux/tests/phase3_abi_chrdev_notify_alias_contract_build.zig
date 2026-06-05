const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const chrdev_notify_abi = b.createModule(.{
        .root_source_file = b.path("../bindings/chrdev_notify_abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    chrdev_notify_abi.addImport("abi_bindings", abi_bindings);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_chrdev_notify_alias_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("abi_bindings", abi_bindings);
    root_module.addImport("chrdev_notify_abi", chrdev_notify_abi);

    const unit_tests = b.addTest(.{
        .root_module = root_module,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);

    const named_step = b.step(
        "phase3-abi-chrdev-notify-alias-contract",
        "Run the Phase 3 ABI chrdev notify alias contract",
    );
    named_step.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run the Phase 3 ABI chrdev notify alias contract");
    test_step.dependOn(&run_unit_tests.step);
}
