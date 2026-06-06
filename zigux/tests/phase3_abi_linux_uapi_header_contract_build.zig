const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const linux_header_path = b.option(
        []const u8,
        "linux-header-path",
        "Path to the Linux-facing Zigux UAPI header inspected by the contract",
    ) orelse "include/linux/zigux.h";

    const options = b.addOptions();
    options.addOption([]const u8, "linux_header_path", linux_header_path);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_linux_uapi_header_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("build_options", options);

    const unit_tests = b.addTest(.{
        .root_module = root_module,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);

    const named_step = b.step(
        "phase3-abi-linux-uapi-header-contract",
        "Run the Phase 3 ABI Linux UAPI header facade contract",
    );
    named_step.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run the Phase 3 ABI Linux UAPI header facade contract");
    test_step.dependOn(&run_unit_tests.step);
}
