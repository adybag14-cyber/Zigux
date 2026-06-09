const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("check_zig_toolchain_version_probe_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_contract = b.addRunArtifact(contract);
    run_contract.setCwd(b.path("../.."));

    const contract_step = b.step(
        "check-zig-toolchain-version-probe-contract",
        "Run the Lane 03 check-zig-toolchain version probe contract.",
    );
    contract_step.dependOn(&run_contract.step);

    const test_step = b.step(
        "test",
        "Run the Lane 03 check-zig-toolchain version probe contract tests.",
    );
    test_step.dependOn(&run_contract.step);

    b.default_step.dependOn(&run_contract.step);
}
