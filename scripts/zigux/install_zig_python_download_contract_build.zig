const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const test_step = b.step("test", "Run the install-zig Python download contract");
    const contract_step = b.step("install-zig-python-download-contract", "Run the install-zig Python download contract");

    const contract_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("install_zig_python_download_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    contract_step.dependOn(&run_contract_tests.step);
    test_step.dependOn(&run_contract_tests.step);
}
