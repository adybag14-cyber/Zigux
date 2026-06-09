const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("check_zig_toolchain_archive_target_scope_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_contract = b.addRunArtifact(tests);

    const contract_step = b.step(
        "check-zig-toolchain-archive-target-scope-contract",
        "Run the Zig toolchain archive target scope contract",
    );
    contract_step.dependOn(&run_contract.step);

    const test_step = b.step("test", "Run tests");
    test_step.dependOn(&run_contract.step);

    b.default_step.dependOn(&run_contract.step);
}
