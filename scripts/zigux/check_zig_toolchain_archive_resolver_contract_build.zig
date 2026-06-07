const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const contract_path = b.path("check_zig_toolchain_archive_resolver_contract.zig");

    const contract = b.addExecutable(.{
        .name = "check-zig-toolchain-archive-resolver-contract",
        .root_module = b.createModule(.{
            .root_source_file = contract_path,
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_contract = b.addRunArtifact(contract);
    if (b.args) |args| {
        run_contract.addArgs(args);
    }

    const contract_step = b.step(
        "check-zig-toolchain-archive-resolver-contract",
        "Run the Lane 18 check-zig-toolchain archive resolver contract.",
    );
    contract_step.dependOn(&run_contract.step);

    const unit_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = contract_path,
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);

    const test_step = b.step(
        "test",
        "Run the Lane 18 check-zig-toolchain archive resolver contract tests.",
    );
    test_step.dependOn(&run_unit_tests.step);
    b.default_step.dependOn(&run_contract.step);
}
