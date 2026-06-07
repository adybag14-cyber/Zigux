const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const unit_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("install_zig_action_path_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);

    const contract_step = b.step(
        "install-zig-action-path-contract",
        "Validate install-zig action-path source contracts",
    );
    contract_step.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run install-zig action-path contract tests");
    test_step.dependOn(&run_unit_tests.step);
    b.default_step.dependOn(&run_unit_tests.step);
}
