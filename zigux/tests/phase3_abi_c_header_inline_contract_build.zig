const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const abi_header_path = b.option(
        []const u8,
        "abi-header-path",
        "Path to the C ABI header inspected by the contract",
    ) orelse "include/zigux/abi.h";

    const options = b.addOptions();
    options.addOption([]const u8, "abi_header_path", abi_header_path);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_c_header_inline_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("build_options", options);

    const unit_tests = b.addTest(.{
        .root_module = root_module,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);

    const named_step = b.step(
        "phase3-abi-c-header-inline-contract",
        "Run the Phase 3 ABI C header inline helper contract",
    );
    named_step.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run the Phase 3 ABI C header inline helper contract");
    test_step.dependOn(&run_unit_tests.step);
}
