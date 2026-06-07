const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .name = "validate-bootstrap-toolchain-roster-contract",
        .root_module = b.createModule(.{
            .root_source_file = b.path("validate_bootstrap_toolchain_roster_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);
    const contract_step = b.step(
        "validate-bootstrap-toolchain-roster-contract",
        "Run the Lane 03 validate-bootstrap toolchain roster contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 03 validate-bootstrap toolchain roster contract");
    test_step.dependOn(&run_tests.step);
    b.default_step.dependOn(&run_tests.step);
}
