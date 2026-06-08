const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const unit_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("check_zig_toolchain_archive_duplicate_suffix_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(unit_tests);

    const contract_step = b.step(
        "check-zig-toolchain-archive-duplicate-suffix-contract",
        "Run the check-zig-toolchain archive duplicate suffix source contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run archive duplicate suffix contract tests");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
