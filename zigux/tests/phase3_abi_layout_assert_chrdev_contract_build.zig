const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings_path = b.option(
        []const u8,
        "abi-bindings-path",
        "Path to the ABI binding module under test",
    ) orelse "../bindings/abi.zig";
    const layout_assert_path = b.option(
        []const u8,
        "layout-assert-path",
        "Path to the layout assertion helper module under test",
    ) orelse "../helpers/layout_assert.zig";

    const abi_bindings_module = b.createModule(.{
        .root_source_file = b.path(abi_bindings_path),
        .target = target,
        .optimize = optimize,
    });
    const layout_assert_module = b.createModule(.{
        .root_source_file = b.path(layout_assert_path),
        .target = target,
        .optimize = optimize,
    });
    layout_assert_module.addImport("abi_bindings", abi_bindings_module);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_layout_assert_chrdev_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("abi_bindings", abi_bindings_module);
    root_module.addImport("layout_assert_helpers", layout_assert_module);

    const tests = b.addTest(.{
        .name = "phase3-abi-layout-assert-chrdev-contract",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const contract_step = b.step(
        "phase3-abi-layout-assert-chrdev-contract",
        "Run the Phase 3 ABI layout-assert chrdev contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 3 ABI layout-assert chrdev contract");
    test_step.dependOn(&run_tests.step);
}
