const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_module = b.createModule(.{
        .root_source_file = b.path("check_zig_toolchain_archive_search_roots_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .name = "check-zig-toolchain-archive-search-roots-contract-tests",
        .root_module = contract_module,
    });
    const run_contract = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "check-zig-toolchain-archive-search-roots-contract",
        "Run the Lane 18 check-zig-toolchain archive search roots contract.",
    );
    contract_step.dependOn(&run_contract.step);

    const test_step = b.step("test", "Run the Lane 18 check-zig-toolchain archive search roots contract tests.");
    test_step.dependOn(&run_contract.step);
    b.default_step.dependOn(test_step);
}
